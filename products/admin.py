from django.contrib import admin
from .models import Category, Product, ProductImageSet
from tinymce.widgets import TinyMCE
from django.db import models
# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {
        'slug': ('name', )
    }


class ProductImageSetInline(admin.TabularInline):
    model = ProductImageSet
    extra = 4

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'discount_percent','brand', 'featured', 'stock', 'updated']
    list_filter = ['featured', 'created', 'updated']
    list_editable = ['price', 'discount_percent', 'featured', 'stock']
    prepopulated_fields = {
        'slug': ('name', )
    }
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }
    inlines = [
        ProductImageSetInline,
    ]
    
admin.site.register(ProductImageSet)
