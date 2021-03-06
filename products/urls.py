from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products-by-category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('products/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('product-detail/ajax/<int:product_id>/', views.product_quick_detail_ajax,name='product_quick_detail_ajax')
]
