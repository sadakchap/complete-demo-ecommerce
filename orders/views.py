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
    address = get_object_or_404(UserAddress, id=adr_id)
    
    order_qs = Order.objects.filter(user=user, paid=False)
    if order_qs.exists():
        order = order_qs[0]
    else:
        order = Order.objects.create(user=user, address=address)

        for item in cart:
            product = item['product']
            quantity = item['quantity']
            if order.items.filter(product_id=product.id):
                order_item = order.items.get(product_id=product.id)
                order_item.quantity += quantity
                order_item.save()
            else:
                OrderItem.objects.create(order=order,product=product, price=item['price'],
                                    quantity=quantity)
            # update product stock quantity
            product.stock -= quantity
            product.save()
        if cart.coupon:
            order.coupon = cart.coupon
            order.discount = cart.coupon.discount
            order.save()

            # clear the cart
        cart.clear()
        send_invoice_order.delay(order.id) #launchinf async task
        request.session['order_id'] = order.id
        return redirect(reverse('payments:process'))  
    return render(request, "orders/order_summary.html", {'address_form': address_form, 'cart': cart, 'addresses': addresses, 'modal': modal})


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
