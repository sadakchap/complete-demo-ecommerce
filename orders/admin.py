from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 4

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email_id','get_address', 'get_phone','created', 'updated', 'paid']
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]

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
