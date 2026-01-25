from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("success-stories/", views.success_stories, name="success_stories"),

    path("dashboard/", views.dashboard, name="dashboard"),
    path("register/", views.register, name="register"),

    path("projects/new/", views.project_new, name="project_new"),

    path("contact/", views.contact_submit, name="contact_submit"),
    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),
]
