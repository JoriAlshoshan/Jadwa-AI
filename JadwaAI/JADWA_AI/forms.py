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


# =========================================
# ✅ فلترة المدن حسب المنطقة (قيم لازم تطابق CITY_CHOICES)
# ملاحظة: ما يحتاج نحط "other" هنا لأننا بنضيفه تلقائيًا تحت
# =========================================
REGION_TO_CITIES = {
    "riyadh":   ["riyadh_city", "diriyah", "kharj"],
    "qassim":   ["buraidah", "unaizah", "ras"],
    "eastern":  ["dammam", "khobar", "dhahran", "jubail"],
    "makkah":   ["jeddah", "taif"],
    "madinah":  ["madinah_city"],
    "asir":     ["abha", "khamees"],
    "tabuk":    ["tabuk_city"],
    "jazan":    ["jazan_city"],
    "hail":     ["hail_city"],
    "jouf":     ["sakaka"],
    "northern": ["arar"],
    "najran":   ["najran_city"],
    "bahah":    ["bahah_city"],
    "other":    ["other"],
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
        ]

        widgets = {
            'project_name': forms.TextInput(attrs={'class': 'form-input'}),
            'Project_type': forms.Select(attrs={'class': 'form-select'}),

            'project_region': forms.Select(attrs={'class': 'form-select'}),
            'project_city': forms.Select(attrs={'class': 'form-select'}),

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

            'project_region': 'region:',
            'project_city': 'city:',
            'project_location_other': 'specify location:',

            'project_location_type': 'project location type:',
            'project_budget': 'project budget:',
            'project_duration': 'project duration:',
            'number_of_employees': 'number of employees:',
        }

        # ✅ رسائل أخطاء نظيفة
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
            "project_budget": {"required": "This field is required.", "invalid": "Please enter a valid budget."},
            "project_duration": {"required": "This field is required.", "invalid": "Please enter a valid duration."},
            "number_of_employees": {"required": "This field is required.", "invalid": "Please enter a valid number."},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Map للقيم -> الليبل (أسماء المدن بالعربي)
        city_label_map = dict(self.fields['project_city'].choices)

        # نحدد المنطقة من POST أو instance
        region_value = None
        if self.data.get("project_region"):
            region_value = self.data.get("project_region")
        elif self.instance and getattr(self.instance, "pk", None):
            region_value = self.instance.project_region

        if region_value:
            allowed = REGION_TO_CITIES.get(region_value, [])

            # ✅ أهم سطر: نضمن وجود other دايمًا
            if "other" not in allowed:
                allowed = allowed + ["other"]

            self.fields['project_city'].choices = [(c, city_label_map.get(c, c)) for c in allowed]
        else:
            # قبل اختيار المنطقة: خليها other فقط
            self.fields['project_city'].choices = [("other", city_label_map.get("other", "أخرى"))]

    def clean(self):
        cleaned = super().clean()

        region = cleaned.get('project_region')
        city = cleaned.get('project_city')
        other = (cleaned.get('project_location_other') or '').strip()

        # إذا اختار other لازم يكتب
        if (region == "other" or city == "other") and not other:
            self.add_error('project_location_other', 'Please specify the location.')

        # إذا مو other امسح النص
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
