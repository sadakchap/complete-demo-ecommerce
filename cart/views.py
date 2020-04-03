from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from products.models import Product
from .cart import Cart
from .forms import CartAddProductForm
from coupons.forms import CouponForm

# Create your views here.

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add( product=product, quantity=cd['quantity'], update_quantity=cd['update'])
    return redirect('cart:cart_detail')

@login_required
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'update': True
        })
    coupon_form = CouponForm()
    return render(request, "cart/cart_detail.html", {'cart': cart, 'coupon_form': coupon_form})


def cart_add_ajax(request, product_id):
    data = {}
    cart = Cart(request)
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        product = None
    
    if product:
        update_quan = cart.item_in_cart(product_id)
        item_quan = cart.item_quantity_in_cart(product_id)
        quantity = 1+item_quan
        cart.add(product=product,
                 quantity=quantity, update_quantity=update_quan)
        data['added'] = 'ok'
    
    data['added_item'] = {
        'cart_item_product_id': str(product.id),
        'product_name': str(product.name),
        'product_url': str(product.get_absolute_url()),
        'product_image_url': str(product.image.url),
        'quantity': str(quantity),
        'price': str(product.price)
    }
    data['cart_total'] = str(cart.get_total_price())
    data['cart_length'] = str(len(cart))
    return JsonResponse(data, safe=False)
