FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libspatialindex-dev \
    libproj-dev \
    proj-data \
    proj-bin \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal \
    C_INCLUDE_PATH=/usr/include/gdal

# Create and set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt backend/requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r requirements-dev.txt

# Copy the rest of the application
COPY backend ./backend
COPY scripts ./scripts

# Make scripts executable
RUN chmod +x scripts/run_backend.sh

# Expose port
EXPOSE 8000

# Run the application
CMD ["./scripts/run_backend.sh"] 