from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from accounts.forms import UserAddressForm
from accounts.models import UserAddress
from .models import OrderItem, Order
from cart.cart import Cart

# Create your views here.

User = get_user_model()

@login_required
def order_create(request, adr_id=None):
    cart = Cart(request)
    user = request.user
    addresses = user.addresses.all()
    address = None
    address_form = UserAddressForm()

    if adr_id:
        address = get_object_or_404(UserAddress, id=adr_id)
    elif request.method == 'POST':
        address_form = UserAddressForm(request.POST)
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user = request.user
            address.save()
    # create order when we got address else user might have entered wrong info
    if address:
        order = Order.objects.create(user=user, address=address)
        for item in cart:
            product = item['product']
            quantity = item['quantity']
            OrderItem.objects.create(order=order,product=product, price=item['price'],
                                    quantity=quantity)
            # update product stock quantity
            product.stock -= quantity
            product.save()

        # clear the cart
        cart.clear()
        return render(request, "orders/order_created.html", {'order': order})        
    
    return render(request, "orders/order_form.html", {'address_form': address_form, 'cart': cart, 'addresses': addresses})
