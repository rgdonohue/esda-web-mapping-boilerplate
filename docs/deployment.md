# Deployment Guide

## Deployment Options

### 1. Docker Deployment (Recommended)

#### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 20GB disk space

#### Steps

1. **Build and Start Services**
   ```bash
   # Build images
   docker-compose build

   # Start services
   docker-compose up -d
   ```

2. **Verify Deployment**
   ```bash
   # Check service status
   docker-compose ps

   # View logs
   docker-compose logs -f
   ```

3. **Scale Services**
   ```bash
   # Scale backend service
   docker-compose up -d --scale backend=3
   ```

### 2. Kubernetes Deployment

#### Prerequisites
- Kubernetes 1.22+
- kubectl CLI
- Helm 3.0+

#### Steps

1. **Apply Kubernetes Manifests**
   ```bash
   # Apply namespace
   kubectl apply -f k8s/namespace.yaml

   # Apply configurations
   kubectl apply -f k8s/configmaps/
   kubectl apply -f k8s/secrets/

   # Deploy services
   kubectl apply -f k8s/deployments/
   kubectl apply -f k8s/services/
   ```

2. **Verify Deployment**
   ```bash
   # Check pods status
   kubectl get pods -n esda

   # Check services
   kubectl get svc -n esda
   ```

### 3. Manual Deployment

#### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 13+ with PostGIS
- Redis 6+

#### Steps

1. **Backend Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt

   # Run migrations
   alembic upgrade head

   # Start backend service
   gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
   ```

2. **Frontend Setup**
   ```bash
   # Install dependencies
   cd frontend
   npm install

   # Build for production
   npm run build

   # Serve with nginx
   cp nginx.conf /etc/nginx/sites-available/esda
   ln -s /etc/nginx/sites-available/esda /etc/nginx/sites-enabled/
   nginx -t && systemctl restart nginx
   ```

## Environment Configuration

### Production Environment Variables

```ini
# Backend
DEBUG=False
BACKEND_PORT=8000
DATABASE_URL=postgresql://user:pass@db:5432/esda_db
REDIS_URL=redis://redis:6379/0
CORS_ORIGINS=https://yourdomain.com
LOG_LEVEL=INFO

# Frontend
NODE_ENV=production
VITE_API_URL=https://api.yourdomain.com
```

### Security Configuration

1. **SSL/TLS Setup**
   ```bash
   # Generate SSL certificate with Let's Encrypt
   certbot --nginx -d yourdomain.com
   ```

2. **Firewall Configuration**
   ```bash
   # Allow only necessary ports
   ufw allow 80,443/tcp
   ufw allow 8000/tcp  # API port
   ```

## Monitoring and Logging

### 1. Prometheus & Grafana Setup

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=secure_password
```

### 2. ELK Stack Integration

```yaml
# docker-compose.logging.yml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.15.0
    environment:
      - discovery.type=single-node

  logstash:
    image: docker.elastic.co/logstash/logstash:7.15.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: docker.elastic.co/kibana/kibana:7.15.0
    ports:
      - "5601:5601"
```

## Backup and Recovery

### 1. Database Backup

```bash
# Automated backup script
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/path/to/backups

# Backup PostGIS database
pg_dump -Fc esda_db > $BACKUP_DIR/esda_db_$TIMESTAMP.dump

# Rotate old backups
find $BACKUP_DIR -type f -mtime +7 -delete
```

### 2. File Storage Backup

```bash
# Backup uploaded files
rsync -av /path/to/uploads/ /path/to/backups/uploads/

# Backup configuration
cp -r /etc/esda/* /path/to/backups/config/
```

## Performance Optimization

### 1. Nginx Configuration

```nginx
# /etc/nginx/sites-available/esda
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
        expires 1h;
        add_header Cache-Control "public, no-transform";
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_cache_use_stale error timeout http_500 http_502 http_503 http_504;
    }
}
```

### 2. Database Optimization

```sql
-- Create spatial indexes
CREATE INDEX idx_spatial_data_geom ON spatial_data USING GIST (geometry);

-- Analyze tables
ANALYZE spatial_data;

-- Configure PostgreSQL
ALTER SYSTEM SET shared_buffers = '1GB';
ALTER SYSTEM SET work_mem = '50MB';
ALTER SYSTEM SET maintenance_work_mem = '256MB';
```

## Continuous Integration/Deployment

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Build and test
        run: |
          make test
          make build

      - name: Deploy to production
        if: success()
        run: |
          docker-compose -f docker-compose.prod.yml up -d
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   ```bash
   # Check PostgreSQL logs
   tail -f /var/log/postgresql/postgresql-13-main.log

   # Verify connection
   psql -h localhost -U postgres -d esda_db
   ```

2. **Memory Issues**
   ```bash
   # Monitor memory usage
   docker stats

   # Adjust container limits
   docker update --memory 2G --memory-swap 4G container_name
   ```

3. **Network Issues**
   ```bash
   # Check container networking
   docker network inspect esda-network

   # Test connectivity
   docker exec backend ping db
   ```

## Maintenance

### Regular Tasks

1. **Update Dependencies**
   ```bash
   # Backend
   pip-compile requirements.in
   pip-compile requirements-dev.in

   # Frontend
   npm update
   ```

2. **Cleanup**
   ```bash
   # Remove unused Docker resources
   docker system prune -a

   # Clean log files
   find /var/log -name "*.log" -mtime +30 -delete
   ```

3. **Health Checks**
   ```bash
   # Backend health
   curl http://localhost:8000/health

   # Database health
   pg_isready -h localhost -U postgres
   ``` 