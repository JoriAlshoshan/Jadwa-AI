from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # App routes (Landing, pages, etc.)
    path('', include('JADWA_AI.urls')),

    # Authentication
    path('accounts/', include('django.contrib.auth.urls')),
    path("i18n/", include("django.conf.urls.i18n")),

    #  Put analysis under a clear prefix
    path("analysis/", include("analysis.urls")),
]
