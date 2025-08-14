"""
Management command to ingest initial data from Excel files.
"""
from django.core.management.base import BaseCommand
from ingestion.tasks import ingest_initial_data


class Command(BaseCommand):
    help = 'Ingest initial customer and loan data from Excel files'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting data ingestion...')
        )
        
        # Run the ingestion task
        result = ingest_initial_data()
        
        # Display results
        customer_result = result.get('customer_ingestion', {})
        loan_result = result.get('loan_ingestion', {})
        
        if customer_result.get('status') == 'success':
            self.stdout.write(
                self.style.SUCCESS(
                    f"Customer data ingestion completed: "
                    f"{customer_result.get('customers_created', 0)} created, "
                    f"{customer_result.get('customers_updated', 0)} updated"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"Customer data ingestion failed: {customer_result.get('message', 'Unknown error')}"
                )
            )
        
        if loan_result.get('status') == 'success':
            self.stdout.write(
                self.style.SUCCESS(
                    f"Loan data ingestion completed: "
                    f"{loan_result.get('loans_created', 0)} created, "
                    f"{loan_result.get('loans_updated', 0)} updated"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"Loan data ingestion failed: {loan_result.get('message', 'Unknown error')}"
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS('Data ingestion process completed!')
        )