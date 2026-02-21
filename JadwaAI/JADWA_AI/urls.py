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
    path("projects/<int:pk>/delete/", views.project_delete, name="project_delete"),
    path("projects/<int:pk>/", views.project_detail, name="project_detail"),   # لاحقًا
    path("projects/<int:pk>/edit/", views.project_edit, name="project_edit"), # لاحقًا


    path("admin-dashboard/", views.Admin_Dashboard, name="Admin_Dashboard"),
    path("users-details/<int:id>/", views.user_detail, name="user_detail"),
    path("edit-user/<int:id>/", views.edit_user, name="edit_user"),
    path("delete-user/<int:id>/", views.delete_user, name="delete_user"),
    path("user_projects/<int:id>/", views.user_projects, name="user_projects"),
    path("admin/messages/list/", views.messages_list, name="messages_list"),
    path("message/<int:id>/", views.message_detail, name="message_detail"),
    # path("edit/<str : key>/", views.edit_content, name="edit_content"),

]
