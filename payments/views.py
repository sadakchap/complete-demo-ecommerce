from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from io import BytesIO
import weasyprint
from django.core.mail import EmailMessage

from orders.models import Order
from .paytm import Checksum

# Create your views here.

@login_required
def payment_process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, paytm_order_id=order_id)
    params = {
        "MID": settings.PAYMENT_MERCHANT_ID,
        "ORDER_ID": str(order_id),
        "CUST_ID": str(order.user.email),
        # "TXN_AMOUNT": str(order.get_total_cost()), # "%.2f" % order.get_total_cost()
        "TXN_AMOUNT": "%.2f" % order.get_total_cost_after_discount(),
        "CHANNEL_ID": "WEB",
        "INDUSTRY_TYPE_ID": "Retail",
        "WEBSITE": "WEBSTAGING",
        "CALLBACK_URL": request.build_absolute_uri(reverse('payments:handle-response'))
    }
    params['CHECKSUMHASH'] = Checksum.generate_checksum(params, settings.PAYMENT_MERCHANT_KEY)
    return render(request, "payments/paytm.html", {'params': params, 'order': order})


# paytm will send a POST request on our website
@csrf_exempt
def handle_paytm_response(request):
    context = {
        'success': False,
    }
    if request.method == "POST":
        order_id = request.POST.get("ORDERID")
        order = get_object_or_404(Order, paytm_order_id=order_id)

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
                #sending invoice via email
                sub = f'Maa Shop- Invoice no- {order.id}'
                msg = 'Please, find attached the invoice for your recent purchase.'
                email = EmailMessage(sub, msg, settings.EMAIL_HOST_USER, [order.user.email])
                # generate pdf
                html = render_to_string('orders/order_invoice.html', {'order': order})
                out = BytesIO()
                weasyprint.HTML(string=html).write_pdf(out, stylesheets=[
                    weasyprint.CSS(settings.STATIC_ROOT +
                                   '\\' + 'css/order_invoice.css')
                ])
                #attach pdf file to email
                email.attach(f'order_{order.id}.pdf', out.getvalue(), 'application/pdf')
                # send email
                email.send()
                context['success'] = True
            else:
                context['success'] = False
        else:
            return redirect('payments:cancel', resp_msg=response_dict['RESPMSG'])
        context['resp_dict'] = response_dict
        context['order'] = order
    return render(request, "payments/payment_status.html", context=context)

@login_required
def payment_done(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "payments/done.html", {'order': order})

@login_required
def payment_cancel(request, resp_msg=None):
    return render(request, "payments/cancel.html", {'resp_msg': resp_msg})
