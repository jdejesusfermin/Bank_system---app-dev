from django import forms
from .models import Account, User
from django.contrib.auth.hashers import make_password, check_password

class CustomUserCreationForm(forms.ModelForm):  # Updated to handle registration with PIN
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}),
        label="Password",
        required=True
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your password'}),
        label="Confirm Password",
        required=True
    )
    pin = forms.CharField(
        max_length=6,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter a 6-digit PIN'}),
        label="PIN",
        required=True
    )

    class Meta:
        model = User  # Use your custom User model or Django's built-in User model
        fields = ['username', 'email', 'password1', 'password2', 'pin']

    def clean_pin(self):
        pin = self.cleaned_data['pin']
        # Validate PIN to ensure it's a 6-digit number
        if not pin.isdigit() or len(pin) != 6:
            raise forms.ValidationError('PIN must be a 6-digit number.')
        return pin

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match!")
        return password2

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        pin = self.cleaned_data['pin']
        user.password = make_password(self.cleaned_data['password1'])  # Hash the password
        if commit:
            user.save()
            # Create the Account associated with the user and hash the PIN
            Account.objects.create(user=user, balance=0.00, pin=make_password(pin))
        return user

class PINForm(forms.ModelForm):
    class Meta:
        model = Account  # Ensure your Account model includes a 'pin' field
        fields = ['pin']
        widgets = {
            'pin': forms.PasswordInput(attrs={'placeholder': 'Enter 6-digit PIN', 'class': 'form-control'})
        }

    def clean_pin(self):
        pin = self.cleaned_data['pin']
        # Validate PIN: it must be numeric and exactly 6 digits long
        if not pin.isdigit() or len(pin) != 6:
            raise forms.ValidationError('PIN must be a 6-digit number.')
        return pin

    def save(self, commit=True):
        account = super(PINForm, self).save(commit=False)
        # Hash the PIN for security before saving it
        account.pin = make_password(self.cleaned_data['pin'])
        if commit:
            account.save()
        return account