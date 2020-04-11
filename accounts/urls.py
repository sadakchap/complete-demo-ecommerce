from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('activate/<uid>/<token>/', views.activate, name='activate'),
    path('myaddress/', views.list_user_address, name='address_list'),
    path('address/create/', views.add_user_address, name='address_create'),
    path('address/edit/<int:adr_id>/', views.edit_user_address, name='address_edit'),
    path('address/delete/<int:adr_id>/', views.delete_user_address, name='address_delete'),
    path('address/delete/ajax/', views.delete_user_address_ajax, name='address_delete_ajax'),
]