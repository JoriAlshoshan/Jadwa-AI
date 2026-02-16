from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _
from .models import Projects

User = get_user_model()


# =========================================
# Edit Profile Form (Dropdown Region/City)
# =========================================

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

REGION_CHOICES = [("", _("Select region"))] + [
    (k, k.replace("_", " ").title()) for k in REGION_TO_CITIES.keys()
]


class EditProfileForm(forms.ModelForm):
    # dropdowns
    region = forms.ChoiceField(
        choices=REGION_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-input", "id": "id_region"})
    )

    city = forms.ChoiceField(
        choices=[("", _("Select city")), ("other", _("Other"))],  # other always exists
        required=False,
        widget=forms.Select(attrs={"class": "form-input", "id": "id_city"})
    )

    # custom text when other
    region_custom = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": _("Type your region")
        })
    )

    city_custom = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": _("Type your city")
        })
    )

    class Meta:
        model = User
        # ✅ لازم region_custom/city_custom موجودة في User model
        fields = [
            "first_name", "last_name", "profile_image", "bio",
            "region", "city", "linkedin",
            "region_custom", "city_custom"
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-input"}),
            "last_name": forms.TextInput(attrs={"class": "form-input"}),
            "bio": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": _("Short bio (optional)")
            }),
            "linkedin": forms.URLInput(attrs={
                "class": "form-input",
                "placeholder": "https://linkedin.com/in/..."
            }),
            "profile_image": forms.ClearableFileInput(attrs={
                "id": "id_profile_image",
                "accept": "image/*"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 1) determine selected region:
        #    - if POST -> use POST
        #    - else -> use instance.region (only if it's one of the keys)
        posted_region = (self.data.get("region") or "").strip()
        inst_region = (getattr(self.instance, "region", "") or "").strip()

        if posted_region:
            region_val = posted_region
        else:
            region_val = inst_region if inst_region in REGION_TO_CITIES else ""

        # 2) rebuild city choices based on region
        cities = REGION_TO_CITIES.get(region_val, [])
        base = [("", _("Select city"))]
        base += [(c, c.replace("_", " ").title()) for c in cities if c != "other"]
        base += [("other", _("Other"))]
        self.fields["city"].choices = base

        # 3) preserve values when saved as OTHER:
        # if instance stored region == "other", show custom text
        if self.instance and self.instance.pk:
            if (getattr(self.instance, "region", "") == "other"):
                self.initial["region_custom"] = (getattr(self.instance, "region_custom", "") or "")
                # keep dropdown value as "other"
                self.initial["region"] = "other"

            if (getattr(self.instance, "city", "") == "other"):
                self.initial["city_custom"] = (getattr(self.instance, "city_custom", "") or "")
                self.initial["city"] = "other"

            # ✅ لو المنطقة/المدينة مخزنة كنص مخصص (مو من القائمة)
            # نخلي الدروب داون على other ونعبي النص
            if inst_region and inst_region not in REGION_TO_CITIES and inst_region != "other":
                self.initial["region"] = "other"
                self.initial["region_custom"] = inst_region

            inst_city = (getattr(self.instance, "city", "") or "").strip()
            # إذا المدينة نص مخصص
            all_known_cities = set()
            for arr in REGION_TO_CITIES.values():
                all_known_cities.update(arr)
            if inst_city and inst_city not in all_known_cities and inst_city != "other":
                self.initial["city"] = "other"
                self.initial["city_custom"] = inst_city

    def clean(self):
        cleaned = super().clean()

        region = (cleaned.get("region") or "").strip()
        city = (cleaned.get("city") or "").strip()
        region_custom = (cleaned.get("region_custom") or "").strip()
        city_custom = (cleaned.get("city_custom") or "").strip()

        # ✅ Validation
        if region == "other":
            if not region_custom:
                self.add_error("region_custom", _("Please type your region."))
            if city != "other":
                self.add_error("city", _("Please choose Other, then type your city."))
            if not city_custom:
                self.add_error("city_custom", _("Please type your city."))

        if region and region != "other" and city == "other":
            if not city_custom:
                self.add_error("city_custom", _("Please type your city."))

        # ✅ Store: keep dropdown as "other" and save actual text in custom fields
        if region == "other":
            cleaned["region"] = "other"
            cleaned["region_custom"] = region_custom
        else:
            cleaned["region_custom"] = ""

        if city == "other":
            cleaned["city"] = "other"
            cleaned["city_custom"] = city_custom
        else:
            cleaned["city_custom"] = ""

        # ✅ If no region selected => clear city + city_custom
        if not region:
            cleaned["city"] = ""
            cleaned["city_custom"] = ""

        return cleaned


# =========================================
# Auth Forms
# =========================================

class JadwaUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=forms.EmailInput(attrs={
            "placeholder": _("Email"),
            "class": "form-input",
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")
        labels = {"username": _("Username")}
        widgets = {
            "username": forms.TextInput(attrs={
                "placeholder": _("Username"),
                "class": "form-input",
            }),
        }


class JadwaAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": _("Username"), "class": "form-input"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": _("Password"), "class": "form-input"})
    )


# =========================================
# Project Form
# =========================================

class ProjectInformationForm(forms.ModelForm):
    class Meta:
        model = Projects
        fields = [
            "project_name",
            "Project_type",
            "project_region",
            "project_city",
            "project_location_other",
            "project_location_type",
            "project_budget",
            "project_duration",
            "number_of_employees",
            "description",
        ]

        widgets = {
            "project_name": forms.TextInput(attrs={"class": "form-input"}),
            "Project_type": forms.Select(attrs={"class": "form-select"}),
            "project_region": forms.Select(attrs={"class": "form-select"}),
            "project_city": forms.Select(attrs={"class": "form-select"}),
            "project_location_other": forms.TextInput(
                attrs={"class": "form-input", "placeholder": _("Example: Qassim Region, Unaizah")}
            ),
            "project_location_type": forms.Select(attrs={"class": "form-select"}),
            "project_budget": forms.NumberInput(attrs={"class": "form-input"}),
            "project_duration": forms.NumberInput(attrs={"class": "form-input"}),
            "number_of_employees": forms.NumberInput(attrs={"class": "form-input"}),
            "description": forms.Textarea(attrs={
                "class": "form-input",
                "rows": 4,
                "placeholder": _("Describe competitors and target audience (optional)"),
            }),
        }

        labels = {
            "project_name": _("Project Name"),
            "Project_type": _("Project Type"),
            "project_region": _("Region"),
            "project_city": _("City"),
            "project_location_other": _("Specify Location"),
            "project_location_type": _("Project Location Type"),
            "project_budget": _("Project Budget"),
            "project_duration": _("Project Duration"),
            "number_of_employees": _("Number Of Employees"),
            "description": _("Description (Optional)"),
        }

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

    def clean(self):
        cleaned = super().clean()

        region = cleaned.get("project_region")
        city = cleaned.get("project_city")
        other = (cleaned.get("project_location_other") or "").strip()

        if (region == "other" or city == "other"):
            if not other:
                self.add_error("project_location_other", _("Please specify the location."))
            else:
                low = other.lower().strip()
                if low in {"qassim", "riyadh", "makkah", "madinah", "eastern", "asir", "tabuk", "jazan", "hail", "jouf", "najran", "bahah", "northern"}:
                    pass
                else:
                    if not ("," in other or "،" in other) and "منطقة" not in other:
                        self.add_error("project_location_other", _("Write it like: Qassim Region, Unaizah"))

        if not (region == "other" or city == "other"):
            cleaned["project_location_other"] = ""

        return cleaned


# =========================================
# Reset Password Forms
# =========================================

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={"class": "form-input"})
    )


class OTPForm(forms.Form):
    otp = forms.CharField(
        label=_("OTP Code"),
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "123456"})
    )


class ResetPasswordForm(SetPasswordForm):
    pass
