from django.contrib import admin
from .models import ContactMessage, Projects


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "topic", "created_at")
    list_filter = ("topic", "created_at")
    search_fields = ("full_name", "email", "message")
    ordering = ("-created_at",)

class EconomicIndicatorAdmin(admin.ModelAdmin):
    list_display = ('project_location','economic_indicator')

admin.site.register(Projects)