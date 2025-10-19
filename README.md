# Ganjoor - A Persian Poetry Platform

Ganjoor is a web application for browsing and reading a vast collection of Persian poetry. It provides a clean, modern, and user-friendly interface for exploring the works of various poets, organized by categories and poems.

## Features

*   **Multilingual Support (i18n):** Full internationalization with Persian (فارسی) and English support, including RTL/LTR layouts and language switching.
*   **Browse by Poet and Category:** Explore a rich collection of poetry, organized by poets and their respective categories of work.
*   **Beautiful Reading Experience:** A clean and focused reading view for poems, with support for various verse types.
*   **User Favorites:** Registered users can save their favorite poems for easy access.
*   **Search:** A powerful search functionality to find poems by title or content.
*   **RESTful API:** A comprehensive API for programmatic access to the poetry data, with full OpenAPI/Swagger documentation.
*   **Observability with OpenTelemetry and SigNoz:** The application is fully instrumented with OpenTelemetry to send logs, metrics, and traces to a SigNoz server for monitoring and troubleshooting.
*   **Security-Hardened:** Environment-based configuration, secure defaults, and production-ready security headers.
*   **Performance Optimized:** Query optimization, pagination, caching, and rate limiting built-in.

## Technologies Used

*   **Backend:**
    *   Django 5.2.6
    *   Django Rest Framework 3.16.1
    *   DRF Spectacular (for OpenAPI/Swagger documentation)
    *   PostgreSQL (with connection pooling)
    *   Django i18n (Internationalization)
*   **Frontend:**
    *   HTML5
    *   CSS3
    *   Bootstrap 5 (with RTL support)
    *   Vazirmatn Font (for Persian)
*   **Observability:**
    *   OpenTelemetry
    *   SigNoz
*   **Security:**
    *   Environment variables (python-dotenv)
    *   JWT Authentication
    *   Rate Limiting

## Setup and Installation

### Quick Setup (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/kratos47mhs/ganjoor-django.git
cd ganjoor-django

# 2. Run automated setup
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Create virtual environment
- Install dependencies
- Generate secure `.env` file with SECRET_KEY
- Create necessary directories
- Optionally run migrations and create superuser

### Manual Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/kratos47mhs/ganjoor-django.git
    cd ganjoor-django
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    ```bash
    cp .env.example .env
    # Edit .env and set:
    # - SECRET_KEY (generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    # - DB_PASSWORD
    # - Other settings as needed
    ```

4.  **Set up the PostgreSQL database:**
    ```bash
    # Create database and user
    sudo -u postgres psql
    postgres=# CREATE DATABASE ganjoor;
    postgres=# CREATE USER ganjoor WITH PASSWORD 'your-password';
    postgres=# GRANT ALL PRIVILEGES ON DATABASE ganjoor TO ganjoor;
    postgres=# \q
    ```

5.  **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Create a superuser:**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Compile translation files:**
    ```bash
    python manage.py compilemessages
    ```

8.  **Collect static files:**
    ```bash
    python manage.py collectstatic --noinput
    ```

9.  **Import the poetry data (Optional):**
    *   You will need CSV files for poets, categories, poems, and verses.
    *   Run the following command to import the data:
    ```bash
    python manage.py import_ganjoor --poets /path/to/poets.csv --cats /path/to/cats.csv --poems /path/to/poems.csv --verses /path/to/verses.csv --batch-size 1000
    ```

10. **Set up OpenTelemetry for SigNoz (Optional):**
    *   Set the `OTEL_EXPORTER_OTLP_ENDPOINT` in `.env` file:
    ```ini
    OTEL_EXPORTER_OTLP_ENDPOINT=http://your-signoz-server:4317
    ```

11. **Run the development server:**
    ```bash
    python manage.py runserver
    ```

The application will be available at `http://127.0.0.1:8000`.

## Access Points

*   **Home Page:** `http://127.0.0.1:8000/` (Persian)
*   **English Version:** `http://127.0.0.1:8000/en/`
*   **Admin Panel:** `http://127.0.0.1:8000/admin/`
*   **API Root:** `http://127.0.0.1:8000/api/`
*   **API Documentation:** `http://127.0.0.1:8000/api/schema/swagger-ui/`

## Internationalization (i18n)

The application fully supports Persian (فارسی) and English languages:

*   **Language Switcher:** Available in the header navigation
*   **URL-based Language Selection:** 
    - `/` - Persian (default)
    - `/en/` - English
