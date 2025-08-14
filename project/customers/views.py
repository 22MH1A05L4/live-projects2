"""
Views for customer-related API endpoints.
"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Customer
from .serializers import CustomerRegistrationSerializer, CustomerResponseSerializer


@api_view(['POST'])
def register_customer(request):
    """
    Register a new customer.
    
    Expected request format:
    {
        "first_name": "string",
        "last_name": "string",
        "age": 30,
        "monthly_income": 50000,
        "phone_number": "9000000000"
    }
    """
    serializer = CustomerRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        customer = serializer.save()
        response_serializer = CustomerResponseSerializer(customer)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)