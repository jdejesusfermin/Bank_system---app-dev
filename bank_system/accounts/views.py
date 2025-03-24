from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .models import Account, Transaction  # Ensure the Account and Transaction models exist
from .forms import PINForm, CustomUserCreationForm  # Make sure these forms are defined
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from decimal import Decimal


# Home Page View
@login_required
def home(request):
    # Fetch the account associated with the logged-in user
    try:
        account = Account.objects.get(user=request.user)
        transactions = Transaction.objects.filter(account=account).order_by('-timestamp')  # Order by most recent
    except Account.DoesNotExist:
        account = None
        transactions = []

    return render(request, 'accounts/home.html', {
        'account': account,
        'transactions': transactions
    })


# User Registration View
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Save the user object without committing yet
            pin = form.cleaned_data['pin']  # Retrieve the PIN from the form
            user.password = make_password(form.cleaned_data['password1'])  # Hash the password
            user.save()  # Save the user to the database

            # Create an account associated with the user, including the PIN
            Account.objects.create(user=user, balance=0.00, pin=make_password(pin))  # Hash the PIN before saving
            return redirect('login')  # Redirect to login after successful registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


# Create Transaction View
@login_required
def create_transaction(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        transaction_type = request.POST.get('type')

        try:
            # Automatically fetch the account linked to the logged-in user
            account = Account.objects.get(user=request.user)

            # Convert amount to Decimal
            decimal_amount = Decimal(amount)

            # Process the transaction based on the type
            if transaction_type == 'Credit':
                account.balance += decimal_amount
            elif transaction_type == 'Debit':
                if account.balance >= decimal_amount:  # Ensure sufficient balance for debit
                    account.balance -= decimal_amount
                else:
                    return render(request, 'accounts/create_transaction.html', {
                        'error': 'Insufficient balance!'
                    })

            # Save the account updates
            account.save()

            # Save the transaction record
            Transaction.objects.create(
                account=account,
                amount=decimal_amount,
                transaction_type=transaction_type
            )

            # Redirect to the success page after a successful transaction
            return render(request, 'accounts/transaction_success.html')

        except Account.DoesNotExist:
            return render(request, 'accounts/create_transaction.html', {
                'error': 'No account associated with this user!'
            })
        except Exception:
            return render(request, 'accounts/create_transaction.html', {
                'error': 'Invalid amount entered!'
            })

    # Render the transaction form by default
    return render(request, 'accounts/create_transaction.html')


# Set PIN View
@login_required
def set_pin(request):
    # Access the logged-in user's account
    try:
        account = Account.objects.get(user=request.user)
    except Account.DoesNotExist:
        return redirect('home')  # Redirect if no account is found

    if request.method == 'POST':
        form = PINForm(request.POST, instance=account)
        if form.is_valid():
            form.save()  # Saves the hashed PIN securely to the database
            return redirect('home')  # Redirect to the homepage or success page
    else:
        form = PINForm(instance=account)  # Pre-fill the form with current data, if available
    return render(request, 'accounts/set_pin.html', {'form': form})


# Verify PIN View
@login_required
def verify_pin(request):
    if request.method == 'POST':
        pin = request.POST.get('pin')  # Retrieve the submitted PIN
        try:
            account = Account.objects.get(user=request.user)  # Find the associated account
            if make_password(pin) == account.pin:  # Validate the entered PIN
                return redirect('transaction_success')  # Redirect to a success page
            else:
                return render(request, 'accounts/verify_pin.html', {'error': 'Invalid PIN'})  # Show error message
        except Account.DoesNotExist:
            return render(request, 'accounts/verify_pin.html', {'error': 'Account not found!'})

    return render(request, 'accounts/verify_pin.html')  # Render the PIN verification page


# Profile Page View
@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {'user': request.user})  # Render the profile page
