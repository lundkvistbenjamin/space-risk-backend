# Space Weather Risk Backend

**Live Demo (Frontend):** _Coming soon_

**Frontend Repository:** _Coming soon_

Space Weather Risk Backend is a FastAPI service and automated data ingestion pipeline that collects solar flare and coronal mass ejection (CME) data from NASA DONKI, transforms the observations into risk-related features, and calculates infrastructure risk assessments for radio communications, GPS, and power grids.

The project is designed as a portfolio backend demonstrating API development, external API integration, data transformation, automated ingestion, risk scoring, testing, and cloud deployment.

## Core Features

### NASA DONKI Data Ingestion

The ingestion pipeline retrieves solar flare and CME events from NASA's DONKI API over a configurable rolling date range.

The pipeline identifies the strongest observed solar flare and the most significant CME based on Earth-directed status and CME speed.

### Space Weather Risk Engine

The risk engine converts observed space weather activity into normalized risk scores for:

- Radio blackout risk
- GPS disruption risk
- Power grid risk

The individual scores are combined into an overall assessment with a corresponding threat level.

### FastAPI REST API

The backend exposes endpoints for health monitoring, retrieving the latest assessment, and viewing recent assessment history.

### Supabase Persistence

Generated assessments can be stored in Supabase, including metadata, observed extremes, individual risk scores, and the resulting threat level.

### Automated Daily Ingestion

A GitHub Actions workflow runs the ingestion pipeline automatically each day and can also be triggered manually.

### Automated Testing

The project includes a pytest suite covering:

- Event transformation
- NASA API client behavior
- Ingestion logic
- Risk calculations
- API endpoints

External services are mocked where appropriate so the tests do not depend on live NASA or Supabase data.

## Tech Stack

### Backend

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic

### Data & External Services

- NASA DONKI API
- Supabase
- Requests

### Testing & Infrastructure

- `pytest` — automated test suite
- GitHub Actions — scheduled ingestion
- Vercel — serverless API deployment configuration

## Project Structure

```text
.
├── .github/
│   └── workflows/
│       └── ingest.yml              # Daily GitHub Actions ingestion workflow
├── api/
│   └── index.py                    # Vercel serverless entry point
├── app/
│   ├── database/
│   │   ├── __init__.py
│   │   └── supabase.py             # Supabase client configuration
│   ├── pipeline/
│   │   ├── __init__.py
│   │   └── ingestion.py            # Data ingestion and Supabase persistence
│   ├── services/
│   │   ├── __init__.py
│   │   ├── event_transformer.py    # NASA event feature extraction
│   │   ├── nasa_client.py           # NASA DONKI API client
│   │   └── risk_engine.py           # Infrastructure risk calculations
│   ├── __init__.py
│   ├── config.py                   # Environment and API configuration
│   └── server.py                   # FastAPI application and API endpoints
├── tests/
│   ├── __init__.py
│   ├── test_event_transformer.py   # Event transformation tests
│   ├── test_ingestion.py           # Ingestion selection tests
│   ├── test_nasa_client.py         # NASA API client tests
│   ├── test_risk_engine.py         # Risk calculation tests
│   └── test_server.py              # API endpoint tests
├── .gitignore
├── LICENSE
├── main.py                         # GitHub Actions ingestion entry point
├── README.md
├── requirements.txt
└── vercel.json                     # Vercel deployment configuration
```

## Data Pipeline

The ingestion process follows a simple workflow:

### 1. Data Collection

Retrieve solar flare and CME events from NASA DONKI for the configured rolling time window.

### 2. Event Transformation

Convert solar flare classifications into X-ray flux values and extract relevant CME properties such as speed, half-angle, and Earth-directed status.

### 3. Event Selection

Select the strongest solar flare and the primary CME. Earth-directed CMEs receive priority, with CME speed used as a tie-breaker.

### 4. Risk Assessment

Calculate infrastructure-specific risk scores and determine the overall threat level.

### 5. Persistence

Store the generated assessment in Supabase when database credentials are configured.

## API Endpoints

| Endpoint | Description |
|-----------|-------------|
| `/health` | Returns the service health status |
| `/api/v1/latest-assessment` | Returns the most recent stored assessment |
| `/api/v1/trends` | Returns recent assessment history |

The trends endpoint accepts an optional `limit` query parameter and caps the requested number of records at 30.

Example:

```text
GET /api/v1/trends?limit=10
```

## Risk Assessment

The risk engine produces three infrastructure-specific scores:

| Risk Category | Description |
|---------------|-------------|
| Radio | Estimates radio blackout risk from solar X-ray flux |
| GPS | Estimates GPS disruption risk using solar activity and CME characteristics |
| Power Grid | Estimates power grid risk using Earth-directed CME characteristics |

Each score is normalized to a range from `0` to `100`.

The final assessment reports the highest infrastructure risk score as `overall_max` and assigns a threat level based on the resulting score.

## Automated Ingestion

The GitHub Actions workflow runs the ingestion pipeline daily at 01:00 UTC.

The workflow:

1. Checks out the repository.
2. Sets up Python.
3. Installs project dependencies.
4. Loads NASA and Supabase credentials from GitHub Actions secrets.
5. Runs `main.py` to generate and store the latest assessment.

The workflow can also be triggered manually from GitHub Actions.

## Configuration

The application reads the following environment variables:

```text
NASA_API_KEY
SUPABASE_URL
SUPABASE_KEY
```

For local development, these values can be stored in a `.env` file.

The `.env` file is excluded from version control.

## Testing

Run the complete test suite from the project root:

```bash
pytest
```

The test suite uses mocks for external services where appropriate, allowing the tests to run without making live API requests or writing to the production database.

## Local Development

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI application locally:

```bash
uvicorn app.server:app --reload
```

The API will be available locally at:

```text
http://127.0.0.1:8000
```

FastAPI's interactive API documentation is available at `/docs` during local development.

## Security

API credentials are supplied through environment variables and GitHub Actions secrets rather than being committed to the repository.

The backend does not expose NASA or Supabase credentials through its API responses.

CORS is currently configured for development and frontend integration and can be restricted to the production frontend once the frontend application is complete.

## Deployment

The project includes Vercel configuration for deploying the FastAPI application as a serverless function.

The ingestion pipeline is separate from the API deployment and is executed through GitHub Actions.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.
