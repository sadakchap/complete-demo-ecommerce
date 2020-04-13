from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.http import HttpResponse
import weasyprint

from accounts.forms import UserAddressForm
from accounts.models import UserAddress
from .models import OrderItem, Order
from cart.cart import Cart
from .tasks import send_invoice_order
from coupons.models import Coupon

# Create your views here.

User = get_user_model()

@login_required
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
    unique_order_id = order.set_unique_paytm_order_id()
    request.session['order_id'] = unique_order_id
    return redirect(reverse('payments:process'))


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
