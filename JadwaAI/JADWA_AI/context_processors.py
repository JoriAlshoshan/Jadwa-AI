from django.urls import reverse
from django.utils.translation import gettext as _

def global_page_meta(request):
    url_name = getattr(getattr(request, "resolver_match", None), "url_name", "") or ""

    HOME_URL = reverse("landing") + "#home"

    MAP = {
        "landing": {
            "title": "",
            "subtitle": "",
            "crumbs": [{"label": _("Home"), "url": HOME_URL}],
            "show": False,
        },

        "dashboard": {
            "title": _("Dashboard"),
            "subtitle": _("Manage your projects and run feasibility analysis."),
            "crumbs": [
                {"label": _("Home"), "url": HOME_URL},
                {"label": _("Dashboard"), "url": None},
            ],
            "show": True,
        },

        "project_new": {
            "title": _("Add Project"),
            "subtitle": _("Fill the project details to run feasibility analysis."),
            "crumbs": [
                {"label": _("Home"), "url": HOME_URL},
                {"label": _("Dashboard"), "url": reverse("dashboard")},
                {"label": _("Add Project"), "url": None},
            ],
            "show": True,
        },

        "edit_profile": {
            "title": _("Edit Profile"),
            "subtitle": "",
            "crumbs": [
                {"label": _("Home"), "url": HOME_URL},
                {"label": _("Dashboard"), "url": reverse("dashboard")},
                {"label": _("Edit Profile"), "url": None},
            ],
            "show": True,
        },

        "project_detail": {
            "title": _("Project Details"),
            "subtitle": "",
            "crumbs": [
                {"label": _("Home"), "url": HOME_URL},
                {"label": _("Dashboard"), "url": reverse("dashboard")},
                {"label": _("Project Details"), "url": None},
            ],
            "show": True,
        },

        "project_edit": {
            "title": _("Edit Project"),
            "subtitle": "",
            "crumbs": [
                {"label": _("Home"), "url": HOME_URL},
                {"label": _("Dashboard"), "url": reverse("dashboard")},
                {"label": _("Edit Project"), "url": None},
            ],
            "show": True,
        },

        "analysis_result": {
            "title": _("Analysis Result"),
            "subtitle": _("AI-powered feasibility insights for your project"),
            "crumbs": [
                {"label": _("Home"), "url": HOME_URL},
                {"label": _("Dashboard"), "url": reverse("dashboard")},
                {"label": _("Analysis Result"), "url": None},
            ],
            "show": True,
        },

            "success_stories": {
            "title": "",  
            "subtitle": "", 
            "crumbs": [
                {"label": _("Home"), "url": HOME_URL},
                {"label": _("Success Stories"), "url": None},
            ],
            "show": True,  
        },
    }

    meta = MAP.get(url_name)

    if not meta:
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