from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Homepage URL
    path('register/', views.register, name='register'),  # URL for user registration
    path('create/', views.create_transaction, name='create_transaction'),  # URL for creating a transaction
    path('set_pin/', views.set_pin, name='set_pin'),  # URL for setting a PIN
    path('verify_pin/', views.verify_pin, name='verify_pin'),  # URL for verifying a PIN
    path('accounts/login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),  # Updated login URL
    path('accounts/logout/', LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),  # Updated logout URL
    path('profile/', views.profile, name='profile'),  # Profile URL
    path('transaction/', views.create_transaction, name='create_transaction'),  # Transaction URL
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
]


