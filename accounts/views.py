from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import login_required
from django.contrib.auth import login, logout, authenticate, get_user_model
from .forms import UserLoginForm, UserRegisterForm, UserAddressForm
from django.contrib import messages
from django.conf import settings

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from .tokens import account_activation_token

from .models import UserAddress
from orders.models import Order
from cart.cart import Cart

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
                # if user has order and not paid then add all the items to the cart session also
                if Order.objects.filter(user=user, paid=False):
                    cart = Cart(request)
                    order = Order.objects.filter(user=user, paid=False)[0]
                    for item in order.items.all():
                        prod = item.product
                        quan = item.quantity
                        cart.add(product=prod, quantity=quan)
                # redirect user to desired path
                if _next:
                    return redirect(_next)
                return redirect('/')
    else:
        form = UserLoginForm()
    return render(request, "accounts/login.html", {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:login')

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
            return redirect("accounts:login")
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

@login_required
def add_user_address(request):
    address_form = UserAddressForm(request.POST or None)
    if address_form.is_valid():
        address = address_form.save(commit=False)
        address.user = request.user
        address.save()
        return redirect('accounts:address_list')
    return render(request, "accounts/address_form.html", {'address_form': address_form})

@login_required
def edit_user_address(request, adr_id):
    address = get_object_or_404(UserAddress, id=adr_id)
    cc, phone = address.phone.split(" ")
    data = {
        'country_code': cc,
        'phone': phone,
    }
    address_form = UserAddressForm(request.POST or None, instance=address, initial=data)
    if address_form.is_valid():
        address_form.save()
        return redirect('accounts:address_list')
    return render(request, "accounts/address_form.html", {'address_form': address_form, 'address': address})

@login_required
def list_user_address(request):
    address_list = UserAddress.objects.filter(user=request.user)
    return render(request, "accounts/address_list.html", {'address_list': address_list})

@login_required
def delete_user_address(request, adr_id):
    address = get_object_or_404(UserAddress, id=adr_id)
    if request.method == 'POST':
        address.delete()
        return redirect('accounts:address_list')
    return render(request, "accounts/address_delete.html", {'address': address})