*   **RTL/LTR Support:** Automatic layout switching
*   **Translated Components:** Models, views, templates, API responses, and error messages

For more details, see:
- `I18N_GUIDE.md` - Comprehensive i18n documentation
- `I18N_SUMMARY.md` - Implementation summary
- `I18N_QUICKREF.md` - Quick reference card

## API

The application provides a comprehensive RESTful API for accessing the poetry data. The API endpoints are available at `/api/`.

### Main Endpoints

*   `/api/poets/` - List and manage poets
*   `/api/categories/` - Browse poetry categories
*   `/api/poems/` - Access poems and verses
*   `/api/verses/` - Individual verse management
*   `/api/favorites/` - User favorites (authentication required)

### Custom Actions

*   `/api/poets/{id}/categories/` - Get poet's categories
*   `/api/poets/{id}/poems/` - Get poet's poems
*   `/api/categories/{id}/poems/` - Get category's poems
*   `/api/poems/search/?q=query` - Search poems
*   `/api/favorites/toggle/` - Toggle favorite status
*   `/api/settings/me/` - Get/update user settings

### API Features

*   **Pagination:** 20 items per page (default)
*   **Filtering:** Filter by related fields
*   **Searching:** Full-text search across models
*   **Ordering:** Sort by multiple fields
*   **Authentication:** JWT + Session auth
*   **Rate Limiting:** 100 req/hour (anonymous), 1000 req/hour (authenticated)

### API Documentation

Interactive API documentation is available via Swagger UI at `/api/schema/swagger-ui/` when the development server is running. This provides a user-friendly interface to explore and test the API endpoints, view request/response schemas, and understand authentication requirements.

### Authentication

```bash
# Get JWT token
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"your-username","password":"your-password"}'

# Use token in requests
curl http://127.0.0.1:8000/api/favorites/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Project Documentation

- **`README.md`** - This file (overview and setup)
- **`QUICKSTART.md`** - Quick start guide with examples
- **`CODE_REVIEW_IMPROVEMENTS.md`** - Comprehensive code review and improvements (560 lines)
- **`CHANGES_SUMMARY.md`** - Summary of all changes (399 lines)
- **`DEPLOYMENT_CHECKLIST.md`** - Production deployment guide (467 lines)
- **`I18N_GUIDE.md`** - Complete i18n documentation (650 lines)
- **`I18N_SUMMARY.md`** - i18n implementation summary (452 lines)
- **`I18N_QUICKREF.md`** - i18n quick reference (304 lines)

## Security Notes

⚠️ **IMPORTANT:** Before deploying to production:

1. Create a `.env` file from `.env.example`
2. Generate a secure `SECRET_KEY`
3. Set `DEBUG=False`
4. Update `ALLOWED_HOSTS` with your domain
5. Use strong database passwords
6. Enable HTTPS and security headers
7. Review the `DEPLOYMENT_CHECKLIST.md`

## Performance Features

- ✅ Query optimization with `select_related` and `prefetch_related`
- ✅ Database connection pooling
- ✅ Pagination on all list views
- ✅ API rate limiting
- ✅ Cache configuration (local memory + Redis support)
- ✅ Bulk operations in data import

## Code Quality

- ✅ No wildcard imports
- ✅ Comprehensive docstrings
- ✅ Type hints where appropriate
- ✅ Consistent error handling
- ✅ Structured API responses
- ✅ Bilingual error messages
- ✅ Validation throughout

## Testing

```bash
# Run tests (when implemented)
python manage.py test

# Check for issues
python manage.py check

# Check deployment readiness
python manage.py check --deploy
```

## Contributing

Contributions are welcome! Please:

1. Follow the existing code patterns
2. Add tests for new features
3. Update docstrings and comments
4. Ensure i18n strings are translatable
5. Test in both Persian and English
6. Update documentation as needed

Please feel free to submit a pull request or open an issue.

## License

This project is open source. Please check the LICENSE file for details.

## Support

For issues or questions:
1. Check the documentation files
2. Review error logs in `logs/` directory
3. Enable `DEBUG=True` in `.env` for detailed errors
4. Check OpenTelemetry traces in SigNoz (if configured)

## Acknowledgments

- Persian poetry data from Ganjoor project
- Django and Django REST Framework communities
- Bootstrap for responsive UI
- Vazirmatn font for beautiful Persian typography
