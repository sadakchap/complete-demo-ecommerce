from django.shortcuts import redirect
from django.contrib import messages
# from django.contrib.auth import get_user_model
from .models import Order
from cart.cart import Cart
# User = get_user_model()

# no unpaid orders

def no_active_order_msg(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            order_qs = Order.objects.filter(user=user, paid=False, cancelled=False)
            if order_qs.exists():
                messages.info(request, "You have an incomplete Order!")
        return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def no_active_order_redirect(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            order_qs = Order.objects.filter(user=user, paid=False, cancelled=False)
            if order_qs.exists():
                print('user has active unpaid order')
                order = order_qs[0]
                return redirect('orders:pending_order', order_id=order.id)
            else:
                return function(request, *args, **kwargs)
        else:
            return redirect('accounts:login')
    
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
        
    


def no_active_order(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            order_qs = Order.objects.filter(user=user, paid=False, cancelled=False)
            if order_qs.exists():
                order = order_qs[0]
                cart = Cart(request)
                cart.clear()
                print('user has active order which is not paid!')
                return redirect('orders:pending_order', order_id=order.id)
            else:
                print('user doesnt have any unpaid order')
                return function(request, *args, **kwargs)
        else:
            print('not logged in!')
            return redirect('accounts:login')
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
