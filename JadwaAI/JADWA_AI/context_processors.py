from django.urls import reverse
from django.utils.translation import gettext as _
from .models import SiteContent
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

        "Admin_Dashboard": {
            "title": _("Admin Dashboard"),
            "subtitle": _("Manage users, projects, messages, and site content from one place."),
            "crumbs": [
                {"label": _("Home"), "url": HOME_URL},
                {"label": _("Admin Dashboard"), "url": None},
            ],
            "show": True,
        },

        "user_detail": {
            "title": _("User Details"),
            "subtitle": _("Manage user account information and permissions."),
            "crumbs": [
                {"label": _("Home"), "url": HOME_URL},
                {"label": _("Admin Dashboard"), "url": reverse("Admin_Dashboard")},
                {"label": _("Users"), "url": reverse("Admin_Dashboard")},
                {"label": _("User Details"), "url": None},
            ],
            "show": True,
        },

        "edit_user": {
            "title": _("Edit User"),
            "subtitle": _("Update user account details and roles."),
            "crumbs": [
                {"label": _("Home"), "url": HOME_URL},
                {"label": _("Admin Dashboard"), "url": reverse("Admin_Dashboard")},
                {"label": _("Users"), "url": reverse("Admin_Dashboard")},
                {"label": _("Edit User"), "url": None},
            ],
            "show": True,
        },

        "user_projects": {
            "title": _("User Projects"),
            "subtitle": _("Review projects created by this user."),
            "crumbs": [
                {"label": _("Home"), "url": HOME_URL},
                {"label": _("Admin Dashboard"), "url": reverse("Admin_Dashboard")},
                {"label": _("Users"), "url": reverse("Admin_Dashboard")},
                {"label": _("User Projects"), "url": None},
            ],
            "show": True,
        },

        "messages_list": {
            "title": _("Messages"),
            "subtitle": _("Review contact requests and user inquiries."),
            "crumbs": [
                {"label": _("Home"), "url": HOME_URL},
                {"label": _("Admin Dashboard"), "url": reverse("Admin_Dashboard")},
                {"label": _("Messages"), "url": None},
            ],
            "show": True,
        },

        "send_message": {
            "title": _("Message Details"),
            "subtitle": _("Read and reply to contact messages."),
            "crumbs": [
                {"label": _("Home"), "url": HOME_URL},
                {"label": _("Admin Dashboard"), "url": reverse("Admin_Dashboard")},
                {"label": _("Messages"), "url": reverse("messages_list")},
                {"label": _("Message Details"), "url": None},
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

def global_site_content(request):
    site_content = SiteContent.objects.first()
    return {
        "site_content": site_content
    }