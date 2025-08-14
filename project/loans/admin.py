"""
Admin configuration for loans app.
"""
from django.contrib import admin
from .models import Loan


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['loan_id', 'customer', 'loan_amount', 'interest_rate', 'tenure', 'start_date', 'end_date']
    list_filter = ['interest_rate', 'tenure', 'start_date', 'end_date']
    search_fields = ['customer__first_name', 'customer__last_name', 'loan_id']
    readonly_fields = ['loan_id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer')