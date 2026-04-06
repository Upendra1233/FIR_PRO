from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

# add API/exempt prefixes here
EXEMPT_PATHS = (
    "/static/",
    getattr(settings, "MEDIA_URL", "/media/"),
    "/login/",
    "/logout/",
    "/admin/",
    # allow feedback page (already suggested)
    "/direct_calls/submit_feedback/",
    # ALLOW JSON API endpoints under direct_calls (adjust exact prefixes as needed)
    "/direct_calls/api/",
    "/direct_calls/device-repair-form/",
    "/direct_calls/submit_feedback/",
    # any other public API prefixes:
    "/api/",
)

class SiteAuthMiddleware:
    """
    Require a single shared login for the site.
    Exemptions: static/media, login/logout, admin and explicit EXEMPT_PATHS prefixes.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.login_url = settings.LOGIN_URL or "/login/"

    def __call__(self, request):
        path = request.path or "/"

        # allow configured explicit exemptions
        if any(path.startswith(p) for p in EXEMPT_PATHS if p):
            return self.get_response(request)

        # allow login/logout and admin (safe fallback)
        try:
            login_path = reverse("site_login")
            logout_path = reverse("site_logout")
        except Exception:
            login_path = "/login/"
            logout_path = "/logout/"

        if path == login_path or path == logout_path or path.startswith("/admin/"):
            return self.get_response(request)

        # optional: allow JSON API POSTs by prefix (extra safety)
        content_type = (request.META.get("CONTENT_TYPE") or "").lower()
        if (content_type.startswith("application/json") or request.META.get("HTTP_ACCEPT", "").find("application/json") != -1) and (
            path.startswith("/direct_calls/") or path.startswith("/api/")
        ):
            return self.get_response(request)

        # allow if session authenticated
        if request.session.get("site_authenticated"):
            return self.get_response(request)

        # otherwise redirect to login preserving next
        return redirect(f"{self.login_url}?next={request.path}")