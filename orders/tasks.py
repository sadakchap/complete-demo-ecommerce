from django.conf import settings
from django.core.mail import send_mail
from .models import Order
from celery import task

@task
def send_invoice_order(order_id):
    order = Order.objects.get(id=order_id)
    subject = f'Order no. {order.id}'
    user = order.user
    message = f'Dear {user.first_name}, \n\nYou have successfully placed an order.\n Your order id is {order.id}'
    mail_sent = send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
    return mail_sent

