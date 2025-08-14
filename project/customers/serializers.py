"""
Serializers for customer-related API endpoints.
"""
from rest_framework import serializers
from .models import Customer


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for customer registration.
    """
    monthly_income = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'age', 'monthly_income', 'phone_number']
    
    def create(self, validated_data):
        """
        Create a new customer with calculated approved limit.
        """
        monthly_income = validated_data.pop('monthly_income')
        
        # Calculate approved limit: round to nearest lakh (100,000)
        approved_limit = round(36 * monthly_income, -5)
        
        customer = Customer.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            age=validated_data['age'],
            phone_number=validated_data['phone_number'],
            monthly_salary=monthly_income,
            approved_limit=approved_limit,
            current_debt=0
        )
        
        return customer


class CustomerResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for customer registration response.
    """
    name = serializers.CharField(source='full_name', read_only=True)
    monthly_income = serializers.IntegerField(source='monthly_salary', read_only=True)
    
    class Meta:
        model = Customer
        fields = ['customer_id', 'name', 'age', 'monthly_income', 'approved_limit', 'phone_number']


class CustomerMiniProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for customer mini profile in loan details.
    """
    class Meta:
        model = Customer
        fields = ['customer_id', 'first_name', 'last_name', 'phone_number', 'age']