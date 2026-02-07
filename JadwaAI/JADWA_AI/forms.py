from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from django.contrib.auth import get_user_model

from .models import Projects

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


class ProjectInformationForm(forms.ModelForm):
    """
    ✅ تعديل مهم:
    - project_location صار Dropdown (forms.Select) لأن في الموديل صار choices
    - أضفنا project_location_other للحل الهجين (Other)
    - تحقق clean() لمنع الأخطاء
    """

    class Meta:
        model = Projects
        fields = [
            'project_name',
            'Project_type',
            'project_location',
            'project_location_other',    
            'project_location_type',
            'project_budget',
            'project_duration',
            'number_of_employees',
        ]

        widgets = {
            'project_name': forms.TextInput(attrs={'class': 'form-input'}),

            'Project_type': forms.Select(attrs={'class': 'form-select'}),

            'project_location': forms.Select(attrs={'class': 'form-select'}),

            'project_location_other': forms.TextInput(
                attrs={'class': 'form-input', 'placeholder': 'Type the location...'}
            ),

            'project_location_type': forms.Select(attrs={'class': 'form-select'}),

            'project_budget': forms.NumberInput(attrs={'class': 'form-input'}),
            'project_duration': forms.NumberInput(attrs={'class': 'form-input'}),
            'number_of_employees': forms.NumberInput(attrs={'class': 'form-input'}),
        }

        labels = {
            'project_name': 'project name:',
            'Project_type': 'Project type:',
            'project_location': 'project location:',
            'project_location_other': 'specify location:',
            'project_location_type': 'project location type:',
            'project_budget': 'project budget:',
            'project_duration': 'project duration:',
            'number_of_employees': 'number of employees:',
        }

    def clean(self):
        cleaned = super().clean()
        loc = cleaned.get('project_location')
        other = (cleaned.get('project_location_other') or '').strip()

        if loc == "Other" and not other:
            self.add_error('project_location_other', 'Please specify the location.')

        if loc != "Other":
            cleaned['project_location_other'] = ""

        return cleaned


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )


class OTPForm(forms.Form):
    otp = forms.CharField(
        label="OTP Code",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '123456'})
    )


class ResetPasswordForm(SetPasswordForm):
    pass
