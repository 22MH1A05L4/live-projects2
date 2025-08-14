"""
Loan models for the credit approval system.
"""
from django.db import models
from customers.models import Customer
from decimal import Decimal
import math


class Loan(models.Model):
    """
    Loan model representing a customer's loan.
    """
    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loans')
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tenure = models.IntegerField()  # in months
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    monthly_repayment = models.DecimalField(max_digits=12, decimal_places=2)
    emis_paid_on_time = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'loans'
        ordering = ['-created_at']

    def __str__(self):
        return f"Loan {self.loan_id} - {self.customer.full_name}"

    @staticmethod
    def calculate_emi(principal, annual_rate, tenure_months):
        """
        Calculate EMI using compound interest formula.
        EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
        """
        if annual_rate == 0:
            return float(principal) / tenure_months
        
        monthly_rate = float(annual_rate) / 12 / 100
        emi = float(principal) * monthly_rate * (1 + monthly_rate) ** tenure_months / ((1 + monthly_rate) ** tenure_months - 1)
        return round(emi, 2)

    @property
    def repayments_left(self):
        """Calculate remaining EMIs."""
        return max(0, self.tenure - self.emis_paid_on_time)

    def is_current_loan(self):
        """Check if loan is currently active."""
        from django.utils import timezone
        return self.end_date >= timezone.now().date()