from django.shortcuts import render, redirect
from django.contrib.auth.views import login_required
from django.contrib.auth import login, logout, authenticate, get_user_model
from .forms import UserLoginForm, UserRegisterForm
from django.contrib import messages

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from .tokens import account_activation_token

User = get_user_model()

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
            current_site = get_current_site(request)
            subject = "Activate Your ---- Account"
            message = render_to_string(
                'accounts/account_activation_email.html',{
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                }
            )
            user.email_user(subject, message)
            messages.info(request, "An activation link has been sent to your Email!")
            return redirect("login")
    else:
        form = UserRegisterForm()
    return render(request, "accounts/register.html", {'form': form})


def activate(request, uid, token):
    try:
        u_id = force_text(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=u_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and account_activation_token.check_token(user, token):
        user.active = True
        user.profile.confirmed_email = True
        user.profile.set_confirmed_date()
        user.save()
        login(request, user)
        messages.success(request, "we have confirmed your email!")
        return redirect("/")
    else:
        messages.error(request, "Account Activation Failed!")
        return render(request, "accounts/activation_invalid.html")
