"""
URL configuration for JadwaAI project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # App routes (Landing, pages, etc.)
    path('', include('JADWA_AI.urls')),

    #  Authentication (Login / Logout / Password reset)
    path('accounts/', include('django.contrib.auth.urls')),
]
