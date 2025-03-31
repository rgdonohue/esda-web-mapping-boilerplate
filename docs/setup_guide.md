# Setup Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Development Tools](#development-tools)

## Prerequisites

### Required Software
- **Python 3.8+**
  - Check version: `python --version`
  - [Download Python](https://www.python.org/downloads/)

- **Node.js 16+**
  - Check version: `node --version`
  - [Download Node.js](https://nodejs.org/)

- **Make**
  - Check version: `make --version`
  - Unix/Linux: Usually pre-installed
  - macOS: Install via Xcode Command Line Tools: `xcode-select --install`
  - Windows: Install via [Chocolatey](https://chocolatey.org/): `choco install make`

### Spatial Libraries

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libspatialindex-dev \
    libproj-dev \
    proj-data \
    proj-bin
```

#### macOS
```bash
brew install gdal
brew install spatialindex
brew install proj
```

#### Windows
1. Download OSGeo4W Network Installer from [OSGeo4W](https://trac.osgeo.org/osgeo4w/)
2. Run installer and select:
   - GDAL
   - PROJ
   - Spatial Index

## Installation

### Automated Setup (Recommended)

1. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/esda-web-mapping-boilerplate.git
   cd esda-web-mapping-boilerplate
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

3. **Install Dependencies**
   ```bash
   make setup
   ```

4. **Start Development Environment**
   ```bash
   make dev
   ```

### Manual Setup

1. **Backend Setup**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

3. **Start Services**
   ```bash
   # In one terminal (backend)
   ./scripts/run_backend.sh
   
   # In another terminal (frontend)
   ./scripts/run_frontend.sh
   ```

## Configuration

### Environment Variables

Key environment variables in `.env`:

```ini
# Backend
BACKEND_PORT=8000
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/esda_db

# Frontend
FRONTEND_PORT=3000
VITE_API_URL=http://localhost:8000
```

### Database Setup

1. **PostgreSQL with PostGIS**
   ```bash
   # Install PostGIS extension
   psql -d your_database -c "CREATE EXTENSION postgis;"
   ```

2. **Run Migrations**
   ```bash
   make migrate
   ```

## Development Tools

### Available Make Commands
- `make setup` - Initial project setup
- `make dev` - Start development environment
- `make test` - Run all tests
- `make lint` - Run linters
- `make format` - Format code
- `make clean` - Clean build artifacts
- `make build` - Build for production
- `make migrate` - Run database migrations

### Code Quality Tools
- Pre-commit hooks
- ESLint (JavaScript/TypeScript)
- Black (Python)
- MyPy (Python type checking)

## Troubleshooting

### Common Issues

1. **GDAL Installation Problems**
   ```bash
   # If GDAL installation fails, try:
   pip install --global-option=build_ext --global-option="-I/usr/include/gdal" GDAL==<version>
   ```

2. **Node.js Dependencies Issues**
   ```bash
   # Clear npm cache
   npm cache clean --force
   rm -rf node_modules
   npm install
   ```

3. **Python Virtual Environment Issues**
   ```bash
   # If venv creation fails
   python -m pip install --upgrade pip
   python -m pip install virtualenv
   python -m virtualenv venv
   ```

4. **Database Connection Issues**
   - Check PostgreSQL service is running
   - Verify database credentials in `.env`
   - Ensure PostGIS extension is installed

### Getting Help
- Check our [FAQ](./faq.md)
- Open an issue on GitHub
- Join our community Discord server

## Next Steps
- Read the [Architecture Overview](./architecture.md)
- Explore [Example Projects](../examples/)
- Review [Contributing Guidelines](../CONTRIBUTING.md)
