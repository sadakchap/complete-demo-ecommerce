from django import forms
from .models import Product

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'short_desc': forms.Textarea(),
        }
