# Credit Approval System

A comprehensive backend application for credit approval system built with Django, PostgreSQL, Celery, and Redis. The system provides APIs for customer registration, loan eligibility checking, loan creation, and loan management.

## Features

- **Customer Management**: Register new customers with automatic credit limit calculation
- **Loan Eligibility**: Check loan eligibility based on credit scoring algorithm
- **Loan Management**: Create, view, and manage loans
- **Data Ingestion**: Background processing of Excel data using Celery
- **Credit Scoring**: Advanced algorithm considering payment history, loan activity, and utilization
- **Dockerized**: Complete Docker setup for easy deployment

## Tech Stack

- **Backend**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL 14
- **Task Queue**: Celery with Redis broker
- **Containerization**: Docker & Docker Compose
- **Data Processing**: Pandas for Excel file processing

## Project Structure

```
credit-approval-system/
├── credit_core/           # Django project settings
├── customers/             # Customer management app
├── loans/                 # Loan management app
├── ingestion/             # Data ingestion app with Celery tasks
├── customer_data.xlsx     # Sample customer data
├── loan_data.xlsx         # Sample loan data
├── docker-compose.yml     # Docker services configuration
├── Dockerfile            # Application container
├── requirements.txt      # Python dependencies
└── README.md
```

## API Endpoints

### 1. Customer Registration
**POST** `/register`

Register a new customer with automatic credit limit calculation.

**Request:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "age": 30,
  "monthly_income": 50000,
  "phone_number": "9000000000"
}
```

**Response:**
```json
{
  "customer_id": 1,
  "name": "John Doe",
  "age": 30,
  "monthly_income": 50000,
  "approved_limit": 1800000,
  "phone_number": "9000000000"
}
```

### 2. Check Loan Eligibility
**POST** `/check-eligibility`

Check if a customer is eligible for a loan based on credit scoring.

**Request:**
```json
{
  "customer_id": 1,
  "loan_amount": 500000,
  "interest_rate": 10.5,
  "tenure": 24
}
```

**Response:**
```json
{
  "customer_id": 1,
  "approval": true,
  "interest_rate": 10.5,
  "corrected_interest_rate": 12.0,
  "tenure": 24,
  "monthly_installment": 23500.45
}
```

### 3. Create Loan
**POST** `/create-loan`

Create a new loan if the customer is eligible.

**Request:**
```json
{
  "customer_id": 1,
  "loan_amount": 500000,
  "interest_rate": 12.0,
  "tenure": 24
}
```

**Response:**
```json
{
  "loan_id": 1001,
  "customer_id": 1,
  "loan_approved": true,
  "message": "Loan approved successfully",
  "monthly_installment": 23500.45
}
```

### 4. View Loan Details
**GET** `/view-loan/{loan_id}`

Get detailed information about a specific loan.

**Response:**
```json
{
  "loan_id": 1001,
  "customer": {
    "customer_id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "9000000000",
    "age": 30
  },
  "loan_amount": "500000.00",
  "interest_rate": "12.00",
  "monthly_repayment": "23500.45",
  "tenure": 24,
  "start_date": "2023-01-01",
  "end_date": "2025-01-01"
}
```

### 5. View Customer Loans
**GET** `/view-loans/{customer_id}`

Get all current loans for a specific customer.

**Response:**
```json
[
  {
    "loan_id": 1001,
    "loan_amount": "500000.00",
    "interest_rate": "12.00",
    "monthly_installment": "23500.45",
    "repayments_left": 4
  }
]
```

## Credit Scoring Algorithm

The system uses a comprehensive credit scoring algorithm (0-100 scale) based on:

1. **Payment History (40 points)**: Ratio of EMIs paid on time
2. **Number of Past Loans (20 points)**: Credit experience with diminishing returns
3. **Current Year Activity (20 points)**: Recent loan activity
4. **Credit Utilization (20 points)**: Current loans vs approved limit

### Approval Rules

- **Score > 50**: Approve at requested rate (minimum 10%)
- **Score 30-50**: Approve at minimum 12% interest
- **Score 10-30**: Approve at minimum 16% interest  
- **Score ≤ 10**: Reject loan
- **EMI > 50% of salary**: Reject regardless of score

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- Git for cloning the repository

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd credit-approval-system
```

2. **Copy environment file**
```bash
cp .env.example .env
```

3. **Build and start services**
```bash
docker-compose up --build
```

4. **Run database migrations**
```bash
docker-compose exec web python manage.py migrate
```

5. **Ingest initial data**
```bash
docker-compose exec web python manage.py ingest_initial_data
```

6. **Create superuser (optional)**
```bash
docker-compose exec web python manage.py createsuperuser
```

The application will be available at `http://localhost:8000`

### Services

- **Web Application**: http://localhost:8000
- **PostgreSQL Database**: localhost:5432
- **Redis**: localhost:6379
- **Django Admin**: http://localhost:8000/admin

## Data Ingestion

The system includes automated data ingestion from Excel files:

- **customer_data.xlsx**: Customer information
- **loan_data.xlsx**: Historical loan data

### Manual Data Ingestion

```bash
# Ingest both customer and loan data
docker-compose exec web python manage.py ingest_initial_data

# Or use Celery tasks directly in Django shell
docker-compose exec web python manage.py shell
>>> from ingestion.tasks import ingest_initial_data
>>> result = ingest_initial_data()
>>> print(result)
```

## Development

### Running Tests

```bash
docker-compose exec web python manage.py test
```

### Accessing Django Shell

```bash
docker-compose exec web python manage.py shell
```

### Viewing Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs web
docker-compose logs worker
docker-compose logs db
```

## Production Deployment

### Environment Variables

Update the `.env` file with production values:

```env
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_PASSWORD=strong-database-password
```

### Security Considerations

1. Change the default SECRET_KEY
2. Set DEBUG=False in production
3. Use strong database passwords
4. Configure proper ALLOWED_HOSTS
5. Set up SSL/TLS certificates
6. Configure firewall rules

### Scaling

- **Database**: Use managed PostgreSQL service (AWS RDS, Google Cloud SQL)
- **Redis**: Use managed Redis service (AWS ElastiCache, Redis Cloud)
- **Application**: Deploy multiple web containers behind a load balancer
- **Workers**: Scale Celery workers based on task queue length

## Monitoring

### Health Checks

The application includes basic health check endpoints:

- **Database**: Check via Django admin or API calls
- **Redis**: Monitor Celery task processing
- **Application**: Monitor API response times

### Logging

Logs are available through Docker:

```bash
# Application logs
docker-compose logs -f web

# Worker logs  
docker-compose logs -f worker

# Database logs
docker-compose logs -f db
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure PostgreSQL container is running
   - Check database credentials in .env file

2. **Celery Tasks Not Processing**
   - Verify Redis is running
   - Check worker container logs
   - Ensure CELERY_BROKER_URL is correct

3. **Excel File Not Found**
   - Ensure customer_data.xlsx and loan_data.xlsx are in project root
   - Check file permissions

4. **Port Already in Use**
   - Change port mappings in docker-compose.yml
   - Stop conflicting services

### Reset Database

```bash
# Stop services
docker-compose down

# Remove database volume
docker volume rm credit-approval-system_postgres_data

# Restart services
docker-compose up --build

# Run migrations and ingest data
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py ingest_initial_data
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

1. Check the troubleshooting section
2. Review Docker and application logs
3. Open an issue on the repository
4. Contact the development team

---

**Note**: This is a development setup. For production deployment, additional security measures, monitoring, and scaling considerations should be implemented.