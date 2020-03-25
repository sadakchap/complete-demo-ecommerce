from django.db import models
from products.models import Product
from accounts.models import UserAddress
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from coupons.models import Coupon

# Create your models here.

User = get_user_model()

class Order(models.Model):
    user        = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE, null=True)
    address     = models.ForeignKey(UserAddress, related_name="orders", on_delete=models.CASCADE)
    created     = models.DateTimeField(auto_now_add=True)
    updated     = models.DateTimeField(auto_now=True)
    paid        = models.BooleanField(default=False)
    paytm_txn_id= models.CharField(max_length=255, blank=True, null=True)
    coupon      = models.ForeignKey(Coupon, related_name='orders', null=True, blank=True, on_delete=models.SET_NULL)
    discount    = models.IntegerField(default=0, validators=[MinValueValidator(5), MaxValueValidator(100)])

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

class OrderItem(models.Model):
    order   = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="order_items", on_delete=models.CASCADE)
    price   = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f'{self.id}'
    
    def get_cost(self):
        return self.price * self.quantity
