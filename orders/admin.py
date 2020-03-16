from django.contrib import admin
from .models import Order, OrderItem

# Register your models here.

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 4

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id','user', 'created', 'updated', 'paid']
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]
