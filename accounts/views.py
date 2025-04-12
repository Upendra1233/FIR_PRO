from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')  # Redirect to root URL after successful login
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)  # Log out the user
    return redirect('login')  # Redirect to the login page

def home_view(request):
    role = request.session.get('role', None)
    if not role:
        return redirect('login')  # Redirect to login if not logged in

    return render(request, 'accounts/home.html', {'role': role})


def homepage(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if not logged in

    # Get the user's role from the session or database
    role = request.session.get('role', 'Unknown Role')  # Default to 'Unknown Role' if not set
    username = request.user.username  # Get the logged-in user's username

    print(f"Username: {request.user.username}")
    print(f"Role: {request.session.get('role')}")

    return render(request, 'psnapp/homepage.html', {'role': role, 'username': username})
