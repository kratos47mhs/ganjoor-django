# Ganjoor - A Persian Poetry Platform

Ganjoor is a web application for browsing and reading a vast collection of Persian poetry. It provides a clean, modern, and user-friendly interface for exploring the works of various poets, organized by categories and poems.

## Features

*   **Browse by Poet and Category:** Explore a rich collection of poetry, organized by poets and their respective categories of work.
*   **Beautiful Reading Experience:** A clean and focused reading view for poems, with support for various verse types.
*   **User Favorites:** Registered users can save their favorite poems for easy access.
*   **Search:** A powerful search functionality to find poems by title or content.
*   **RESTful API:** A comprehensive API for programmatic access to the poetry data, with full OpenAPI/Swagger documentation.
*   **Observability with OpenTelemetry and SigNoz:** The application is fully instrumented with OpenTelemetry to send logs, metrics, and traces to a SigNoz server for monitoring and troubleshooting.

## Technologies Used

*   **Backend:**
    *   Django
    *   Django Rest Framework
    *   DRF Spectacular (for OpenAPI/Swagger documentation)
    *   PostgreSQL
*   **Frontend:**
    *   HTML5
    *   CSS3
    *   Bootstrap 5
*   **Observability:**
    *   OpenTelemetry
    *   SigNoz

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/kratos47mhs/ganjoor-django.git
    cd ganjoor-django
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Set up the PostgreSQL database:**
    *   Create a PostgreSQL database named `ganjoor`.
    *   Create a user named `ganjoor` with a password.
    *   Update the database credentials in `ganjoor/settings.py`.

4.  **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Import the poetry data:**
    *   You will need CSV files for poets, categories, poems, and verses.
    *   Run the following command to import the data:
    ```bash
    python manage.py import_ganjoor --poets /path/to/poets.csv --cats /path/to/cats.csv --poems /path/to/poems.csv --verses /path/to/verses.csv
    ```

6.  **Set up OpenTelemetry for SigNoz (Optional):**
    *   Set the `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable to the address of your SigNoz server.
    ```bash
    export OTEL_EXPORTER_OTLP_ENDPOINT="http://your-signoz-server:4317"
    ```

7.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

The application will be available at `http://127.0.0.1:8000`.

## API

The application provides a RESTful API for accessing the poetry data. The API endpoints are available at `/api/`.

*   `/api/poets/`
*   `/api/categories/`
*   `/api/poems/`
*   `/api/verses/`
*   `/api/favorites/`

### API Documentation

Interactive API documentation is available via Swagger UI at `/api/schema/swagger-ui/` when the development server is running. This provides a user-friendly interface to explore and test the API endpoints, view request/response schemas, and understand authentication requirements.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.
