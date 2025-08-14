"""
Serializers for loan-related API endpoints.
"""
from rest_framework import serializers
from .models import Loan
from customers.models import Customer
from customers.serializers import CustomerMiniProfileSerializer
from django.utils import timezone
from datetime import timedelta


class LoanEligibilitySerializer(serializers.Serializer):
    """
    Serializer for loan eligibility check request.
    """
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField()


class LoanEligibilityResponseSerializer(serializers.Serializer):
    """
    Serializer for loan eligibility check response.
    """
    customer_id = serializers.IntegerField()
    approval = serializers.BooleanField()
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    corrected_interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField()
    monthly_installment = serializers.DecimalField(max_digits=12, decimal_places=2)
    message = serializers.CharField(required=False)


class LoanCreationSerializer(serializers.Serializer):
    """
    Serializer for loan creation request.
    """
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField()


class LoanCreationResponseSerializer(serializers.Serializer):
    """
    Serializer for loan creation response.
    """
    loan_id = serializers.IntegerField(allow_null=True)
    customer_id = serializers.IntegerField()
    loan_approved = serializers.BooleanField()
    message = serializers.CharField()
    monthly_installment = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)


class LoanDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for loan details with customer info.
    """
    customer = CustomerMiniProfileSerializer(read_only=True)
    
    class Meta:
        model = Loan
        fields = ['loan_id', 'customer', 'loan_amount', 'interest_rate', 
                 'monthly_repayment', 'tenure', 'start_date', 'end_date']


class CustomerLoanSerializer(serializers.ModelSerializer):
    """
    Serializer for customer's current loans.
    """
    monthly_installment = serializers.DecimalField(source='monthly_repayment', max_digits=12, decimal_places=2)
    repayments_left = serializers.IntegerField()
    
    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_installment', 'repayments_left']