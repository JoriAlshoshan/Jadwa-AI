from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('JADWA_AI.urls')),


    path('accounts/', include('django.contrib.auth.urls')),
    path("i18n/", include("django.conf.urls.i18n")),

    path("analysis/", include("analysis.urls")),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



