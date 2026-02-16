from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .fill_economic_indicator import calculate_update_economic_indicator
from .num_similar_enterprises import get_similar_enterprises


class User(AbstractUser):
    email = models.EmailField(unique=True)
    region_custom = models.CharField(max_length=80, blank=True, null=True)
    city_custom = models.CharField(max_length=80, blank=True, null=True)

    profile_image = models.ImageField(upload_to="profiles/", null=True, blank=True)
    bio = models.CharField(max_length=180, blank=True, null=True)
    region = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []


class Project(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project_name = models.CharField(max_length=200)
    budget = models.FloatField()
    duration = models.IntegerField()
    location = models.CharField(max_length=100)
    sector = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.project_name


class AnalysisResult(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    feasibility_score = models.FloatField()
    recommendation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for {self.project.project_name}"


class ContactMessage(models.Model):
    TOPIC_CHOICES = [
        ("demo", _("Request a demo")),
        ("support", _("Support")),
        ("partnership", _("Partnership")),
        ("other", _("Other")),
    ]

    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    topic = models.CharField(max_length=30, choices=TOPIC_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.topic}"


class Projects(models.Model):

    user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="jadwa_projects",
    null=True,
    blank=True
)

    project_name = models.CharField(max_length=80)

    PROJECT_TYPE_CHOICES = [
        ("Service", _("Service")),
        ("Product", _("Product")),
        ("Hybrid", _("Hybrid")),
    ]
    Project_type = models.CharField(max_length=50, choices=PROJECT_TYPE_CHOICES, db_column="Project_type")

    REGION_CHOICES = [
        ("", _("---------")),
        ("riyadh", _("Riyadh Region")),
        ("qassim", _("Qassim Region")),
        ("eastern", _("Eastern Region")),
        ("makkah", _("Makkah Region")),
        ("madinah", _("Madinah Region")),
        ("asir", _("Asir Region")),
        ("tabuk", _("Tabuk Region")),
        ("jazan", _("Jazan Region")),
        ("hail", _("Hail Region")),
        ("jouf", _("Al Jouf Region")),
        ("najran", _("Najran Region")),
        ("bahah", _("Al Bahah Region")),
        ("northern", _("Northern Borders")),
        ("other", _("Other")),
    ]

    CITY_CHOICES = [
        ("", _("---------")),
        ("riyadh", _("Riyadh")),
        ("diriyah", _("Diriyah")),
        ("kharj", _("Al Kharj")),
        ("buraidah", _("Buraidah")),
        ("unaizah", _("Unaizah")),
        ("ras", _("Ar Rass")),
        ("dammam", _("Dammam")),
        ("khobar", _("Khobar")),
        ("dhahran", _("Dhahran")),
        ("jubail", _("Jubail")),
        ("jeddah", _("Jeddah")),
        ("taif", _("Taif")),
        ("madinah", _("Madinah")),
        ("abha", _("Abha")),
        ("khamees", _("Khamis Mushait")),
        ("tabuk", _("Tabuk")),
        ("jazan", _("Jazan")),
        ("hail", _("Hail")),
        ("sakaka", _("Sakaka")),
        ("arar", _("Arar")),
        ("najran", _("Najran")),
        ("bahah", _("Al Bahah")),
        ("other", _("Other")),
    ]

    project_region = models.CharField(max_length=30, choices=REGION_CHOICES, blank=True, null=True)
    project_city = models.CharField(max_length=30, choices=CITY_CHOICES, blank=True, null=True)
    project_location_other = models.CharField(max_length=100, blank=True, null=True)

    LOCATION_CHOICES = [
        ("Other", _("Other")),
    ]
    project_location = models.CharField(max_length=255, choices=LOCATION_CHOICES, default="Other")

    LOCATION_TYPE_CHOICES = [
        ("On-site", _("On-site")),
        ("Online", _("Online")),
        ("Hybrid", _("Hybrid")),
    ]
    project_location_type = models.CharField(max_length=50, choices=LOCATION_TYPE_CHOICES)

    project_budget = models.IntegerField()
    project_duration = models.IntegerField()
    number_of_employees = models.IntegerField()
    description = models.TextField(null=True, blank=True)

    economic_indicator = models.CharField(max_length=20, null=True, blank=True, editable=False)
    num_of_similar_enterprises = models.IntegerField(null=True, blank=True, editable=False)

    REGION_CITY_TO_DATASET_LOC = {
        ("riyadh", "riyadh"): "منطقة الرياض, الرياض",
        ("riyadh", "diriyah"): "منطقة الرياض, الدرعية",
        ("riyadh", "kharj"): "منطقة الرياض, الخرج",
        ("qassim", "buraidah"): "منطقة القصيم, بريدة",
        ("qassim", "unaizah"): "منطقة القصيم, عنيزة",
        ("qassim", "ras"): "منطقة القصيم, الرس",
        ("eastern", "dammam"): "المنطقة الشرقية, الدمام",
        ("eastern", "khobar"): "المنطقة الشرقية, الخبر",
        ("eastern", "dhahran"): "المنطقة الشرقية, الظهران",
        ("eastern", "jubail"): "المنطقة الشرقية, الجبيل",
        ("makkah", "jeddah"): "منطقة مكة المكرمة, جدة",
        ("makkah", "taif"): "منطقة مكة المكرمة, الطائف",
        ("madinah", "madinah"): "منطقة المدينة المنورة, المدينة المنورة",
        ("asir", "abha"): "منطقة عسير, أبها",
        ("asir", "khamees"): "منطقة عسير, خميس مشيط",
        ("tabuk", "tabuk"): "منطقة تبوك, تبوك",
        ("jazan", "jazan"): "منطقة جازان, جازان",
        ("hail", "hail"): "منطقة حائل, حائل",
        ("jouf", "sakaka"): "منطقة الجوف, سكاكا",
        ("northern", "arar"): "منطقة الحدود الشمالية, عرعر",
        ("najran", "najran"): "منطقة نجران, نجران",
        ("bahah", "bahah"): "منطقة الباحة, الباحة",
    }

    TEXT_LOC_NORMALIZE = {
        "qassim": "منطقة القصيم",
        "riyadh": "منطقة الرياض",
        "makkah": "منطقة مكة المكرمة",
        "madinah": "منطقة المدينة المنورة",
        "eastern": "المنطقة الشرقية",
        "asir": "منطقة عسير",
        "tabuk": "منطقة تبوك",
        "jazan": "منطقة جازان",
        "hail": "منطقة حائل",
        "jouf": "منطقة الجوف",
        "najran": "منطقة نجران",
        "bahah": "منطقة الباحة",
        "northern": "منطقة الحدود الشمالية",
        "other": "Other",
    }

    def save(self, *args, **kwargs):
        region_df = calculate_update_economic_indicator()

        if not self.project_region or not self.project_city or self.project_region == "other" or self.project_city == "other":
            effective_loc = self.project_location_other.strip() if self.project_location_other else "Other"
            self.project_location = "Other"
        else:
            mapped = self.REGION_CITY_TO_DATASET_LOC.get((self.project_region, self.project_city))
            if mapped:
                effective_loc = mapped
                self.project_location = mapped
            else:
                effective_loc = "Other"
                self.project_location = "Other"

        effective_loc = ", ".join([p.strip() for p in str(effective_loc).split(",") if p.strip()])

        raw = (effective_loc or "").strip()
        norm = self.TEXT_LOC_NORMALIZE.get(raw.lower())
        if norm:
            effective_loc = norm

        region_data = region_df[region_df["region_project"].astype(str).str.strip() == effective_loc]

        value = None
        if not region_data.empty:
            value = float(region_data["economic_indicator"].values[0])

        if value is None:
            self.economic_indicator = "Unknown"
        else:
            if value <= 0.33:
                self.economic_indicator = "Low"
            elif value <= 0.66:
                self.economic_indicator = "Medium"
            else:
                self.economic_indicator = "High"

        self.num_of_similar_enterprises = get_similar_enterprises(self.Project_type, self.project_location)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project_name} - {self.project_location}"

    class Meta:
        db_table = "projects_table"


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)

    def is_valid(self):
        now = timezone.now()
        expiry_time = self.created_at + timezone.timedelta(minutes=10)
        return now <= expiry_time
