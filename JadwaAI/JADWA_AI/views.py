from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login
import random
from analysis.models import AnalysisResult
from django.utils import translation
from django.db.models import OuterRef, Subquery
from django.utils.translation import gettext as _


from .models import ContactMessage, PasswordResetOTP, Projects
from .forms import (
    ProjectInformationForm,
    JadwaUserCreationForm,
    JadwaAuthenticationForm,
    ForgotPasswordForm,
    OTPForm,
    ResetPasswordForm
)

User = get_user_model()


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
        messages.info(request, "You are already logged in.")
        return redirect("dashboard")

    if request.method == "POST":
        form = JadwaUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account has been created successfully! You are now logged in.")
            return redirect("dashboard")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = JadwaUserCreationForm()

    return render(request, "pages/register.html", {"form": form})


# =======================
# Login
# =======================

def jadwa_login(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect("dashboard")

    if request.method == "POST":
        form = JadwaAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "You have logged in successfully!")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password.")
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
                messages.error(request, "No user found with this email.")
                return redirect("forgot_password")

            otp = f"{random.randint(100000, 999999)}"
            PasswordResetOTP.objects.create(user=user, code=otp)

            send_mail(
                subject="Your Jadwa AI OTP Code",
                message=f"Your OTP code is: {otp}",
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
                otp_invalid = True   # ✅ الرمز غلط/منتهي
        else:
            otp_incomplete = True   # ✅ ما كتب 6 أرقام صح
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
            messages.success(request, "Password reset successfully. You can login now.")
            request.session.flush()
            # ✅ اسم المسار في urls عندك هو name="login"
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

        messages.error(request, "Please fix the errors below.")
        return render(request, "pages/project_new.html", {"form": form})

    # ✅ GET عادي: بدون initial_data
    form = ProjectInformationForm()
    return render(request, "pages/project_new.html", {"form": form})




# =======================
# Project Result Page
# =======================



@login_required
def project_result(request, pk):
    project = get_object_or_404(Projects, pk=pk)

    # ✅ جيب آخر نتيجة تحليل مرتبطة بالمشروع (يدعم project FK أو project_id)
    try:
        AnalysisResult._meta.get_field("project")
        result = AnalysisResult.objects.filter(project=project).order_by("-id").first()
    except Exception:
        result = AnalysisResult.objects.filter(project_id=project.id).order_by("-id").first()

    if not result:
        messages.error(request, "ما فيه نتيجة تحليل لهذا المشروع للحين. شغّلي التحليل أول.")
        return redirect("dashboard")

    lang = translation.get_language() or "en"
    recs_status = result.recommendations_status_ar if lang.startswith("ar") else result.recommendations_status_en

    return render(request, "analysis/result.html", {
        "project": project,
        "result": result,          # ✅ ضروري
        "recs_status": recs_status, # ✅ صحيح
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
            messages.success(request, "Welcome! Your account has been created.")
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
        messages.error(request, "Please fill in all required fields correctly.")
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

    messages.success(request, "Message sent successfully. We will get back to you shortly.")
    return redirect("/#contact")


@login_required
def user_dashboard(request):
    qs = Projects.objects.filter(user=request.user).order_by("-id")

    last_result = AnalysisResult.objects.filter(project_id=OuterRef("pk")).order_by("-id")

    projects = qs.annotate(
        last_score=Subquery(last_result.values("probability")[:1]),   # بدل feasibility_score
        last_decision=Subquery(last_result.values("label")[:1]),      # بدل decision
        last_result_id=Subquery(last_result.values("id")[:1]),
    )

    return render(request, "pages/dashboard.html", {
        "projects": projects,
        "profile_name": request.user.get_full_name() or request.user.username,
        "profile_email": request.user.email,
    })