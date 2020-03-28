from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Category, Product
from cart.forms import CartAddProductForm

# Create your views here.
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

    paginator = Paginator(products, 2)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    return render(request, 'products/product_list.html', {
        'products': products,
        'category': category,
        'categories': categories
    })

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug)
    cart_form = CartAddProductForm()
    return render(request, 'products/product_detail.html', {
        'product': product,
        'cart_form': cart_form,
    })
