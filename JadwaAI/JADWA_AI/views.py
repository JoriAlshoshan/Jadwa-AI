from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactMessage


def landing(request):
    return render(request, "pages/landing.html")


def success_stories(request):
    return render(request, "pages/success_stories.html")


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

    messages.success(request, "Message sent successfully. We will get back to you shortly.")
    return redirect("/#contact")
