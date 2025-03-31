# API Reference

This document provides a comprehensive reference for the ESDA Web Mapping Project API endpoints.

## Base URL

All API endpoints are prefixed with `/api/v1`.

## Authentication

Currently, the API does not require authentication. This may change in future versions.

## Endpoints

### Maps

Endpoints related to map configuration and geospatial data.

#### Get Basemap Configuration

```
GET /api/v1/maps/basemap
```

**Description:** Returns the basemap configuration for the frontend application.

**Response Model:** Dictionary with basemap configuration details

**Example Response:**

```json
{
  "type": "mapbox",
  "style": "mapbox://styles/mapbox/light-v10",
  "center": [-73.935242, 40.730610],
  "zoom": 12
}
```

**Error Responses:**

- `500 Internal Server Error` - Server error occurred while retrieving basemap configuration

## Response Formats

All API responses are returned in JSON format with appropriate HTTP status codes.

## Error Handling

Errors are returned with appropriate HTTP status codes and a JSON body containing:

```json
{
  "detail": "Error message description"
}
```

## Rate Limiting

Currently, there are no rate limits implemented for the API. This may change in future versions.

## Versioning

The API uses versioning in the URL path (e.g., `/api/v1/`) to ensure backward compatibility as the API evolves.

## Caching

The API implements caching for certain endpoints to improve performance. Cached endpoints are marked with the `@cached` decorator.