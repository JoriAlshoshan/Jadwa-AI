from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("success-stories/", views.success_stories, name="success_stories"),

    path("register/", views.register, name="register"),

    path("projects/new/", views.project_new, name="project_new"),
    path("projects/<int:pk>/result/", views.project_result, name="project_result"),

    path("contact/", views.contact_submit, name="contact_submit"),
    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),

    path("login/", views.jadwa_login, name="login"),
    path("signup/", views.jadwa_signup, name="signup"),
    path('activate/<int:uid>/<str:token>/', views.activate_account, name='activate_account'),
    path("logout/", auth_views.LogoutView.as_view(next_page="landing"), name="logout"),

    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("reset-password/", views.reset_password, name="reset_password"),

    
    path("dashboard/", views.user_dashboard, name="dashboard"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),


]
