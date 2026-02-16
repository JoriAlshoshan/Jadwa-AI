import json
import random

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login
from django.utils import translation
from django.utils.translation import gettext as _
from django.db.models import OuterRef, Subquery, FloatField, ExpressionWrapper
from django.core.files.storage import default_storage
from django.utils.translation import gettext as _
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .forms import JadwaUserCreationForm, account_activation_token
from django.contrib.auth import get_user_model

from analysis.models import AnalysisResult

from .forms import (
    ProjectInformationForm,
    JadwaUserCreationForm,
    JadwaAuthenticationForm,
    ForgotPasswordForm,
    OTPForm,
    ResetPasswordForm,
    EditProfileForm,
    REGION_TO_CITIES,
)
from .models import User, ContactMessage, PasswordResetOTP, Projects

User = get_user_model()


# =======================
# Edit Profile
# =======================
@login_required
def edit_profile(request):
    user = request.user

    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Profile updated successfully!"))
            return redirect("dashboard")
    else:
        form = EditProfileForm(instance=user)

    profile_image_url = None
    if getattr(user, "profile_image", None) and user.profile_image.name:
        if default_storage.exists(user.profile_image.name):
            profile_image_url = user.profile_image.url

    return render(request, "pages/edit_profile.html", {
        "form": form,
        "region_to_cities_json": json.dumps(REGION_TO_CITIES),
        "profile_image_url": profile_image_url,
    })


# =======================
# Public pages (No Login)
# =======================
def landing(request):
    return render(request, "pages/landing.html")


def success_stories(request):
    return render(request, "pages/success_stories.html")


def privacy(request):
    return render(request, "pages/privacy.html")


def terms(request):
    return render(request, "pages/terms.html")


# =======================
# SignUp
# =======================
def jadwa_signup(request):
    if request.user.is_authenticated:
        messages.info(request, _("You are already logged in."))
        return redirect("dashboard")

    if request.method == "POST":
        form = JadwaUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            from django.urls import reverse
            from .forms import account_activation_token
            activation_link = request.build_absolute_uri(
                reverse("activate_account", kwargs={"uid": user.pk, "token": account_activation_token.make_token(user)})
            )

            send_mail(
                subject=_("Activate your Jadwa AI account"),
                message=_(
                    f"Hi {user.username},\n\n"
                    f"Please click the link below to activate your account:\n{activation_link}\n\n"
                    "Thank you for joining Jadwa AI!"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
  
            messages.success(request, _("Your account was created. Check your email to activate it."))
            return redirect("login")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = JadwaUserCreationForm()

    return render(request, "pages/register.html", {"form": form})

def activate_account(request, uid, token):
    user = get_object_or_404(User, pk=uid)

    if account_activation_token.check_token(user, token):
        if not user.is_active:
            user.is_active = True
            user.save()
            login(request, user)
            messages.success(request, _(f"Welcome {user.username}, Your account has been activated successfully."))
        else:
            messages.info(request, _("Your account is already active."))

        return redirect("dashboard")  
    else:
        messages.error(request, _("Activation link is invalid or expired."))
        return redirect("login")
    
# =======================
# Login
# =======================
def jadwa_login(request):
    if request.user.is_authenticated:
        messages.info(request, _("You are already logged in."))
        return redirect("dashboard")

    if request.method == "POST":
        form = JadwaAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, _("You have logged in successfully!"))
            return redirect("dashboard")
        else:
            messages.error(request, _("Invalid username or password."))
    else:
        form = JadwaAuthenticationForm()

    return render(request, "registration/login.html", {"form": form})


# =======================
# Forgot Password
# =======================
def forgot_password(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, _("No user found with this email."))
                return redirect("forgot_password")

            otp = f"{random.randint(100000, 999999)}"
            PasswordResetOTP.objects.create(user=user, code=otp)

            send_mail(
                subject=_("Your Jadwa AI OTP Code"),
                message=_("Your OTP code is: ") + otp,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )

            request.session["reset_user_id"] = user.id
            messages.success(request, _("OTP sent to your email."))
            return redirect("verify_otp")
    else:
        form = ForgotPasswordForm()

    return render(request, "pages/forgot_password.html", {"form": form})


def verify_otp(request):
    user_id = request.session.get("reset_user_id")
    if not user_id:
        return redirect("forgot_password")

    user = get_object_or_404(User, id=user_id)

    otp_invalid = False
    otp_incomplete = False

    if request.method == "POST":
        otp_digits = [request.POST.get(f"otp{i}", "") for i in range(1, 7)]
        full_otp = "".join(otp_digits)

        form = OTPForm({"otp": full_otp})

        if form.is_valid():
            otp_obj = PasswordResetOTP.objects.filter(user=user, code=full_otp).last()

            if otp_obj and otp_obj.is_valid():
                request.session["otp_verified"] = True
                return redirect("reset_password")
            else:
                otp_invalid = True
        else:
            otp_incomplete = True
    else:
        form = OTPForm()

    return render(request, "pages/verify_otp.html", {
        "form": form,
        "otp_invalid": otp_invalid,
        "otp_incomplete": otp_incomplete,
    })


# =======================
# Reset Password
# =======================
def reset_password(request):
    if not request.session.get("otp_verified"):
        return redirect("forgot_password")

    user = get_object_or_404(User, id=request.session.get("reset_user_id"))

    if request.method == "POST":
        form = ResetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Password reset successfully. You can login now."))
            request.session.flush()
            return redirect("login")
    else:
        form = ResetPasswordForm(user)

    return render(request, "pages/reset_password.html", {"form": form})


# =======================
# Project Create (After Login)
# =======================
@login_required
def project_new(request):
    if request.method == "POST":
        form = ProjectInformationForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            return redirect("run_analysis", project_id=project.pk)

        messages.error(request, _("Please fix the errors below."))
        return render(request, "pages/project_new.html", {"form": form})

    form = ProjectInformationForm()
    return render(request, "pages/project_new.html", {"form": form})


# =======================
# Project Result Page
# =======================
@login_required
def project_result(request, pk):
    project = get_object_or_404(Projects, pk=pk)

    # آخر نتيجة مرتبطة بالمشروع
    try:
        AnalysisResult._meta.get_field("project")
        result = AnalysisResult.objects.filter(project=project).order_by("-id").first()
    except Exception:
        result = AnalysisResult.objects.filter(project_id=project.id).order_by("-id").first()

    if not result:
        messages.error(request, _("No analysis result for this project yet. Run the analysis first."))
        return redirect("dashboard")

    lang = translation.get_language() or "en"
    recs_status = result.recommendations_status_ar if lang.startswith("ar") else result.recommendations_status_en

    return render(request, "analysis/result.html", {
        "project": project,
        "result": result,
        "recs_status": recs_status,
        "has_other_ready": False,
    })


# =======================
# Register (optional duplicate)
# =======================
def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = JadwaUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _("Welcome! Your account has been created."))
            return redirect("dashboard")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = JadwaUserCreationForm()

    return render(request, "pages/register.html", {"form": form})


# =======================
# Contact
# =======================
def contact_submit(request):
    if request.method != "POST":
        return redirect("/#contact")

    name = (request.POST.get("name") or "").strip()
    email = (request.POST.get("email") or "").strip()
    topic = (request.POST.get("topic") or "").strip()
    message = (request.POST.get("message") or "").strip()

    if not name or not email or "@" not in email or not topic or not message:
        messages.error(request, _("Please fill in all required fields correctly."))
        return redirect("/#contact")

    ContactMessage.objects.create(
        full_name=name,
        email=email,
        topic=topic,
        message=message,
    )

    send_mail(
        subject=f"[Jadwa AI] New Contact: {topic}",
        message=(
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Topic: {topic}\n\n"
            f"Message:\n{message}"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.CONTACT_NOTIFY_EMAIL],
        fail_silently=False,
    )

    messages.success(request, _("Message sent successfully. We will get back to you shortly."))
    return redirect("/#contact")


# =======================
# Dashboard
# =======================
@login_required
def user_dashboard(request):
    lang = translation.get_language() or getattr(request, "LANGUAGE_CODE", "en") or "en"
    is_ar = str(lang).startswith("ar")

    qs = Projects.objects.filter(user=request.user).order_by("-id")

    last_result = AnalysisResult.objects.filter(
        user=request.user,
        project_id=OuterRef("pk")
    ).order_by("-id")

    projects = qs.annotate(
        last_score=Subquery(last_result.values("probability")[:1]),
        last_score_percent=ExpressionWrapper(
            Subquery(last_result.values("probability")[:1]) * 100,
            output_field=FloatField()
        ),
        last_decision=Subquery(last_result.values("label")[:1]),
        last_result_id=Subquery(last_result.values("id")[:1]),
        recs_status_ar=Subquery(last_result.values("recommendations_status_ar")[:1]),
        recs_status_en=Subquery(last_result.values("recommendations_status_en")[:1]),
        recs_ar=Subquery(last_result.values("recommendations_ar")[:1]),
        recs_en=Subquery(last_result.values("recommendations_en")[:1]),
    )

    # ======= FIX: Region/City labels (support OTHER + custom text) =======
    u = request.user

    REGION_LABELS = dict(Projects.REGION_CHOICES)
    CITY_LABELS = dict(Projects.CITY_CHOICES)

    # region_label
    if (u.region or "") == "other":
        region_label = (getattr(u, "region_custom", "") or "").strip()
    else:
        region_label = (REGION_LABELS.get(u.region, u.region or "") or "").strip()

    # city_label
    if (u.city or "") == "other":
        city_label = (getattr(u, "city_custom", "") or "").strip()
    else:
        city_label = (CITY_LABELS.get(u.city, u.city or "") or "").strip()

    # remove placeholders / fake values
    bad_vals = {"Other", "other", "Select region", "Select city", "---------", ""}
    if region_label in bad_vals:
        region_label = ""
    if city_label in bad_vals:
        city_label = ""

    # profile image url
    profile_image_url = None
    if getattr(u, "profile_image", None) and u.profile_image.name:
        if default_storage.exists(u.profile_image.name):
            profile_image_url = u.profile_image.url

    return render(request, "pages/dashboard.html", {
        "projects": projects,
        "profile_name": u.get_full_name() or u.username,
        "profile_email": u.email,
        "is_ar": is_ar,
        "region_label": region_label,
        "city_label": city_label,
        "profile_image_url": profile_image_url,  # ✅ مهم للتمبلت
    })
