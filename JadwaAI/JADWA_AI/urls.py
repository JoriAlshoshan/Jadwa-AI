from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("success-stories/", views.success_stories, name="success_stories"),
    path("contact/", views.contact_submit, name="contact_submit"),
]
