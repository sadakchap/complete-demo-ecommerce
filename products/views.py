from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

import json

from .models import Category, Product
from cart.forms import CartAddProductForm
from orders.decorators import no_active_order_msg

# Create your views here.

@no_active_order_msg
def home_view(request):
    product_list = Product.objects.order_by('-discount_percent')
    products_on_sale = [prod for prod in product_list if prod.discount_percent]
    featured_products = Product.objects.filter(featured=True)
    return render(request, "index.html", context={
        'products_on_sale': products_on_sale[:8],
        'featured_products': featured_products[:8],
    })
    
@no_active_order_msg
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.order_by('-created')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    query = request.GET.get('q')
    if query:
        query_set = query.split()
        for query in query_set:
            products = products.filter(
                Q(name__icontains=query) | 
                Q(desc__icontains=query) | 
                Q(category__name__icontains=query)
            ).distinct()

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    return render(request, 'products/product_list.html', {
        'products': products,
        'category': category,
        'categories': categories
    })

@no_active_order_msg
def product_detail(request, id, slug):
    featured_products = Product.objects.filter(featured=True)
    product = get_object_or_404(Product, id=id, slug=slug)
    cart_form = CartAddProductForm()
    return render(request, 'products/product_detail.html', {
        'product': product,
        'cart_form': cart_form,
        'featured_products': featured_products[:8],
    })


def product_quick_detail_ajax(request, product_id):
    data = {}
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        data['status'] = 'ko'
        data['error_message'] = 'Product does not exist!'
        return JsonResponse(data, safe=False)
    if product:
        data['status'] = 'ok'
        data['item'] = {
            'product_id': str(product.id),
            'product_name': str(product.name),
            'product_image_url': str(product.image.url),
            # 'product_review': str(product.get_review()),
            'product_short_desc': str(product.short_desc),
            'product_current_price': str(product.get_price()),
            'product_original_price': str(product.price),
        }
        product_image_list = []
        for img in product.image_set.all():
            product_image_list.append(img.image.url)
        data['product_image_list'] = json.dumps(product_image_list)
        return JsonResponse(data, safe=False)
