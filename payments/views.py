from django.shortcuts import render, HttpResponse, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
# Create your views here.

# payment will send a POST request on our website
@csrf_exempt
def payment_process(request):
    # set order to paid
    if request.method == 'POST':
        print(request.POST)
        order_id = request.POST.get('ORDERID')
        order = get_object_or_404(Order, id=order_id)
        # set order.paid=True
        return HttpResponse('<h1>D one </h1>')


def payment_done(request):
    pass


def payment_cancel(request):
    pass
