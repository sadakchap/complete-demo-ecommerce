from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('process/', views.payment_process, name='process'),
    path('handle-response', views.handle_paytm_response, name='handle-response'),
    path('done/<int:order_id>/', views.payment_done, name='done'),
    path('cancel/<str:resp_msg>/', views.payment_cancel, name='cancel'),
]   
