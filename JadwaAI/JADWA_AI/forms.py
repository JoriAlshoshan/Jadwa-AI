from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .models import Projects

User = get_user_model()


class JadwaUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=_("Email"),          # ✅ هذا اللي يترجم كلمة Email
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': _("Email"),
            'class': 'form-input'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")
        labels = {            
            "username": _("Username"),
        }
        widgets = {
            "username": forms.TextInput(attrs={
                'placeholder': _("Username"),
                'class': 'form-input'
            }),
        }



class JadwaAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _("Username"), 'class': 'form-input'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': _("Password"), 'class': 'form-input'})
    )


REGION_TO_CITIES = {
    "riyadh": ["riyadh", "diriyah", "kharj", "other"],
    "qassim": ["buraidah", "unaizah", "ras", "other"],
    "eastern": ["dammam", "khobar", "dhahran", "jubail", "other"],
    "makkah": ["jeddah", "taif", "other"],
    "madinah": ["madinah", "other"],
    "asir": ["abha", "khamees", "other"],
    "tabuk": ["tabuk", "other"],
    "jazan": ["jazan", "other"],
    "hail": ["hail", "other"],
    "jouf": ["sakaka", "other"],
    "northern": ["arar", "other"],
    "najran": ["najran", "other"],
    "bahah": ["bahah", "other"],
    "other": ["other"],
}


class ProjectInformationForm(forms.ModelForm):
    class Meta:
        model = Projects
        fields = [
            'project_name',
            'Project_type',
            'project_region',
            'project_city',
            'project_location_other',
            'project_location_type',
            'project_budget',
            'project_duration',
            'number_of_employees',
            'description',
        ]

        widgets = {
            'project_name': forms.TextInput(attrs={'class': 'form-input'}),
            'Project_type': forms.Select(attrs={'class': 'form-select'}),
            'project_region': forms.Select(attrs={'class': 'form-select'}),
            'project_city': forms.Select(attrs={'class': 'form-select'}),
            'project_location_other': forms.TextInput(
                attrs={'class': 'form-input', 'placeholder': _("Example: Qassim Region, Unaizah")}
            ),
            'project_location_type': forms.Select(attrs={'class': 'form-select'}),
            'project_budget': forms.NumberInput(attrs={'class': 'form-input'}),
            'project_duration': forms.NumberInput(attrs={'class': 'form-input'}),
            'number_of_employees': forms.NumberInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-input',
                    'rows': 4,
                    'placeholder': _("Describe competitors and target audience (optional)"),
                }
            ),
        }
        labels = {
            'project_name': _("Project Name"),
            'Project_type': _("Project Type"),
            'project_region': _("Region"),
            'project_city': _("City"),
            'project_location_other': _("Specify Location"),
            'project_location_type': _("Project Location Type"),
            'project_budget': _("Project Budget"),
            'project_duration': _("Project Duration"),
            'number_of_employees': _("Number Of Employees"),
            'description': _("Description (Optional)"),
        }


        # ✅ رسائل الأخطاء مترجمة
        error_messages = {
            "project_name": {"required": _("This field is required.")},
            "Project_type": {"required": _("This field is required.")},
            "project_region": {"required": _("This field is required.")},
            "project_city": {
                "required": _("This field is required."),
                "invalid_choice": _("Please select a city from the list."),
            },
            "project_location_other": {"required": _("Please specify the location.")},
            "project_location_type": {"required": _("This field is required.")},
            "project_budget": {"required": _("This field is required.")},
            "project_duration": {"required": _("This field is required.")},
            "number_of_employees": {"required": _("This field is required.")},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def clean(self):
        cleaned = super().clean()

        region = cleaned.get('project_region')
        city = cleaned.get('project_city')
        other = (cleaned.get('project_location_other') or '').strip()

        if (region == "other" or city == "other"):
            if not other:
                self.add_error('project_location_other', _("Please specify the location."))
            else:
                low = other.lower().strip()
                if low in {"qassim", "riyadh", "makkah", "madinah", "eastern", "asir", "tabuk", "jazan", "hail", "jouf", "najran", "bahah", "northern"}:
                    pass
                else:
                    if not ("," in other or "،" in other) and "منطقة" not in other:
                        self.add_error('project_location_other', _("Write it like: Qassim Region, Unaizah"))

        if not (region == "other" or city == "other"):
            cleaned['project_location_other'] = ""

        return cleaned


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )


class OTPForm(forms.Form):
    otp = forms.CharField(
        label=_("OTP Code"),
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '123456'})
    )


class ResetPasswordForm(SetPasswordForm):
    pass
