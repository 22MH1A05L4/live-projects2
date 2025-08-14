"""
Customer models for the credit approval system.
"""
from django.db import models


class Customer(models.Model):
    """
    Customer model representing a loan applicant.
    """
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    age = models.IntegerField()
    monthly_salary = models.IntegerField()
    approved_limit = models.IntegerField()
    current_debt = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customers'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        """Return the customer's full name."""
        return f"{self.first_name} {self.last_name}"