from django.shortcuts import render, redirect
from accounts.forms import UserAddressForm
from .models import OrderItem, Order
from cart.cart import Cart

# Create your views here.

def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        address_form = UserAddressForm(request.POST)
        if address_form.is_valid():
            address = address_form.save()
            order = Order.objects.create(address=address)
            for item in cart:
                OrderItem.objects.create(order=order,product=item['product'], price=item['price'],
                                        quantity=item['quantity'])
            cart.clear()
            return render(request, "orders/order_created.html", {'order': order})
    else:
        address_form = UserAddressForm()
    
    return render(request, "orders/order_form.html", {'address_form': address_form, 'cart': cart})
