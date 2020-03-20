from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_POST
from django.conf import settings
from django.urls import reverse

from orders.models import Order
from .paytm import Checksum

# Create your views here.

def payment_process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    params = {
        "MID": settings.PAYMENT_MERCHANT_ID,
        "ORDER_ID": str(order.id),
        "CUST_ID": str(order.user.email),
        "TXN_AMOUNT": str(order.get_total_cost()),
        "CHANNEL_ID": "WEB",
        "INDUSTRY_TYPE_ID": "Retail",
        "WEBSITE": "WEBSTAGING",
        "CALLBACK_URL": request.build_absolute_uri(reverse('payments:handle-response'))
    }
    params['CHECKSUMHASH'] = Checksum.generate_checksum(params, settings.PAYMENT_MERCHANT_KEY)
    
    return render(request, "payments/paytm.html", {'params': params, 'order': order})


# payment will send a POST request on our website
@csrf_exempt
def handle_paytm_response(request):
    if request.method == "POST":
        order_id = request.POST.get("ORDERID")
        order = get_object_or_404(Order, id=order_id)

        response_dict = {}
        for key in request.POST.keys():
            response_dict[key] = request.POST.get(key)
            if key == "CHECKSUMHASH":
                checksum = response_dict[key]

        verify = Checksum.verify_checksum(response_dict, settings.PAYMENT_MERCHANT_KEY, checksum)

        if verify:
            if response_dict['RESPCODE'] == '01':
                # update order
                order.paid = True
                order.paytm_txn_id = response_dict.get("TXNID")
                order.save()
                return redirect('payments:done', order_id=order.id)
            else:
                return redirect('payments:cancel', resp_msg=response_dict['RESPMSG'])
        else:
            print("order unsuccessful because "+response_dict['RESPMSG'])
            return redirect('payments:cancel', resp_msg=response_dict['RESPMSG'])


def payment_done(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "payments/done.html", {'order': order})


def payment_cancel(request, resp_msg=None):
    return render(request, "payments/cancel.html", {'resp_msg': resp_msg})
