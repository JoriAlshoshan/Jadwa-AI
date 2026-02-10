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
            'project_location_other': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'مثال: منطقة القصيم, عنيزة'}),
            'project_location_type': forms.Select(attrs={'class': 'form-select'}),
            'project_budget': forms.NumberInput(attrs={'class': 'form-input'}),
            'project_duration': forms.NumberInput(attrs={'class': 'form-input'}),
            'number_of_employees': forms.NumberInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Describe competitors and target audience (optional)'}),
        }

        labels = {
            'project_name': 'project name:',
            'Project_type': 'Project type:',
            'project_region': 'region:',
            'project_city': 'city:',
            'project_location_other': 'specify location:',
            'project_location_type': 'project location type:',
            'project_budget': 'project budget:',
            'project_duration': 'project duration:',
            'number_of_employees': 'number of employees:',
            'description': 'Description (Optional):',
        }

        error_messages = {
            "project_name": {"required": "This field is required."},
            "Project_type": {"required": "This field is required."},
            "project_region": {"required": "This field is required."},
            "project_city": {
                "required": "This field is required.",
                "invalid_choice": "Please select a city from the list.",
            },
            "project_location_other": {"required": "Please specify the location."},
            "project_location_type": {"required": "This field is required."},
            "project_budget": {"required": "This field is required."},
            "project_duration": {"required": "This field is required."},
            "number_of_employees": {"required": "This field is required."},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        city_label_map = dict(self.fields['project_city'].choices)

        region_value = None
        if self.data.get("project_region"):
            region_value = self.data.get("project_region")
        elif self.instance and getattr(self.instance, "pk", None):
            region_value = self.instance.project_region

        if region_value:
            allowed = REGION_TO_CITIES.get(region_value, [])
            if "other" not in allowed:
                allowed.append("other")

            self.fields['project_city'].choices = [("", "---------")] + [
                (c, city_label_map.get(c, c)) for c in allowed if c
            ]
        else:
            self.fields['project_city'].choices = [("", "---------"), ("other", city_label_map.get("other", "أخرى"))]

    def clean(self):
        cleaned = super().clean()

        region = cleaned.get('project_region')
        city = cleaned.get('project_city')
        other = (cleaned.get('project_location_other') or '').strip()

        if (region == "other" or city == "other"):
            if not other:
                self.add_error('project_location_other', 'Please specify the location.')
            else:
                low = other.lower().strip()
                if low in {"qassim", "riyadh", "makkah", "madinah", "eastern", "asir", "tabuk", "jazan", "hail", "jouf", "najran", "bahah", "northern"}:
                    pass
                else:
                    if not ("," in other or "،" in other) and "منطقة" not in other:
                        self.add_error('project_location_other', 'Write it in Arabic like: منطقة القصيم, عنيزة')

        if not (region == "other" or city == "other"):
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
