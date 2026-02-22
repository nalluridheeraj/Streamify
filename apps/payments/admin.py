from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'status', 'payment_method', 'payment_date']
    list_filter = ['status', 'payment_method']
    search_fields = ['user__email', 'transaction_id']
    date_hierarchy = 'payment_date'
    readonly_fields = ['payment_date']
