from django.contrib import admin
from .models import Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration_days', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'start_date', 'end_date']
    list_filter = ['status', 'plan']
    search_fields = ['user__email', 'user__name']
    date_hierarchy = 'start_date'
