from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from .models import ContactMessage
from .forms import JadwaUserCreationForm, JadwaAuthenticationForm, ProjectInformationForm

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

    return render(request, "pages/login.html", {"form": form})

# =======================
# User (After Login)
# =======================

@login_required
def dashboard(request):
    return render(request, "pages/dashboard.html")


@login_required
def project_new(request):
    form = ProjectInformationForm()
    return render(request, "pages/project_new.html",{"form":form})

# =======================
# Register
# =======================

def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
        messages.error(request, "Please fix the errors below.")
    else:
        form = UserCreationForm()

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

    # Save message
    ContactMessage.objects.create(
        full_name=name,
        email=email,
        topic=topic,
        message=message,
    )

    # Email notification
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

    messages.success(
        request,
        "Message sent successfully. We will get back to you shortly."
    )
    return redirect("/#contact")