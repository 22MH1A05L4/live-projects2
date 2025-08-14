"""
Celery tasks for data ingestion.
"""
import pandas as pd
import os
from datetime import datetime
from decimal import Decimal
from celery import shared_task
from django.conf import settings
from customers.models import Customer
from loans.models import Loan


@shared_task
def ingest_customer_data():
    """
    Ingest customer data from Excel file.
    """
    try:
        # Look for customer data file in the project root
        file_path = os.path.join(settings.BASE_DIR, 'customer_data.xlsx')
        
        if not os.path.exists(file_path):
            return {"status": "error", "message": "Customer data file not found"}
        
        # Read Excel file
        df = pd.read_excel(file_path)
        
        customers_created = 0
        customers_updated = 0
        
        for _, row in df.iterrows():
            customer_id = row.get('Customer ID')
            first_name = row.get('First Name', '')
            last_name = row.get('Last Name', '')
            phone_number = str(row.get('Phone Number', ''))
            age = int(row.get('Age', 0))
            monthly_salary = int(row.get('Monthly Salary', 0))
            approved_limit = int(row.get('Approved Limit', 0))
            current_debt = int(row.get('Current Debt', 0))
            
            # Create or update customer
            customer, created = Customer.objects.update_or_create(
                customer_id=customer_id,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone_number': phone_number,
                    'age': age,
                    'monthly_salary': monthly_salary,
                    'approved_limit': approved_limit,
                    'current_debt': current_debt,
                }
            )
            
            if created:
                customers_created += 1
            else:
                customers_updated += 1
        
        return {
            "status": "success",
            "customers_created": customers_created,
            "customers_updated": customers_updated,
            "total_processed": len(df)
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@shared_task
def ingest_loan_data():
    """
    Ingest loan data from Excel file.
    """
    try:
        # Look for loan data file in the project root
        file_path = os.path.join(settings.BASE_DIR, 'loan_data.xlsx')
        
        if not os.path.exists(file_path):
            return {"status": "error", "message": "Loan data file not found"}
        
        # Read Excel file
        df = pd.read_excel(file_path)
        
        loans_created = 0
        loans_updated = 0
        
        for _, row in df.iterrows():
            customer_id = row.get('Customer ID')
            loan_id = row.get('Loan ID')
            loan_amount = Decimal(str(row.get('Loan Amount', 0)))
            tenure = int(row.get('Tenure', 0))
            interest_rate = Decimal(str(row.get('Interest Rate', 0)))
            monthly_payment = Decimal(str(row.get('Monthly payment', 0)))
            emis_paid_on_time = int(row.get('EMIs paid on Time', 0))
            
            # Parse dates
            date_of_approval = row.get('Date of Approval')
            end_date = row.get('End Date')
            
            # Convert date strings to date objects
            if isinstance(date_of_approval, str):
                start_date = datetime.strptime(date_of_approval, '%d-%m-%Y').date()
            else:
                start_date = date_of_approval
                
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%d-%m-%Y').date()
            
            try:
                customer = Customer.objects.get(customer_id=customer_id)
                
                # Create or update loan
                loan, created = Loan.objects.update_or_create(
                    loan_id=loan_id,
                    defaults={
                        'customer': customer,
                        'loan_amount': loan_amount,
                        'tenure': tenure,
                        'interest_rate': interest_rate,
                        'monthly_repayment': monthly_payment,
                        'emis_paid_on_time': emis_paid_on_time,
                        'start_date': start_date,
                        'end_date': end_date,
                    }
                )
                
                if created:
                    loans_created += 1
                else:
                    loans_updated += 1
                    
            except Customer.DoesNotExist:
                print(f"Customer with ID {customer_id} not found for loan {loan_id}")
                continue
        
        return {
            "status": "success",
            "loans_created": loans_created,
            "loans_updated": loans_updated,
            "total_processed": len(df)
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


@shared_task
def ingest_initial_data():
    """
    Ingest both customer and loan data.
    """
    # First ingest customers
    customer_result = ingest_customer_data()
    
    # Then ingest loans
    loan_result = ingest_loan_data()
    
    return {
        "customer_ingestion": customer_result,
        "loan_ingestion": loan_result
    }