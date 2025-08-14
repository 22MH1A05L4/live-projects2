"""
Views for loan-related API endpoints.
"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum, Q
from datetime import timedelta, date
from decimal import Decimal

from .models import Loan
from customers.models import Customer
from .serializers import (
    LoanEligibilitySerializer, LoanEligibilityResponseSerializer,
    LoanCreationSerializer, LoanCreationResponseSerializer,
    LoanDetailSerializer, CustomerLoanSerializer
)


def calculate_credit_score(customer):
    """
    Calculate credit score based on customer's loan history.
    Score ranges from 0-100.
    """
    loans = Loan.objects.filter(customer=customer)
    
    if not loans.exists():
        return 50  # Default score for new customers
    
    score = 0
    
    # Factor 1: Past loans paid on time (40 points max)
    total_emis = loans.aggregate(
        total_emis=Sum('tenure'),
        paid_on_time=Sum('emis_paid_on_time')
    )
    
    if total_emis['total_emis'] and total_emis['total_emis'] > 0:
        on_time_ratio = total_emis['paid_on_time'] / total_emis['total_emis']
        score += min(40, on_time_ratio * 40)
    
    # Factor 2: Number of past loans (20 points max, diminishing returns)
    loan_count = loans.count()
    if loan_count <= 5:
        score += loan_count * 4  # 4 points per loan up to 5 loans
    else:
        score += 20  # Max 20 points
    
    # Factor 3: Loan activity in current year (20 points max)
    current_year = timezone.now().year
    current_year_loans = loans.filter(start_date__year=current_year).count()
    score += min(20, current_year_loans * 5)
    
    # Factor 4: Loan approved volume vs limit (20 points max)
    current_loans = loans.filter(end_date__gte=timezone.now().date())
    total_current_amount = current_loans.aggregate(
        total=Sum('loan_amount')
    )['total'] or 0
    
    if customer.approved_limit > 0:
        utilization_ratio = float(total_current_amount) / customer.approved_limit
        if utilization_ratio <= 0.5:
            score += 20
        elif utilization_ratio <= 0.75:
            score += 10
        elif utilization_ratio < 1.0:
            score += 5
        else:
            score = 0  # Exceeds approved limit
    
    return min(100, max(0, int(score)))


def get_approval_decision(credit_score, customer, loan_amount, requested_rate, tenure):
    """
    Determine loan approval based on credit score and other factors.
    """
    # Check if sum of current loans exceeds approved limit
    current_loans = Loan.objects.filter(
        customer=customer,
        end_date__gte=timezone.now().date()
    )
    current_loan_sum = current_loans.aggregate(
        total=Sum('loan_amount')
    )['total'] or 0
    
    if current_loan_sum + loan_amount > customer.approved_limit:
        return False, requested_rate, "Loan amount exceeds approved limit"
    
    # Credit score based approval
    if credit_score > 50:
        min_interest = 10.0
        approved = True
    elif credit_score > 30:
        min_interest = 12.0
        approved = True
    elif credit_score > 10:
        min_interest = 16.0
        approved = True
    else:
        return False, requested_rate, "Credit score too low"
    
    # Check EMI affordability (should not exceed 50% of monthly salary)
    corrected_rate = max(float(requested_rate), min_interest)
    monthly_emi = Loan.calculate_emi(loan_amount, corrected_rate, tenure)
    
    current_emis = current_loans.aggregate(
        total_emi=Sum('monthly_repayment')
    )['total_emi'] or 0
    
    total_emi = monthly_emi + float(current_emis)
    
    if total_emi > (customer.monthly_salary * 0.5):
        return False, corrected_rate, "EMI exceeds 50% of monthly salary"
    
    return approved, corrected_rate, "Approved"


@api_view(['POST'])
def check_eligibility(request):
    """
    Check loan eligibility for a customer.
    """
    serializer = LoanEligibilitySerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    customer_id = data['customer_id']
    loan_amount = data['loan_amount']
    interest_rate = data['interest_rate']
    tenure = data['tenure']
    
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response(
            {"error": "Customer not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Calculate credit score
    credit_score = calculate_credit_score(customer)
    
    # Get approval decision
    approval, corrected_rate, message = get_approval_decision(
        credit_score, customer, loan_amount, interest_rate, tenure
    )
    
    # Calculate monthly installment
    monthly_installment = Loan.calculate_emi(loan_amount, corrected_rate, tenure)
    
    response_data = {
        'customer_id': customer_id,
        'approval': approval,
        'interest_rate': float(interest_rate),
        'corrected_interest_rate': corrected_rate,
        'tenure': tenure,
        'monthly_installment': monthly_installment
    }
    
    if not approval:
        response_data['message'] = message
    
    response_serializer = LoanEligibilityResponseSerializer(data=response_data)
    if response_serializer.is_valid():
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    return Response(response_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_loan(request):
    """
    Create a new loan if eligible.
    """
    serializer = LoanCreationSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    customer_id = data['customer_id']
    loan_amount = data['loan_amount']
    interest_rate = data['interest_rate']
    tenure = data['tenure']
    
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response(
            {"error": "Customer not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check eligibility
    credit_score = calculate_credit_score(customer)
    approval, corrected_rate, message = get_approval_decision(
        credit_score, customer, loan_amount, interest_rate, tenure
    )
    
    if approval:
        # Create the loan
        monthly_installment = Loan.calculate_emi(loan_amount, corrected_rate, tenure)
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=tenure * 30)  # Approximate
        
        loan = Loan.objects.create(
            customer=customer,
            loan_amount=loan_amount,
            tenure=tenure,
            interest_rate=Decimal(str(corrected_rate)),
            monthly_repayment=Decimal(str(monthly_installment)),
            start_date=start_date,
            end_date=end_date
        )
        
        response_data = {
            'loan_id': loan.loan_id,
            'customer_id': customer_id,
            'loan_approved': True,
            'message': 'Loan approved successfully',
            'monthly_installment': monthly_installment
        }
    else:
        response_data = {
            'loan_id': None,
            'customer_id': customer_id,
            'loan_approved': False,
            'message': message
        }
    
    response_serializer = LoanCreationResponseSerializer(data=response_data)
    if response_serializer.is_valid():
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    return Response(response_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def view_loan(request, loan_id):
    """
    View loan details with customer information.
    """
    loan = get_object_or_404(Loan, loan_id=loan_id)
    serializer = LoanDetailSerializer(loan)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def view_customer_loans(request, customer_id):
    """
    View all current loans for a customer.
    """
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response(
            {"error": "Customer not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get current loans (end_date >= today)
    current_loans = Loan.objects.filter(
        customer=customer,
        end_date__gte=timezone.now().date()
    )
    
    serializer = CustomerLoanSerializer(current_loans, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)