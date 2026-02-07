from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

from .fill_economic_indicator import calculate_update_economic_indicator


class User(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'username'
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
        ("demo", "Request a demo"),
        ("support", "Support"),
        ("partnership", "Partnership"),
        ("other", "Other"),
    ]

    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    topic = models.CharField(max_length=30, choices=TOPIC_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.topic}"


class Projects(models.Model):
    project_name = models.CharField(max_length=20)

    PROJECT_TYPE_CHOICES = [
        ("Service", "Service"),
        ("Product", "Product"),
        ("Hybrid", "Hybrid"),
    ]
    Project_type = models.CharField(max_length=50, choices=PROJECT_TYPE_CHOICES, db_column="Project_type")

    LOCATION_CHOICES = [
        ("الأحساء", "الأحساء"),
        ("الجبيل, الجبيل الصناعية", "الجبيل, الجبيل الصناعية"),
        ("الرياض", "الرياض"),
        ("القدية", "القدية"),
        ("القطيف, المنطقة الشرقية", "القطيف, المنطقة الشرقية"),
        ("المنطقة الشرقية", "المنطقة الشرقية"),
        ("المنطقة الشرقية, الأحساء", "المنطقة الشرقية, الأحساء"),
        ("المنطقة الشرقية, الجبيل", "المنطقة الشرقية, الجبيل"),
        ("المنطقة الشرقية, الجبيل الصناعية", "المنطقة الشرقية, الجبيل الصناعية"),
        ("المنطقة الشرقية, الجبيل, الجبيل الصناعية", "المنطقة الشرقية, الجبيل, الجبيل الصناعية"),
        ("المنطقة الشرقية, الخبر", "المنطقة الشرقية, الخبر"),
        ("المنطقة الشرقية, الخفجي", "المنطقة الشرقية, الخفجي"),
        ("المنطقة الشرقية, الدمام", "المنطقة الشرقية, الدمام"),
        ("المنطقة الشرقية, الظهران", "المنطقة الشرقية, الظهران"),
        ("المنطقة الشرقية, جزيرة تاروت", "المنطقة الشرقية, جزيرة تاروت"),
        ("المنطقة الشرقية, حفر الباطن", "المنطقة الشرقية, حفر الباطن"),
        ("المنطقة الشرقية, رأس الخير", "المنطقة الشرقية, رأس الخير"),
        ("جدة", "جدة"),
        ("حائل", "حائل"),
        ("فيفاء, منطقة جازان", "فيفاء, منطقة جازان"),
        ("مكة المكرمة, الطائف", "مكة المكرمة, الطائف"),
        ("مكة المكرمة, مدينة الملك عبدالله الاقتصادية, المدينة المنورة, جدة", "مكة المكرمة, مدينة الملك عبدالله الاقتصادية, المدينة المنورة, جدة"),
        ("مكة المكرمة, منطقة مكة المكرمة", "مكة المكرمة, منطقة مكة المكرمة"),
        ("مكة المكرمة, منطقة مكة المكرمة, جدة", "مكة المكرمة, منطقة مكة المكرمة, جدة"),
        ("مكة المكرمة, منطقة مكة المكرمة, منطقة الرياض, المزاحمية, البرابر, الجموم, الرياض, جدة", "مكة المكرمة, منطقة مكة المكرمة, منطقة الرياض, المزاحمية, البرابر, الجموم, الرياض, جدة"),
        ("مكة المكرمة, منطقة مكة المكرمة, منطقة القصيم", "مكة المكرمة, منطقة مكة المكرمة, منطقة القصيم"),
        ("منطقة الباحة", "منطقة الباحة"),
        ("منطقة الباحة, الباحة", "منطقة الباحة, الباحة"),
        ("منطقة الباحة, بلجرشي", "منطقة الباحة, بلجرشي"),
        ("منطقة الجوف, القريات", "منطقة الجوف, القريات"),
        ("منطقة الجوف, دومة الجندل", "منطقة الجوف, دومة الجندل"),
        ("منطقة الجوف, سكاكا", "منطقة الجوف, سكاكا"),
        ("منطقة الجوف, طبرجل", "منطقة الجوف, طبرجل"),
        ("منطقة الحدود الشمالية, طريف", "منطقة الحدود الشمالية, طريف"),
        ("منطقة الحدود الشمالية, عرعر", "منطقة الحدود الشمالية, عرعر"),
        ("منطقة الرياض", "منطقة الرياض"),
        ("منطقة الرياض, الأفلاج", "منطقة الرياض, الأفلاج"),
        ("منطقة الرياض, الخرج", "منطقة الرياض, الخرج"),
        ("منطقة الرياض, الدرعية", "منطقة الرياض, الدرعية"),
        ("منطقة الرياض, الرياض", "منطقة الرياض, الرياض"),
        ("منطقة الرياض, القويعية", "منطقة الرياض, القويعية"),
        ("منطقة الرياض, المجمعة", "منطقة الرياض, المجمعة"),
        ("منطقة الرياض, المزاحمية", "منطقة الرياض, المزاحمية"),
        ("منطقة الرياض, المنطقة الشرقية, الدمام, الرياض", "منطقة الرياض, المنطقة الشرقية, الدمام, الرياض"),
        ("منطقة الرياض, شقراء", "منطقة الرياض, شقراء"),
        ("منطقة الرياض, عفيف", "منطقة الرياض, عفيف"),
        ("منطقة الرياض, مدينة سدير للصناعة والأعمال", "منطقة الرياض, مدينة سدير للصناعة والأعمال"),
        ("منطقة القصيم, البكيرية", "منطقة القصيم, البكيرية"),
        ("منطقة القصيم, الرس", "منطقة القصيم, الرس"),
        ("منطقة القصيم, بريدة", "منطقة القصيم, بريدة"),
        ("منطقة القصيم, رياض الخبراء", "منطقة القصيم, رياض الخبراء"),
        ("منطقة القصيم, عنيزة", "منطقة القصيم, عنيزة"),
        ("منطقة القصيم, منطقة الرياض, المنطقة الشرقية, الجبيل", "منطقة القصيم, منطقة الرياض, المنطقة الشرقية, الجبيل"),
        ("منطقة المدينة المنورة", "منطقة المدينة المنورة"),
        ("منطقة المدينة المنورة, الحناكية", "منطقة المدينة المنورة, الحناكية"),
        ("منطقة المدينة المنورة, العلا", "منطقة المدينة المنورة, العلا"),
        ("منطقة المدينة المنورة, المدينة المنورة", "منطقة المدينة المنورة, المدينة المنورة"),
        ("منطقة المدينة المنورة, بدر", "منطقة المدينة المنورة, بدر"),
        ("منطقة المدينة المنورة, منطقة الرياض, المنطقة الشرقية", "منطقة المدينة المنورة, منطقة الرياض, المنطقة الشرقية"),
        ("منطقة المدينة المنورة, منطقة حائل, المدينة المنورة, حائل", "منطقة المدينة المنورة, منطقة حائل, المدينة المنورة, حائل"),
        ("منطقة تبوك", "منطقة تبوك"),
        ("منطقة تبوك, أملج", "منطقة تبوك, أملج"),
        ("منطقة تبوك, تبوك", "منطقة تبوك, تبوك"),
        ("منطقة تبوك, شرما", "منطقة تبوك, شرما"),
        ("منطقة تبوك, ضبا", "منطقة تبوك, ضبا"),
        ("منطقة جازان", "منطقة جازان"),
        ("منطقة جازان, الشقيق", "منطقة جازان, الشقيق"),
        ("منطقة جازان, جازان", "منطقة جازان, جازان"),
        ("منطقة جازان, مدينة جازان للصناعات الاساسية والتحويلية", "منطقة جازان, مدينة جازان للصناعات الاساسية والتحويلية"),
        ("منطقة حائل", "منطقة حائل"),
        ("منطقة حائل, الغزالة", "منطقة حائل, الغزالة"),
        ("منطقة حائل, حائل", "منطقة حائل, حائل"),
        ("منطقة عسير", "منطقة عسير"),
        ("منطقة عسير, أبها", "منطقة عسير, أبها"),
        ("منطقة عسير, بيشة", "منطقة عسير, بيشة"),
        ("منطقة عسير, خميس مشيط", "منطقة عسير, خميس مشيط"),
        ("منطقة عسير, محايل عسير", "منطقة عسير, محايل عسير"),
        ("منطقة مكة المكرمة, الجموم", "منطقة مكة المكرمة, الجموم"),
        ("منطقة مكة المكرمة, الطائف", "منطقة مكة المكرمة, الطائف"),
        ("منطقة مكة المكرمة, القنفذة", "منطقة مكة المكرمة, القنفذة"),
        ("منطقة مكة المكرمة, الكامل", "منطقة مكة المكرمة, الكامل"),
        ("منطقة مكة المكرمة, الليث", "منطقة مكة المكرمة, الليث"),
        ("منطقة مكة المكرمة, بحرة", "منطقة مكة المكرمة, بحرة"),
        ("منطقة مكة المكرمة, تربة", "منطقة مكة المكرمة, تربة"),
        ("منطقة مكة المكرمة, ثول", "منطقة مكة المكرمة, ثول"),
        ("منطقة مكة المكرمة, جدة", "منطقة مكة المكرمة, جدة"),
        ("منطقة مكة المكرمة, رابغ", "منطقة مكة المكرمة, رابغ"),
        ("منطقة مكة المكرمة, مدينة الملك عبدالله الاقتصادية", "منطقة مكة المكرمة, مدينة الملك عبدالله الاقتصادية"),
        ("منطقة مكة المكرمة, منطقة الرياض, منطقة عسير, محايل عسير, المنطقة الشرقية, الدمام, الرياض, جدة", "منطقة مكة المكرمة, منطقة الرياض, منطقة عسير, محايل عسير, المنطقة الشرقية, الدمام, الرياض, جدة"),
        ("منطقة مكة المكرمة, منطقة جازان, مدينة جازان للصناعات الاساسية والتحويلية, الفيصلية, الليث, الشعيبة, جازان, جدة", "منطقة مكة المكرمة, منطقة جازان, مدينة جازان للصناعات الاساسية والتحويلية, الفيصلية, الليث, الشعيبة, جازان, جدة"),
        ("منطقة نجران", "منطقة نجران"),
        ("نجران, منطقة نجران", "نجران, منطقة نجران"),
        ("وادي الدواسر, منطقة الرياض", "وادي الدواسر, منطقة الرياض"),
        ("وعد الشمال, منطقة الحدود الشمالية", "وعد الشمال, منطقة الحدود الشمالية"),
        ("وعد الشمال, منطقة القصيم, منطقة الجوف, منطقة الحدود الشمالية, منطقة الرياض, منطقة حائل, مدينة سدير للصناعة والأعمال, المجمعة, الرياض, بريدة, حائل, عرعر", "وعد الشمال, منطقة القصيم, منطقة الجوف, منطقة الحدود الشمالية, منطقة الرياض, منطقة حائل, مدينة سدير للصناعة والأعمال, المجمعة, الرياض, بريدة, حائل, عرعر"),
        ("ينبع, الأحساء, الجبيل الصناعية, الخرج, الطائف, عنيزة", "ينبع, الأحساء, الجبيل الصناعية, الخرج, الطائف, عنيزة"),
        ("ينبع, منطقة المدينة المنورة", "ينبع, منطقة المدينة المنورة"),
        ("Other", "Other"),
    ]

    # ✅ max_length كبير بسبب القيم الطويلة
    project_location = models.CharField(max_length=255, choices=LOCATION_CHOICES)
    project_location_other = models.CharField(max_length=100, blank=True, null=True)

    LOCATION_TYPE_CHOICES = [
        ("On-site", "On-site"),
        ("Online", "Online"),
        ("Hybrid", "Hybrid"),
    ]
    project_location_type = models.CharField(max_length=50, choices=LOCATION_TYPE_CHOICES)

    project_budget = models.IntegerField(null=False, blank=False)
    project_duration = models.IntegerField(null=False, blank=False)
    number_of_employees = models.IntegerField(null=False, blank=False)

    economic_indicator = models.CharField(null=True, blank=True, editable=False)
    Number_of_Similar_Enterprises = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        region_df = calculate_update_economic_indicator()

        # ✅ لو Other استخدمي النص المكتوب، غير كذا استخدمي الاختيار
        if self.project_location == "Other" and self.project_location_other:
            effective_loc = self.project_location_other.strip()
        else:
            effective_loc = (self.project_location or "").strip()

        # تنظيف بسيط للمسافات حول الفواصل
        effective_loc = ", ".join([p.strip() for p in effective_loc.split(",") if p.strip()])

        region_data = region_df[region_df['region_project'].astype(str).str.strip() == effective_loc]

        value = None
        if not region_data.empty:
            value = float(region_data['economic_indicator'].values[0])

        if value is None:
            self.economic_indicator = None
        else:
            if value <= 0.33:
                self.economic_indicator = "Low"
            elif value <= 0.66:
                self.economic_indicator = "Medium"
            else:
                self.economic_indicator = "High"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project_name} - {self.project_location}"

    class Meta:
        db_table = 'projects_table'


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)

    def is_valid(self):
        now = timezone.now()
        expiry_time = self.created_at + timezone.timedelta(minutes=10)
        return now <= expiry_time
