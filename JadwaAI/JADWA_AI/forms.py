from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from django.contrib.auth import get_user_model  

User = get_user_model()

class JadwaUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-input'})
    )
    
    class Meta(UserCreationForm.Meta): 
        model = User 
        fields = ("username", "email") 
        widgets = {
            "username": forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-input'}),
        }

class JadwaAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-input'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-input'})
    )

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-input'}))

class OTPForm(forms.Form):
        otp = forms.CharField(
        label="OTP Code", 
        max_length=6, 
        min_length=6, 
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '123456'})
    )

class ResetPasswordForm(SetPasswordForm):
    pass
