from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "topic", "created_at")
    list_filter = ("topic", "created_at")
    search_fields = ("full_name", "email", "message")
    ordering = ("-created_at",)
