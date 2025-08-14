"""
Admin configuration for customers app.
"""
from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['customer_id', 'first_name', 'last_name', 'phone_number', 'age', 'monthly_salary', 'approved_limit']
    list_filter = ['age', 'created_at']
    search_fields = ['first_name', 'last_name', 'phone_number']
    readonly_fields = ['customer_id', 'created_at', 'updated_at']
    ordering = ['-created_at']