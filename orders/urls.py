from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('summary/', views.order_summary, name='order_summary'),
    path('create/<int:adr_id>', views.order_create, name='order_create'),
    path('admin/order/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('admin/order/<int:order_id>/pdf/', views.admin_order_pdf, name='admin_order_pdf'),
    # path('created/', views.order_created, name='order_created'),
]