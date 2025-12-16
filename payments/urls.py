from django.urls import path
from . import views

urlpatterns = [
    path('initiate/<int:order_id>/', views.initiate_payment, name='initiate_payment'),
    path('stk-push/<int:payment_id>/', views.trigger_stk_push, name='stk_push'),
    path('status/<int:payment_id>/', views.payment_status, name='payment_status'),
    path('callback/', views.mpesa_callback, name='mpesa_callback'),
    path('manual-confirm/<int:payment_id>/', views.manual_confirm_payment, name='manual_confirm'),
]