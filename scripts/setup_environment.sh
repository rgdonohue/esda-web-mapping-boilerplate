#!/bin/bash

# Script to set up the environment for the ESDA Web Mapping Project

# Create logs directory
mkdir -p logs
echo "Created logs directory"

# Function to create environment-specific .env files
create_env_file() {
    local env_type=$1
    local env_file=".env.${env_type}"
    
    if [ -f "$env_file" ]; then
        echo "$env_file already exists. Skipping."
        return
    fi
    
    echo "Creating $env_file..."
    
    # Common settings
    echo "# Application Environment" > "$env_file"
    echo "ENVIRONMENT=${env_type}" >> "$env_file"
    echo "" >> "$env_file"
    echo "# API Configuration" >> "$env_file"
    echo "API_V1_STR=/api/v1" >> "$env_file"
    echo "PROJECT_NAME=\"ESDA Web Mapping API\"" >> "$env_file"
    
    # Environment-specific settings
    case "$env_type" in
        development)
            echo "BACKEND_CORS_ORIGINS=[\"http://localhost:3000\"]" >> "$env_file"
            echo "LOG_LEVEL=DEBUG" >> "$env_file"
            echo "REDIS_HOST=localhost" >> "$env_file"
            echo "CACHE_TTL=60" >> "$env_file"
            ;;
        testing)
            echo "BACKEND_CORS_ORIGINS=[\"http://localhost:3000\"]" >> "$env_file"
            echo "LOG_LEVEL=INFO" >> "$env_file"
            echo "REDIS_HOST=localhost" >> "$env_file"
            echo "CACHE_TTL=300" >> "$env_file"
            ;;
        production)
            echo "BACKEND_CORS_ORIGINS=[\"https://your-production-domain.com\"]" >> "$env_file"
            echo "LOG_LEVEL=WARNING" >> "$env_file"
            echo "REDIS_HOST=redis" >> "$env_file"
            echo "CACHE_TTL=3600" >> "$env_file"
            ;;
    esac
    
    # Common Redis settings
    echo "" >> "$env_file"
    echo "# Redis Cache Configuration" >> "$env_file"
    echo "REDIS_PORT=6379" >> "$env_file"
    echo "REDIS_DB=0" >> "$env_file"
    echo "REDIS_PASSWORD=" >> "$env_file"
    
    # Logging settings
    echo "" >> "$env_file"
    echo "# Logging Configuration" >> "$env_file"
    echo "LOG_FORMAT=json" >> "$env_file"
    echo "LOG_FILE=logs/app.log" >> "$env_file"
    
    echo "Created $env_file"
}

# Create environment-specific .env files
create_env_file "development"
create_env_file "testing"
create_env_file "production"

# Copy development environment as default .env if it doesn't exist
if [ ! -f ".env" ]; then
    cp ".env.development" ".env"
    echo "Created default .env from .env.development"
fi

echo "Environment setup complete!"