from django.contrib import admin
from .models import Order, OrderItem
from django.urls import reverse
from django.utils.safestring import mark_safe

def order_detail(obj):
    reversed_url = reverse('orders:admin_order_detail', args=[obj.id] )
    return mark_safe(f'<a href="{reversed_url}">VIEW</a>')

def order_pdf(obj):
    reversed_url = reverse('orders:admin_order_pdf', args=[obj.id] )
    return mark_safe(f'<a href="{reversed_url}">PDF</a>')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 4

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'paid', 'full_name', 'email_id','get_address', 'get_phone','created', order_detail, order_pdf]
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]
    list_display_links = None

    def full_name(self, obj):
        return obj.address.full_name
    full_name.short_description = 'full_name'

    def email_id(self, obj):
        return obj.user.email
    email_id.short_description = 'email'

    def get_address(self, obj):
        return obj.address.city +', '+ obj.address.state
    get_address.short_description='address'

    def get_phone(self, obj):
        return obj.address.phone
    get_address.short_description = 'phone'
