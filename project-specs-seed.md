# Revised Project Boilerplate Generation Request (v2.0)

**Goal:**  
Generate the initial directory structure and essential boilerplate files for a web application focused on Exploratory Spatial Data Analysis (ESDA) and Web Cartography—with improvements for scalability, integration testing, CI/CD, and unified environment management.

**Core Technologies:**  
- **Backend:** Python with FastAPI as the primary API framework. Optionally, include a GUI component using Streamlit, Dash, or similar.  
- **Frontend:** Next.js (preferably with TypeScript) for modern web cartography.  
- **Data Handling:** Python libraries including GeoPandas, Pandas, Shapely, Rasterio, SQLAlchemy/psycopg2, Requests, and BeautifulSoup.  
- **Web Cartography:** Use libraries like Leaflet, Mapbox GL JS, or Deck.gl for interactive map rendering.

---

## Enhancements Over the Initial Spec

1. **Modularity and Testing:**  
   - Introduce a dedicated directory for **integration tests** spanning both backend and frontend components.  
   - Retain unit tests in the backend but add guidance for end-to-end tests.

2. **CI/CD and Pre-commit Hooks:**  
   - Add configuration files for CI/CD pipelines (e.g., GitHub Actions) to automate testing and deployment.  
   - Include pre-commit hook configuration (e.g., `.pre-commit-config.yaml`) to enforce code quality.

3. **Unified Environment Management:**  
   - Use a single top-level `.env.example` file to centralize environment variable documentation.  
   - Clearly document geospatial dependencies (e.g., GDAL installation) to ease cross-platform setup.

4. **Improved Documentation:**  
   - Expand the README with detailed onboarding instructions, architectural diagrams, and links to relevant resources.  
   - Add a CODE_OF_CONDUCT.md and LICENSE file for community transparency.

5. **Streamlined Directory Naming:**  
   - Rename the data processing subdirectory to avoid confusion with the top-level scripts.  
   - Consolidate redundant files where possible.

---

## Revised Directory Structure & Instructions

### 1. Create the Root Project Directory:
    mkdir esda-webmapping-project
    cd esda-webmapping-project

### 2. Create Top-Level Directories:
    mkdir backend
    mkdir frontend
    mkdir data
    mkdir docs
    mkdir scripts
    mkdir tests  # For integration/end-to-end tests spanning components

### 3. Populate the `backend` Directory:
    cd backend
    mkdir app
    mkdir app/api
    mkdir app/api/v1
    mkdir app/core
    mkdir app/db        # (If using a database)
    mkdir app/models    # (For Pydantic models/schemas)
    mkdir app/services  # (Business logic)
    mkdir app/utils     # (Shared backend utilities)
    mkdir gui           # (For Python-driven GUI components/app)
    mkdir tests         # (Backend unit tests)
    touch app/__init__.py
    touch app/main.py         # FastAPI app entry point
    touch app/api/__init__.py
    touch app/api/v1/__init__.py
    touch app/api/v1/endpoints_maps.py    # Example map data endpoint
    touch app/api/v1/endpoints_data.py    # Example data endpoint
    touch app/core/config.py              # Settings management
    touch app/core/__init__.py
    touch app/db/__init__.py              # Database connection initialization
    touch app/models/__init__.py
    touch app/models/geojson_models.py     # Example Pydantic model for GeoJSON
    touch app/services/__init__.py
    touch app/utils/__init__.py
    touch gui/__init__.py
    touch gui/main_gui.py                 # Entry point for the GUI (e.g., Streamlit, Dash)
    touch tests/__init__.py
    touch requirements.txt                # Python dependencies for backend
    cd ..

### 4. Populate the `frontend` Directory (using Next.js standard):
*Preferably, initialize with TypeScript and ESLint. If direct command execution isn’t possible, manually create:*

    cd frontend
    # Ideally, run:
    # npx create-next-app@latest . --typescript --eslint --tailwind --src-dir --app --import-alias "@/*"

    # Manual fallback structure:
    mkdir src
    mkdir src/app
    mkdir src/components
    mkdir src/components/ui       # UI library components (e.g., Shadcn/UI)
    mkdir src/components/map      # Map-specific components
    mkdir src/lib                 # Utility functions, API client
    mkdir src/styles
    mkdir public
    mkdir public/icons
    mkdir tests                   # Frontend tests
    touch src/app/layout.tsx      # Root layout file
    touch src/app/page.tsx        # Homepage
    touch src/app/globals.css
    touch src/components/map/MapComponent.tsx   # Placeholder for a map component
    touch src/lib/api.ts          # Functions for backend API calls
    touch src/lib/utils.ts        # General utilities
    touch .env.local              # Local environment variables (add to .gitignore)
    touch .env.example            # Example environment variables (centralized)
    touch next.config.mjs         # Next.js configuration
    touch package.json            # Will be auto-generated by create-next-app
    touch tsconfig.json           # Will be auto-generated by create-next-app
    touch tailwind.config.ts      # If using Tailwind
    touch postcss.config.js       # If using Tailwind
    cd ..

### 5. Populate the `data` Directory:
    cd data
    mkdir notebooks                # Jupyter notebooks for ESDA
    mkdir data_processing          # (Renamed from scripts to avoid ambiguity)
    mkdir data_processing/scraping
    mkdir data_processing/cleaning
    mkdir data_processing/transformation
    mkdir raw                      # Raw data (to be gitignored)
    mkdir processed                # Processed data for analysis/backend consumption
    mkdir utils                    # Shared utilities for data tasks
    touch notebooks/01_Initial_ESDA.ipynb          # Example notebook
    touch data_processing/scraping/scrape_data_source_A.py       # Example scraping script
    touch data_processing/cleaning/clean_dataset_A.py            # Example cleaning script
    touch data_processing/transformation/transform_for_mapping.py # Example transformation script
    touch utils/__init__.py
    touch utils/readers.py         # Example data reader utility
    touch requirements.txt         # Python dependencies for data tasks
    cd ..

### 6. Populate the `docs` Directory:
    cd docs
    touch architecture.md          # High-level design and architecture diagrams
    touch setup_guide.md           # Detailed setup instructions (including GDAL/geospatial dependency setup)
    touch api_reference.md         # API documentation (auto-generate as needed)
    touch CODE_OF_CONDUCT.md       # Community guidelines
    touch LICENSE                  # Licensing information (choose an appropriate license)
    cd ..

### 7. Populate the Top-Level `scripts` Directory:
    cd scripts
    touch run_dev.sh               # Script to start development servers
    touch run_tests.sh             # Script to run all tests (unit and integration)
    touch build_project.sh         # Build and deployment scripts for frontend/backend
    chmod +x *.sh                  # Make scripts executable
    cd ..

### 8. Populate the Top-Level `tests` Directory:
    cd tests
    touch integration_test_example.py   # Example integration test script
    cd ..

### 9. Create Root-Level Files:
    touch README.md                # Project overview, setup instructions, and usage
    touch .gitignore               # Git ignore rules (see below)
    touch .env.example             # Centralized example for environment variables
    touch docker-compose.yml       # Optional: Container orchestration configuration
    touch Makefile                 # Optional: Common tasks (e.g., make run-dev, make test)
    touch .pre-commit-config.yaml  # Pre-commit hook configuration for code quality

---

## Sample Boilerplate Content

### `.gitignore`:
    # Python
    __pycache__/
    *.pyc
    *.pyo
    *.pyd
    .Python
    env/
    venv/
    pip-wheel-metadata/
    *.egg-info/
    dist/
    build/
    *.sqlite3
    *.db

    # Jupyter Notebooks
    .ipynb_checkpoints

    # Data files (raw and processed)
    data/raw/
    data/processed/
    *.csv
    *.geojson
    *.gpkg
    *.shp
    *.shx
    *.dbf
    *.prj
    *.tif
    *.tiff

    # Node (Frontend)
    node_modules/
    .next/
    npm-debug.log*
    yarn-debug.log*
    yarn-error.log*
    *.log
    *.lock
    build/
    dist/
    coverage/

    # Environment Variables
    .env
    .env.*
    !.env.example

    # IDE/Editor files
    .idea/
    .vscode/
    *.sublime-*

    # OS files
    .DS_Store
    Thumbs.db

### `backend/requirements.txt`:
    fastapi[all]         # FastAPI and Pydantic
    uvicorn[standard]    # ASGI server
    geopandas            # Geospatial data processing
    pandas               # Data handling
    shapely              # Geometric operations
    # Uncomment if using database ORM:
    # sqlalchemy
    # Database drivers (e.g., psycopg2-binary for PostgreSQL)
    # GUI libraries (choose one, e.g., streamlit, dash, PyQt6)
    streamlit            # Example for a lightweight GUI
    python-dotenv        # Environment variable management
    requests             # HTTP requests

### `data/requirements.txt`:
    jupyterlab
    notebook
    pandas
    geopandas
    matplotlib
    seaborn
    requests
    beautifulsoup4       # For web scraping
    # Uncomment if working with raster data:
    # rasterio

### `backend/app/main.py`:
    from fastapi import FastAPI
    from contextlib import asynccontextmanager
    # from .api.v1 import endpoints_maps, endpoints_data  # Uncomment as needed
    # from .core.config import settings                  # Load configuration settings

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Initialize resources (e.g., database connections, ML models)
        print("Starting up...")
        yield
        print("Shutting down...")

    app = FastAPI(
        title="ESDA Web Mapping API",
        description="API for serving geospatial data and analysis results.",
        version="0.1.0",
        lifespan=lifespan  # Optional lifecycle management
    )

    # Example root endpoint
    @app.get("/")
    async def read_root():
        return {"message": "Welcome to the ESDA Web Mapping API"}

    # Include routers as endpoints are implemented
    # app.include_router(endpoints_maps.router, prefix="/api/v1/maps", tags=["Maps"])
    # app.include_router(endpoints_data.router, prefix="/api/v1/data", tags=["Data"])

### `frontend/package.json` (example):
    {
      "name": "frontend",
      "version": "0.1.0",
      "private": true,
      "scripts": {
        "dev": "next dev",
        "build": "next build",
        "start": "next start",
        "lint": "next lint"
      },
      "dependencies": {
        "react": "latest",
        "react-dom": "latest",
        "next": "latest",
        "leaflet": "latest",
        "react-leaflet": "latest",
        "@types/leaflet": "latest",
        "axios": "latest"
      },
      "devDependencies": {
        "@types/node": "latest",
        "@types/react": "latest",
        "@types/react-dom": "latest",
        "typescript": "latest",
        "eslint": "latest",
        "eslint-config-next": "latest",
        "autoprefixer": "latest",
        "postcss": "latest",
        "tailwindcss": "latest"
      }
    }

### `README.md`:
    # ESDA Web Mapping Project

    This project combines a Python-based FastAPI backend for geospatial data processing with a Next.js frontend for interactive web cartography and visualization.

    ## Project Structure

    esda-webmapping-project/
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
    │   ├── setup_guide.md   # Detailed setup instructions (including GDAL/geospatial deps)
    │   ├── api_reference.md # API documentation
    │   ├── CODE_OF_CONDUCT.md
    │   └── LICENSE
    ├── scripts/             # Helper scripts (dev, test, build)
    ├── tests/               # Integration and end-to-end tests
    ├── .env.example         # Centralized environment variable documentation
    ├── .gitignore           # Git ignore rules
    ├── docker-compose.yml   # Container orchestration (optional)
    ├── Makefile             # Common tasks
    └── .pre-commit-config.yaml # Pre-commit hook configuration

    ## Setup Instructions

    1. Clone the repository.
    2. Install dependencies:
       - Backend: cd backend && pip install -r requirements.txt
       - Data tasks: cd data && pip install -r requirements.txt
       - Frontend: cd frontend && npm install
    3. Environment Variables:
       - Copy .env.example to .env and configure the values.
    4. Geospatial Dependencies:
       - Install GDAL and other platform-specific geospatial libraries as needed.
    5. Running the Application:
       - Backend: cd backend && uvicorn app.main:app --reload --port 8000
       - Frontend: cd frontend && npm run dev
       - Data Scripts/Notebooks: Run via command line or launch Jupyter Lab from data.

    ## CI/CD & Code Quality

    - CI/CD: Configuration for GitHub Actions is provided in .github/workflows/ (if using GitHub). Adjust accordingly if using another CI/CD platform.
    - Pre-commit Hooks: Run pre-commit install to set up hooks as defined in .pre-commit-config.yaml.

    ## Additional Resources

    - For detailed setup and troubleshooting, refer to docs/setup_guide.md.
    - API documentation will be auto-generated and updated in docs/api_reference.md.
