from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

# SignUp Form
class JadwaUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'})
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'}),
            "password1": forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'}),
            "password2": forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm Password'}),
        }

# Login Form
class JadwaAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'}))