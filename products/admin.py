from django.contrib import admin
from .models import Category, Product
from tinymce.widgets import TinyMCE
from django.db import models
# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {
        'slug': ('name', )
    }


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'created', 'updated']
    list_filter  = ['created', 'updated']
    list_editable = ['price', 'stock']
    prepopulated_fields = {
        'slug': ('name', )
    }
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }
