# ESDA Web Mapping Project

A comprehensive web application focused on Exploratory Spatial Data Analysis (ESDA) and Web Cartography. This project combines a Python-based FastAPI backend for geospatial data processing with a Next.js frontend for interactive web mapping and visualization.

## Project Overview

This project provides a scalable architecture for spatial data analysis and visualization with the following key features:

- **Backend API**: FastAPI-powered RESTful API for geospatial data processing and analysis
- **Frontend Application**: Modern Next.js application with interactive mapping capabilities
- **Data Processing Pipeline**: Tools for data acquisition, cleaning, and transformation
- **Visualization Components**: Interactive web maps using modern cartography libraries
- **Optional GUI Component**: Python-driven GUI using Streamlit for additional analysis capabilities
- **Environment Configuration System**: Flexible configuration system with environment-specific settings
- **Enhanced Logging Infrastructure**: Structured logging with rotation and multiple outputs
- **Geospatial Utilities**: Comprehensive geospatial data validation and processing tools

## Core Technologies

### Backend
- **Python** with **FastAPI** as the primary API framework
- **Streamlit** for optional GUI components
- **GeoPandas**, **Pandas**, **Shapely** for geospatial data processing
- **SQLAlchemy/psycopg2** for database interactions (if configured)

### Frontend
- **Next.js** with **TypeScript** for the web application
- **Leaflet**, **Mapbox GL JS**, or **Deck.gl** for interactive map rendering
- **Tailwind CSS** for styling

### Data Handling
- **Jupyter Notebooks** for exploratory analysis
- **GeoPandas** and **Pandas** for data manipulation
- **Requests** and **BeautifulSoup** for data acquisition

## Project Structure

```
/
├── backend/             # FastAPI backend & Python GUI components
│   ├── app/             # Core application code
│   │   ├── api/         # API endpoint definitions
│   │   ├── core/        # Configuration and core logic
│   │   ├── db/          # Database interaction (models, sessions)
│   │   ├── models/      # Pydantic schemas/models
│   │   ├── services/    # Business logic services
│   │   └── utils/       # Shared backend utilities
│   ├── gui/             # Python-driven GUI components/app
│   ├── tests/           # Unit tests for backend
│   ├── main.py          # FastAPI app entry point
│   └── requirements.txt # Backend dependencies
├── frontend/            # Next.js frontend application
│   ├── src/             # Source code (with App Router, components, lib, styles)
│   ├── public/          # Static assets
│   ├── tests/           # Frontend tests
│   ├── package.json     # Frontend dependencies
│   └── tsconfig.json    # TypeScript configuration
├── data/                # Data processing and analysis
│   ├── notebooks/       # Jupyter notebooks for ESDA
│   ├── data_processing/ # Scripts for scraping, cleaning, transformation
│   ├── raw/             # Raw data (gitignored)
│   ├── processed/       # Processed data
│   ├── utils/           # Shared data utilities
│   └── requirements.txt # Data task dependencies
├── docs/                # Project documentation
│   ├── architecture.md  # High-level design and diagrams
│   ├── setup_guide.md   # Detailed setup instructions
│   ├── api_reference.md # API documentation
│   ├── CODE_OF_CONDUCT.md
│   └── LICENSE
├── scripts/             # Helper scripts (dev, test, build)
├── tests/               # Integration and end-to-end tests
├── .env.example         # Centralized environment variable documentation
├── .gitignore           # Git ignore rules
├── docker-compose.yml   # Container orchestration
├── Makefile             # Common tasks
└── .pre-commit-config.yaml # Pre-commit hook configuration
```

## Setup Instructions

### Prerequisites

- Python 3.8+ for backend and data processing
- Node.js 16+ for frontend development
- GDAL and other geospatial libraries (see detailed setup in `docs/setup_guide.md`)
- PostgreSQL with PostGIS extension (optional, for spatial database functionality)

### Installation

> **Note:** This is a template project. No dependencies are pre-installed, and you will need to install them as described below.

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd esda-webmapping-project
   ```

2. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Install backend dependencies**

   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

4. **Install data processing dependencies**

   ```bash
   cd data
   pip install -r requirements.txt
   cd ..
   ```

5. **Install frontend dependencies** (required)

   ```bash
   cd frontend
   npm install  # This step is required as node_modules are not included in the template
   cd ..
   ```

### Running the Application

#### Using helper scripts

```bash
# Start development servers (backend and frontend)
./scripts/run_dev.sh

# Run all tests
./scripts/run_tests.sh

# Build the project for production
./scripts/build_project.sh
```

#### Manual startup

**Backend API:**

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm run dev
```

**GUI Component (optional):**

```bash
cd backend
streamlit run gui/main_gui.py
```

**Jupyter Notebooks:**

```bash
cd data
jupyter lab
```

## Development Workflow

### Code Quality and Standards

This project uses pre-commit hooks to enforce code quality standards. Install them with:

```bash
pip install pre-commit
pre-commit install
```

### Testing

- **Backend unit tests:** `cd backend && pytest`
- **Frontend tests:** `cd frontend && npm test`
- **Integration tests:** `cd tests && pytest`

### API Documentation

Once the backend server is running, access the auto-generated API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Deployment

### Using Docker

The project includes Docker configuration for containerized deployment:

```bash
docker-compose up -d
```

See `docker-compose.yml` for details on the containerized setup.

### Manual Deployment

For manual deployment instructions, refer to `docs/setup_guide.md`.

## Contributing

Please read `docs/CODE_OF_CONDUCT.md` for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the terms specified in the `docs/LICENSE` file.

## Additional Resources

- For detailed architecture information, see `docs/architecture.md`
- For API reference documentation, see `docs/api_reference.md`
- For troubleshooting and detailed setup instructions, see `docs/setup_guide.md`

## Key Features

### Environment Configuration System

The project includes a flexible environment configuration system that supports different deployment environments:

- **Environment-Specific Settings**: Configuration files for development, testing, staging, and production environments
- **JSON Configuration Files**: Located in `backend/config/` directory with environment-specific settings
- **Environment Variables**: Override configuration via `.env` file or system environment variables
- **Hierarchical Configuration**: Settings are loaded from files, then environment variables, with sensible defaults

```python
# Example of accessing configuration in code
from app.core.environment_config import EnvironmentConfig

# Get database settings for current environment
db_settings = EnvironmentConfig.get_database_settings()
```

### Enhanced Logging Infrastructure

The project includes a comprehensive logging system with the following features:

- **Structured Logging**: JSON-formatted logs for better parsing and analysis
- **Multiple Outputs**: Console and file logging with different configurations
- **Log Rotation**: Size-based or time-based log rotation to manage log files
- **Environment-Aware**: Different log levels based on the environment (DEBUG for development, WARNING for production)
- **Contextual Information**: Automatic enrichment of logs with process, thread, and module information

```python
# Example of using the logger in code
from app.utils.enhanced_logging import get_logger

logger = get_logger(__name__)
logger.info("Processing data", extra={"data_size": 1024, "format": "GeoJSON"})
```

### Geospatial Utilities

The project provides a comprehensive set of geospatial utilities for working with geographic data:

- **GeoJSON Validation**: Pydantic models for validating GeoJSON objects
- **Spatial Operations**: Functions for distance calculations, buffering, and bounding box operations
- **Coordinate Transformations**: Utilities for converting between coordinate systems
- **Geometry Simplification**: Tools for simplifying complex geometries
- **Spatial Queries**: Support for spatial filtering and proximity searches

```python
# Example of using geospatial utilities
from app.utils.geospatial import haversine_distance, DistanceUnit

# Calculate distance between two points
distance = haversine_distance(
    point1=(longitude1, latitude1),
    point2=(longitude2, latitude2),
    unit=DistanceUnit.KILOMETERS
)
```