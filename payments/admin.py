from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'phone_number', 'amount', 'status', 'mpesa_receipt', 'created_at']
    list_filter = ['status']
    search_fields = ['phone_number', 'mpesa_receipt', 'order__id']