from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse

def site_login(request):
    error = None
    next_url = request.GET.get("next") or request.POST.get("next") or "/"
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        expected_user = getattr(settings, "ENGINEER_USERNAME", "")
        expected_pass = getattr(settings, "ENGINEER_PASSWORD", "")
        if username and password and username == expected_user and password == expected_pass:
            request.session["site_authenticated"] = True
            request.session.set_expiry(0)  # expires on browser close; change if needed
            return redirect(next_url)
        error = "Invalid credentials"
    return render(request, "auth/login.html", {"error": error, "next": next_url})

def site_logout(request):
    request.session.pop("site_authenticated", None)
    return redirect(reverse("site_login"))