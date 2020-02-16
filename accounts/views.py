from django.shortcuts import render, redirect
from django.contrib.auth.views import login_required
from django.contrib.auth import login, logout, authenticate
from .forms import UserLoginForm, UserRegisterForm


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

def register_view(request):
    _next = request.GET.get('next')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password2')
            user = form.save(commit=False)
            user.set_password(password)
            user.save()
            return redirect("/")
    else:
        form = UserRegisterForm()
    return render(request, "accounts/register.html", {'form': form})