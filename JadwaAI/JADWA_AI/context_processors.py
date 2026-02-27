from django.urls import reverse
from django.utils.translation import gettext as _

def global_page_meta(request):
    """
    يطلع page_title + page_subtitle + breadcrumbs بشكل تلقائي
    حسب اسم الـ URL (request.resolver_match.url_name).
    تقدر أي صفحة تسوي override إذا مرّرت قيم من الـ view.
    """

    url_name = getattr(getattr(request, "resolver_match", None), "url_name", "") or ""

    # Mapping (عدّلي الأسماء حسب urls عندك)
    MAP = {
        "landing": {
            "title": "",
            "subtitle": "",
            "crumbs": [
                {"label": _("Home"), "url": reverse("landing")},
            ],
            "show": False,  # لا تعرض الهيدر في اللاندنق
        },

        "dashboard": {
            "title": _("Dashboard"),
            "subtitle": _("Manage your projects and run feasibility analysis."),
            "crumbs": [
                {"label": _("Home"), "url": reverse("landing")},
                {"label": _("Dashboard"), "url": None},
            ],
            "show": True,
        },

        "project_new": {
            "title": _("Add Project"),
            "subtitle": _("Fill the project details to run feasibility analysis."),
            "crumbs": [
                {"label": _("Home"), "url": reverse("landing")},
                {"label": _("Dashboard"), "url": reverse("dashboard")},
                {"label": _("Add Project"), "url": None},
            ],
            "show": True,
        },

        "edit_profile": {
            "title": _("Edit Profile"),
            "subtitle": "",
            "crumbs": [
                {"label": _("Home"), "url": reverse("landing")},
                {"label": _("Dashboard"), "url": reverse("dashboard")},
                {"label": _("Edit Profile"), "url": None},
            ],
            "show": True,
        },

        "project_detail": {
            "title": _("Project Details"),
            "subtitle": "",
            "crumbs": [
                {"label": _("Home"), "url": reverse("landing")},
                {"label": _("Dashboard"), "url": reverse("dashboard")},
                {"label": _("Project Details"), "url": None},  # اسم المشروع نضيفه بالـ view لو تبين
            ],
            "show": True,
        },

        "project_edit": {
            "title": _("Edit Project"),
            "subtitle": "",
            "crumbs": [
                {"label": _("Home"), "url": reverse("landing")},
                {"label": _("Dashboard"), "url": reverse("dashboard")},
                {"label": _("Edit Project"), "url": None},
            ],
            "show": True,
        },
        "analysis_result": {   # 👈 هنا حطيه
        "title": _("Analysis Result"),
        "subtitle": _("AI-powered feasibility insights for your project"),
        "crumbs": [
            {"label": _("Home"), "url": reverse("landing")},
            {"label": _("Dashboard"), "url": reverse("dashboard")},
            {"label": _("Analysis Result"), "url": None},
        ],
        "show": True,
    },
    }

    meta = MAP.get(url_name, None)

    if not meta:
        # افتراضي لأي صفحة ما عرفناها
        return {
            "page_title": "",
            "page_subtitle": "",
            "breadcrumbs": [],
            "show_page_header": False,
        }

    return {
        "page_title": meta.get("title", ""),
        "page_subtitle": meta.get("subtitle", ""),
        "breadcrumbs": meta.get("crumbs", []),
        "show_page_header": meta.get("show", True),
    }