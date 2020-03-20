from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse
from payments.paytm import checksum

from accounts.forms import UserAddressForm
from accounts.models import UserAddress
from .models import OrderItem, Order
from cart.cart import Cart
from .tasks import send_invoice_order

# Create your views here.

User = get_user_model()

@login_required
def order_create(request, adr_id=None):
    cart = Cart(request)
    user = request.user
    addresses = user.addresses.all()
    address = None
    address_form = UserAddressForm(request.POST or None)

    if adr_id:
        address = get_object_or_404(UserAddress, id=adr_id)
    if address_form.is_valid():
        print('going in')
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
        send_invoice_order.delay(order.id) #launchinf async task

        # request.session['order_id'] = order.id
        
        #request payment to transfer amount
        params = {
            "MID": settings.PAYMENT_MERCHANT_ID,
            "ORDER_ID": str(order.id),
            "CUST_ID": str(order.user.email),
            "TXN_AMOUNT": str(order.get_total_cost()),
            "CHANNEL_ID": "WEB",
            "INDUSTRY_TYPE_ID": "Retail",
            "WEBSITE": "WEBSTAGING",
            "CALLBACK_URL": request.build_absolute_uri(reverse('payments:process'))
        }
        params['CHECKSUMHASH'] = checksum.generate_checksum(params, settings.PAYMENT_MERCHANT_KEY)
        print(request.session.get('order_id'))
        return render(request, "payments/paytm.html", {'params': params})
        # return render(request, "orders/order_created.html", {'order': order})        
    
    return render(request, "orders/order_form.html", {'address_form': address_form, 'cart': cart, 'addresses': addresses})
