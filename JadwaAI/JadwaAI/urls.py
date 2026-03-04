from django.contrib import admin
from django.urls import path, include, reverse
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import Sitemap


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return ["landing", "success_stories", "privacy", "terms"]

    # def location(self, item):
    #     return reverse(item)
    def location(self, item):
     return f"https://jadwa-ai.com{reverse(item)}"

sitemaps = {
    "static": StaticViewSitemap(),
}

urlpatterns = [
    path('admin/', admin.site.urls),

    path(
        "google64563470828a31e3.html",
        TemplateView.as_view(
            template_name="google64563470828a31e3.html",
            content_type="text/plain"
        ),
    ),

    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),

    path('', include('JADWA_AI.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path("i18n/", include("django.conf.urls.i18n")),
    path("analysis/", include("analysis.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)