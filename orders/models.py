from django.db import models
from products.models import Product
from accounts.models import UserAddress
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()

class Order(models.Model):
    user        = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE, null=True)
    address     = models.ForeignKey(UserAddress, related_name="orders", on_delete=models.CASCADE)
    created     = models.DateTimeField(auto_now_add=True)
    updated     = models.DateTimeField(auto_now=True)
    paid        = models.BooleanField(default=False)
    paytm_txn_id= models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ('-created',)
    
    def __str__(self):
        return f'Order no {self.id} from {self.address.full_name}'
    
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order   = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="order_items", on_delete=models.CASCADE)
    price   = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f'{self.id}'
    
    def get_cost(self):
        return self.price * self.quantity
