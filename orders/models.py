from django.db import models
from products.models import Product
from accounts.models import UserAddress
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from coupons.models import Coupon

from uuid import uuid4

# Create your models here.

User = get_user_model()

class Order(models.Model):
    user        = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE, null=True)
    address     = models.ForeignKey(UserAddress, related_name="orders", on_delete=models.CASCADE)
    created     = models.DateTimeField(auto_now_add=True)
    updated     = models.DateTimeField(auto_now=True)
    paid        = models.BooleanField(default=False)
    coupon      = models.ForeignKey(Coupon, related_name='orders', null=True, blank=True, on_delete=models.SET_NULL)
    discount    = models.IntegerField(default=0, validators=[MinValueValidator(5), MaxValueValidator(100)])
    paytm_txn_id= models.CharField(max_length=255, blank=True, null=True)
    paytm_order_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ('-created',)
    
    def __str__(self):
        return f'Order no {self.id} from {self.address.full_name}'
    
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())
    
    def get_discount(self):
        total_cost = self.get_total_cost()
        return total_cost * (self.discount / Decimal('100'))

    def get_total_cost_after_discount(self):
        total_cost = self.get_total_cost()
        disc = self.get_discount() if self.coupon else 0
        return total_cost - disc

    def set_unique_paytm_order_id(self):
        ord_id = uuid4().hex
        if not Order.objects.filter(paytm_order_id=ord_id).exists():
            self.paytm_order_id = ord_id
            self.save()
            return self.paytm_order_id
        return self.set_unique_paytm_order_id()
        
    
    def get_unqiue_paytm_order_id(self):
        return self.paytm_order_id

class OrderItem(models.Model):
    order   = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="order_items", on_delete=models.CASCADE)
    price   = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f'{self.id}'
    
    def get_cost(self):
        return self.price * self.quantity
