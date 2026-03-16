from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _
from .models import Projects
from django.utils import translation
User = get_user_model()

from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active)
        )

account_activation_token = AccountActivationTokenGenerator()

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _
from django.utils import translation
from .models import Projects

User = get_user_model()


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

REGION_LABELS_AR = {
    "riyadh": "منطقة الرياض",
    "qassim": "منطقة القصيم",
    "eastern": "المنطقة الشرقية",
    "makkah": "منطقة مكة المكرمة",
    "madinah": "منطقة المدينة المنورة",
    "asir": "منطقة عسير",
    "tabuk": "منطقة تبوك",
    "jazan": "منطقة جازان",
    "hail": "منطقة حائل",
    "jouf": "منطقة الجوف",
    "northern": "منطقة الحدود الشمالية",
    "najran": "منطقة نجران",
    "bahah": "منطقة الباحة",
    "other": "أخرى",
}

REGION_LABELS_EN = {
    "riyadh": "Riyadh Region",
    "qassim": "Qassim Region",
    "eastern": "Eastern Region",
    "makkah": "Makkah Region",
    "madinah": "Madinah Region",
    "asir": "Asir Region",
    "tabuk": "Tabuk Region",
    "jazan": "Jazan Region",
    "hail": "Hail Region",
    "jouf": "Al Jouf Region",
    "northern": "Northern Borders",
    "najran": "Najran Region",
    "bahah": "Al Bahah Region",
    "other": "Other",
}

CITY_LABELS_AR = {
    "riyadh": "الرياض",
    "diriyah": "الدرعية",
    "kharj": "الخرج",
    "buraidah": "بريدة",
    "unaizah": "عنيزة",
    "ras": "الرس",
    "dammam": "الدمام",
    "khobar": "الخبر",
    "dhahran": "الظهران",
    "jubail": "الجبيل",
    "jeddah": "جدة",
    "taif": "الطائف",
    "madinah": "المدينة المنورة",
    "abha": "أبها",
    "khamees": "خميس مشيط",
    "tabuk": "تبوك",
    "jazan": "جازان",
    "hail": "حائل",
    "sakaka": "سكاكا",
    "arar": "عرعر",
    "najran": "نجران",
    "bahah": "الباحة",
    "other": "أخرى",
}

CITY_LABELS_EN = {
    "riyadh": "Riyadh",
    "diriyah": "Diriyah",
    "kharj": "Al Kharj",
    "buraidah": "Buraidah",
    "unaizah": "Unaizah",
    "ras": "Ar Rass",
    "dammam": "Dammam",
    "khobar": "Khobar",
    "dhahran": "Dhahran",
    "jubail": "Jubail",
    "jeddah": "Jeddah",
    "taif": "Taif",
    "madinah": "Madinah",
    "abha": "Abha",
    "khamees": "Khamis Mushait",
    "tabuk": "Tabuk",
    "jazan": "Jazan",
    "hail": "Hail",
    "sakaka": "Sakaka",
    "arar": "Arar",
    "najran": "Najran",
    "bahah": "Al Bahah",
    "other": "Other",
}


