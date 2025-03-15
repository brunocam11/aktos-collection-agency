# Collection Agency Data Management System

A Django application that allows a collection agency to ingest data files provided by their clients and query account information.

## Features

- API endpoint for accounts with filtering capabilities
- CSV file ingestion through API endpoint
- Support for multiple collection agencies and clients
- Cursor-based pagination for efficient data retrieval
- Comprehensive test coverage

## Requirements

- Python 3.10 or higher
- Poetry for dependency management
- SQLite for development (PostgreSQL for production)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/collection-agency.git
   cd collection-agency
   ```

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

3. Run migrations:
   ```
   poetry run python manage.py migrate
   ```

4. Create a superuser:
   ```
   poetry run python manage.py createsuperuser
   ```

## Running the Server

```
poetry run python manage.py runserver
```

The API will be available at http://localhost:8000/api/

## API Endpoints

### Accounts

- `GET /api/accounts/`: List all accounts (with pagination)
- `GET /api/accounts/?min_balance=100&max_balance=1000&status=IN_COLLECTION`: Filter accounts by balance range and status
- `GET /api/accounts/?consumer_name=John`: Filter accounts by consumer name
- `POST /api/accounts/upload-csv/`: Upload a CSV file for data ingestion

### Filtering Parameters

All query parameters are optional and can be combined:

1. `min_balance`: The minimum balance (inclusive)
2. `max_balance`: The maximum balance (inclusive)
3. `consumer_name`: Filter by consumer name (case-insensitive, partial match)
4. `status`: Filter by status (exact match: IN_COLLECTION, PAID_IN_FULL, INACTIVE)

### Pagination

The API uses cursor-based pagination which provides:
- Consistent results when new items are added
- Better performance with large datasets
- No duplicate records when paginating

To navigate through pages, use the `next` and `previous` links in the response.

## Running Tests

```
poetry run python manage.py test
```

### Test Coverage

To run tests with coverage reporting:

```
./run_tests_with_coverage.sh
```

This will:
- Run all tests with coverage measurement
- Display coverage statistics in the terminal 

The coverage report shows which lines of code are executed during tests, helping identify untested code.

## Deployment

The application is designed to be deployed to Heroku or any other cloud platform that supports Django applications. For production deployment:

1. Set the `DATABASE_URL` environment variable for PostgreSQL
2. Configure static file serving
3. Set `DEBUG=False` and configure proper `ALLOWED_HOSTS`

## Design Decisions

- Used Django REST Framework for API development
- Implemented cursor-based pagination for efficient data retrieval
- Used a service-based approach for CSV ingestion with transaction support
- Created a normalized data model to support many-to-many relationships between accounts and consumers

## Areas for Improvement

- Add authentication and authorization
- Implement background processing for large CSV files
- Add more comprehensive data validation
- Create a frontend interface for data visualization 