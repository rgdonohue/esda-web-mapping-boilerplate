# API Reference

## Base URL
All API endpoints are prefixed with `/api/v1`

## Authentication
```http
POST /auth/token
```
Obtain JWT token for authentication.

### Request
```json
{
    "username": "string",
    "password": "string"
}
```

### Response
```json
{
    "access_token": "string",
    "token_type": "bearer"
}
```

## Spatial Data Management

### Upload Spatial Data
```http
POST /spatial-data/upload
```
Upload spatial data file (GeoJSON, Shapefile, etc.).

### Parameters
- `file`: The spatial data file
- `type`: File type (geojson, shapefile, etc.)
- `name`: Dataset name

### Response
```json
{
    "id": "integer",
    "name": "string",
    "type": "string",
    "feature_count": "integer",
    "bbox": [xmin, ymin, xmax, ymax]
}
```

### List Spatial Datasets
```http
GET /spatial-data
```

### Response
```json
{
    "datasets": [
        {
            "id": "integer",
            "name": "string",
            "type": "string",
            "feature_count": "integer",
            "created_at": "datetime"
        }
    ]
}
```

## Spatial Analysis

### Network Analysis
```http
GET /statistics/network-analysis/{spatial_data_id}
```
Calculate network metrics and topology statistics.

### Response
```json
{
    "total_length": "float",
    "node_count": "integer",
    "edge_count": "integer",
    "average_edge_length": "float"
}
```

### Spatial Interpolation
```http
GET /statistics/spatial-interpolation/{spatial_data_id}
```

### Parameters
- `method`: Interpolation method (idw, kriging, spline)
- `field`: Field to interpolate
- `resolution`: Output resolution

### Response
```json
{
    "method": "string",
    "resolution": "float",
    "interpolated_values": [
        {
            "coordinates": [x, y],
            "value": "float"
        }
    ]
}
```

### Pattern Analysis
```http
GET /statistics/pattern-analysis/{spatial_data_id}
```

### Parameters
- `method`: Analysis method (quadrat, nearest_neighbor, ripleys_k)

### Response
```json
{
    "method": "string",
    "statistics": {
        "pattern_type": "string",
        "confidence_level": "float",
        "metrics": {}
    }
}
```

## Visualization

### Update Style
```http
POST /visualization/style/{spatial_data_id}
```

### Request
```json
{
    "type": "simple|categorized|graduated",
    "property": "string",
    "style_rules": [
        {
            "value": "any",
            "symbol": {}
        }
    ]
}
```

### Create Choropleth
```http
POST /visualization/choropleth
```

### Request
```json
{
    "spatial_data_id": "integer",
    "field": "string",
    "classification": "natural_breaks|equal_interval|quantile",
    "class_count": "integer"
}
```

### Create Heatmap
```http
POST /visualization/heatmap
```

### Request
```json
{
    "spatial_data_id": "integer",
    "weight_field": "string",
    "radius": "float",
    "blur": "float"
}
```

## Validation

### Validate Geometry
```http
GET /validation/geometry/{spatial_data_id}
```

### Response
```json
{
    "is_valid": "boolean",
    "issues": [
        {
            "type": "string",
            "location": [x, y],
            "description": "string"
        }
    ]
}
```

### Check Topology
```http
GET /validation/topology/{spatial_data_id}
```

### Response
```json
{
    "has_errors": "boolean",
    "topology_errors": [
        {
            "type": "string",
            "features": ["id1", "id2"],
            "location": [x, y]
        }
    ]
}
```

## Error Responses

### 400 Bad Request
```json
{
    "detail": "Error message explaining the problem"
}
```

### 401 Unauthorized
```json
{
    "detail": "Invalid authentication credentials"
}
```

### 404 Not Found
```json
{
    "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
    "detail": "Internal server error"
}
```

## Rate Limiting
- Rate limit: 100 requests per minute
- Rate limit header: `X-RateLimit-Limit`
- Remaining requests: `X-RateLimit-Remaining`
- Reset time: `X-RateLimit-Reset`

## Versioning
API versioning is handled through the URL path. Current version is v1.

## CORS
CORS is enabled for all origins in development and configured per domain in production. 