class EditProfileForm(forms.ModelForm):
    region = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select(attrs={"class": "form-input", "id": "id_region"})
    )

    city = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select(attrs={"class": "form-input", "id": "id_city"})
    )

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

        lang = translation.get_language() or "en"
        is_ar = str(lang).startswith("ar")

        region_labels = REGION_LABELS_AR if is_ar else REGION_LABELS_EN
        city_labels = CITY_LABELS_AR if is_ar else CITY_LABELS_EN

        self.fields["region"].choices = [("", _("Select region"))] + [
            (key, region_labels.get(key, key))
            for key in REGION_TO_CITIES.keys()
        ]

        posted_region = (self.data.get("region") or "").strip()
        inst_region = (getattr(self.instance, "region", "") or "").strip()

        if posted_region:
            region_val = posted_region
        else:
            region_val = inst_region if inst_region in REGION_TO_CITIES else ""

        cities = REGION_TO_CITIES.get(region_val, [])
        self.fields["city"].choices = [("", _("Select city"))] + [
            (key, city_labels.get(key, key))
            for key in cities
        ]

        if self.instance and self.instance.pk:
            if getattr(self.instance, "region", "") == "other":
                self.initial["region"] = "other"
                self.initial["region_custom"] = getattr(self.instance, "region_custom", "") or ""

            if getattr(self.instance, "city", "") == "other":
                self.initial["city"] = "other"
                self.initial["city_custom"] = getattr(self.instance, "city_custom", "") or ""

            if inst_region and inst_region not in REGION_TO_CITIES and inst_region != "other":
                self.initial["region"] = "other"
                self.initial["region_custom"] = inst_region

            inst_city = (getattr(self.instance, "city", "") or "").strip()
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

        if region == "other":
            if not region_custom:
                self.add_error("region_custom", _("Please type your region."))
            if city != "other":
                self.add_error("city", _("Please choose Other, then type your city."))
            if not city_custom:
                self.add_error("city_custom", _("Please type your city."))

        if region and region != "other" and city == "other" and not city_custom:
            self.add_error("city_custom", _("Please type your city."))

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

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("This email is already registered."))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False  
        if commit:
            user.save()
        return user


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

        region = (cleaned.get("project_region") or "").strip().lower()
        city = (cleaned.get("project_city") or "").strip().lower()
        other = (cleaned.get("project_location_other") or "").strip()

        is_other = (region == "other" or city == "other")

        # ✅ لو مو other: فضّي الحقل وخلاص
        if not is_other:
            cleaned["project_location_other"] = ""
            return cleaned

        # ✅ لو other: لازم Specify Location
        if not other:
            self.add_error("project_location_other", _("Please specify the location."))
            return cleaned

        # ✅ parsing: "qassim, unaizah" أو "Qassim Region, Unaizah"
        txt = other.replace("،", ",").strip()
        parts = [p.strip() for p in txt.split(",") if p.strip()]
        
        AR_REGION_MAP = {
        "القصيم": "qassim",
        "منطقة القصيم": "qassim",

        "الرياض": "riyadh",
        "منطقة الرياض": "riyadh",

        "الشرقية": "eastern",
        "المنطقة الشرقية": "eastern",

        "مكة": "makkah",
        "منطقة مكة": "makkah",
        "مكة المكرمة": "makkah",

        "المدينة": "madinah",
        "المدينة المنورة": "madinah",
        "منطقة المدينة": "madinah",

        "عسير": "asir",
        "تبوك": "tabuk",
        "جازان": "jazan",
        "حائل": "hail",
        "الجوف": "jouf",
        "نجران": "najran",
        "الباحة": "bahah",
        "الحدود الشمالية": "northern",
        }

        AR_CITY_MAP = {
            "عنيزة": "unaizah",
            "بريدة": "buraidah",
            "الرس": "ras",
            "الدمام": "dammam",
            "الخبر": "khobar",
            "الظهران": "dhahran",
            "الجبيل": "jubail",
            "جدة": "jeddah",
            "الطائف": "taif",
            "أبها": "abha",
            "خميس مشيط": "khamees",
            "سكاكا": "sakaka",
            "عرعر": "arar",
        }

        def norm(s: str) -> str:
            s = (s or "").strip()
            s = s.replace("،", ",")
            # شيل Region / منطقة
            s_low = s.lower().replace(" region", "").strip()
            s_ar = s.replace("منطقة", "").strip()  # يبقى ممكن "القصيم"
            s_ar = s_ar.strip()

            # ✅ إذا عربي معروف حوّله
            if s in AR_REGION_MAP: 
                return AR_REGION_MAP[s]
            if s_ar in AR_REGION_MAP:
                return AR_REGION_MAP[s_ar]

            if s in AR_CITY_MAP:
                return AR_CITY_MAP[s]
            if s_ar in AR_CITY_MAP:
                return AR_CITY_MAP[s_ar]

            # ✅ وإلا خله إنجليزي normalized
            return s_low
            

        

        part1 = norm(parts[0]) if len(parts) >= 1 else norm(txt)
        part2 = norm(parts[1]) if len(parts) >= 2 else ""

        # ✅ 1) region مباشر
        region_key = part1 if (part1 in REGION_TO_CITIES and part1 != "other") else None

        # ✅ 2) city داخل كل المناطق
        city_key = None

        if part2:
            for r, cities in REGION_TO_CITIES.items():
                if part2 in cities and part2 != "other":
                    region_key = r
                    city_key = part2
                    break
        else:
            for r, cities in REGION_TO_CITIES.items():
                if part1 in cities and part1 != "other":
                    region_key = r
                    city_key = part1
                    break

        # ✅ إذا لقينا مكان صحيح نحوله
        if region_key:
            cleaned["project_region"] = region_key
            cleaned["project_city"] = city_key or next((c for c in REGION_TO_CITIES.get(region_key, []) if c != "other"), "other")
        else:
            self.add_error("project_location_other", _("Write it like: qassim, unaizah"))

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

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'bio', 'region', 'city', 'linkedin', 'is_active', 'is_staff', 'is_superuser']
        labels = {
            "username": _("Username"),
            "email": _("Email"),
            "is_active": _("Account active"),
            "is_staff": _("Admin access"),
            "is_superuser": _("Full admin access"),
        }
        widgets = {
            'username': forms.TextInput(attrs={'readonly' : 'readonly'}),
            'email': forms.TextInput(attrs={'readonly' : 'readonly'}),
            'bio': forms.TextInput(attrs={'readonly' : 'readonly'}),
            'region': forms.TextInput(attrs={'readonly' : 'readonly'}),
            'city': forms.TextInput(attrs={'readonly' : 'readonly'}),
            'linkedin': forms.TextInput(attrs={'readonly' : 'readonly'}),
        }
