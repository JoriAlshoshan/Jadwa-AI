from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import ContactMessage


# =======================
# Public pages
# =======================

def landing(request):
    return render(request, "pages/landing.html")


def success_stories(request):
    return render(request, "pages/success_stories.html")


# =======================
# User (After Login)
# =======================

@login_required
def dashboard(request):
    return render(request, "pages/dashboard.html")


@login_required
def project_new(request):
    """
    /projects/new/
    (مؤقت الآن) صفحة إضافة مشروع
    لاحقاً نحولها فورم + حفظ DB
    """
    return render(request, "pages/project_new.html")


# =======================
# Register (اختياري إذا بتستخدمين signup مخصص)
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

    ContactMessage.objects.create(
        full_name=name,
        email=email,
        topic=topic,
        message=message,
    )

    send_mail(
        subject=f"[Jadwa AI] New Contact: {topic}",
        message=f"Name: {name}\nEmail: {email}\nTopic: {topic}\n\nMessage:\n{message}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.CONTACT_NOTIFY_EMAIL],
        fail_silently=False,
    )

    messages.success(request, "Message sent successfully. We will get back to you shortly.")
    return redirect("/#contact")
