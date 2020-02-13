from django.shortcuts import render, redirect
from django.contrib.auth.views import login_required
from django.contrib.auth import login, logout, authenticate
from .forms import UserLoginForm


# Create your views here.
def home_view(request):
    return render(request, "home.html", context={})

def login_view(request):
    _next = request.GET.get('next')
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            pswd  = form.cleaned_data.get('password')
            user = authenticate(username=email, password=pswd)
            if user:
                login(request, user)
                if _next:
                    return redirect(_next)
                return redirect('/')
    else:
        form = UserLoginForm()
    return render(request, "accounts/login.html", {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')