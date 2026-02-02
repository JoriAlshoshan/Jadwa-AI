from django.db import models
from django.conf import settings
from django.utils import timezone
from .fill_economic_indicator import calculate_update_economic_indicator
from django.contrib.auth.models import AbstractUser

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
        ("Service","Service"),
        ("Product","Product"),
        ("Hybrid","Hybrid"),
    ]
    Project_type = models.CharField(max_length=50,choices=PROJECT_TYPE_CHOICES,db_column="Project_type")
    project_location = models.CharField(max_length=50)
    LOCATION_TYPE_CHOICES = [
        ("On-site","On-site"),
        ("Online","Online"),
        ("Hybrid","Hybrid"),
    ]
    project_location_type = models.CharField(max_length=50,choices=LOCATION_TYPE_CHOICES)
    project_budget = models.IntegerField(null = False , blank = False)
    project_duration = models.IntegerField(null = False , blank = False)
    number_of_employees = models.IntegerField(null = False , blank = False)
    economic_indicator = models.CharField(null=True, blank=True,editable =False)
    Number_of_Similar_Enterprises = models.IntegerField(null=True, blank=True)
   
    def save(self, *args, **kwargs):
        region_df = calculate_update_economic_indicator()
        region_data = region_df[region_df['region_project'] == self.project_location]
        if not region_data.empty:
            self.economic_indicator = float(region_data['economic_indicator'].values[0])
            value = self.economic_indicator

        if value<=0.33:
            self.economic_indicator ="Low"
        elif value<=0.66:
            self.economic_indicator ="Medium"
        else:
            self.economic_indicator ="High"

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
        print(f"DEBUG: Now: {now} | Created: {self.created_at} | Expires: {expiry_time}")
        return now <= expiry_time
