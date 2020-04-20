from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib import messages
import weasyprint

from accounts.forms import UserAddressForm
from accounts.models import UserAddress
from .models import OrderItem, Order
from cart.cart import Cart
from .tasks import send_invoice_order
from coupons.models import Coupon
from .decorators import no_active_order_redirect

# Create your views here.

User = get_user_model()

@login_required
@no_active_order_redirect
def order_summary(request):
    cart = Cart(request)
    user = request.user
    address_list = user.addresses.order_by('-created')
    modal = False
    if request.method == 'POST':
        modal = True
        address_form = UserAddressForm(request.POST)
        if address_form.is_valid():
            print('form is valid')
            address = address_form.save(commit=False)
            address.user = user
            address.save()
            return redirect('orders:order_summary')
    else:
        address_form = UserAddressForm()
    context = {
        'cart': cart,
        'address_form': address_form,
        'address_list': address_list,
        'modal': modal,
    }
    return render(request, "orders/order_summary.html", context=context)


@login_required
@no_active_order_redirect
def order_create(request, adr_id):
    cart = Cart(request)
    user = request.user
    address = get_object_or_404(UserAddress, id=adr_id)
    order = Order.objects.create(user=user, address=address)
    for item in cart:
        product = item['product']
        quantity = item['quantity']
        OrderItem.objects.create(order=order, product=product, price=item['price'],
                                 quantity=quantity)
        product.stock -= quantity
        product.save()
    # if cart has discount coupon applicable then save its info on order 
    if cart.coupon and cart.coupon.is_active():
        order.coupon = cart.coupon
        order.discount = cart.coupon.discount
        order.save()

    cart.clear()
    send_invoice_order.delay(order.id)  # launchinf async task
    return redirect(reverse('payments:process', kwargs={'order_id': order.id}))


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "orders/admin/order_detail.html", {'order': order})


@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string('orders/order_invoice.html', {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    weasyprint.HTML(string=html).write_pdf(response, stylesheets=[
        weasyprint.CSS(settings.STATIC_ROOT +'\\' + 'css/order_invoice.css')
    ])
    return response

@login_required
def user_pending_order_action(request, order_id):
    user = request.user
    order = get_object_or_404(Order, id=order_id)
    address_list = user.addresses.order_by('-created')
    modal = False
    if request.method == 'POST':
        modal = True
        address_form = UserAddressForm(request.POST)
        if address_form.is_valid():
            print('form is valid')
            address = address_form.save(commit=False)
            address.user = user
            address.save()
            return redirect('orders:pending_order')
    else:
        address_form = UserAddressForm()

    msg = '''You have an incompleted Order, 
            before making any other orders Please complete this order by making 
            payment or cancelling the Order!'''
    context = {
        'order': order,
        'address_form': address_form,
        'address_list': address_list,
        'modal': modal
    }
    messages.info(request, msg)
    return render(request, "orders/pending_order.html", context=context)

@login_required
def user_pending_order_update(request, adr_id, order_id):
    user = request.user
    address = get_object_or_404(UserAddress, id=adr_id)
    order = get_object_or_404(Order, id=order_id)
    if order.address != address:
        order.address = address
        order.save()
    # send updated order invoice
    send_invoice_order.delay(order.id)
    return redirect(reverse('payments:process', kwargs={'order_id': order.id}))


@login_required
def cancel_pending_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.cancelled = True
    order.save()
    return redirect('/')
