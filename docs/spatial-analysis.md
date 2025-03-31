# Spatial Analysis Guide

## Overview

This guide covers the spatial analysis capabilities available in the ESDA Web Mapping Boilerplate. Each analysis type includes examples, use cases, and best practices.

## Network Analysis

### Shortest Path Analysis
```python
from app.core.spatial_analysis import calculate_network_analysis

result = await calculate_network_analysis(
    spatial_data,
    method="shortest_path",
    start_point=[lon1, lat1],
    end_point=[lon2, lat2],
    weight_field="travel_time"
)
```

### Network Centrality
```python
result = await calculate_network_analysis(
    spatial_data,
    method="centrality",
    metrics=["betweenness", "closeness"],
    weight_field="distance"
)
```

### Service Area Analysis
```python
result = await calculate_network_analysis(
    spatial_data,
    method="service_area",
    facilities=[[lon, lat]],
    break_values=[5, 10, 15],  # minutes
    travel_mode="driving"
)
```

## Spatial Interpolation

### Inverse Distance Weighting (IDW)
```python
from app.core.spatial_analysis import perform_spatial_interpolation

result = await perform_spatial_interpolation(
    spatial_data,
    method="idw",
    field="temperature",
    power=2,
    search_radius=1000,
    resolution=100
)
```

### Kriging
```python
result = await perform_spatial_interpolation(
    spatial_data,
    method="kriging",
    field="rainfall",
    variogram_model="spherical",
    resolution=100
)
```

### Spline Interpolation
```python
result = await perform_spatial_interpolation(
    spatial_data,
    method="spline",
    field="elevation",
    smoothing=0.5,
    resolution=100
)
```

## Pattern Analysis

### Quadrat Analysis
```python
from app.core.spatial_analysis import analyze_spatial_patterns

result = await analyze_spatial_patterns(
    spatial_data,
    method="quadrat",
    cell_size=1000,  # meters
    significance_level=0.05
)
```

### Nearest Neighbor Analysis
```python
result = await analyze_spatial_patterns(
    spatial_data,
    method="nearest_neighbor",
    distance_method="euclidean",
    boundary_correction=True
)
```

### Ripley's K Function
```python
result = await analyze_spatial_patterns(
    spatial_data,
    method="ripleys_k",
    distances=range(100, 1000, 100),
    permutations=99
)
```

## Geostatistics

### Basic Statistics
```python
from app.core.spatial_analysis import calculate_geostatistics

result = await calculate_geostatistics(
    spatial_data,
    field="population",
    statistics=["mean", "std", "skewness", "kurtosis"]
)
```

### Spatial Autocorrelation
```python
result = await calculate_geostatistics(
    spatial_data,
    method="morans_i",
    field="income",
    weights_type="queen"
)
```

### Semivariogram Analysis
```python
result = await calculate_geostatistics(
    spatial_data,
    method="semivariogram",
    field="soil_ph",
    lag_size=100,
    max_lag=1500
)
```

## Spatial Regression

### Ordinary Least Squares
```python
from app.core.spatial_analysis import perform_spatial_regression

result = await perform_spatial_regression(
    spatial_data,
    method="ols",
    dependent="house_price",
    independents=["size", "age", "distance_cbd"]
)
```

### Geographically Weighted Regression
```python
result = await perform_spatial_regression(
    spatial_data,
    method="gwr",
    dependent="crime_rate",
    independents=["income", "education", "unemployment"],
    bandwidth="AIC",
    kernel="gaussian"
)
```

### Spatial Lag Model
```python
result = await perform_spatial_regression(
    spatial_data,
    method="spatial_lag",
    dependent="population_density",
    independents=["employment", "housing_density"],
    weights_type="queen"
)
```

## Best Practices

### Data Preparation
1. **Clean Your Data**
   - Remove duplicates
   - Handle missing values
   - Check for outliers
   ```python
   from app.utils.data_cleaning import clean_spatial_data
   
   cleaned_data = clean_spatial_data(
       spatial_data,
       remove_duplicates=True,
       fill_missing="mean",
       outlier_method="iqr"
   )
   ```

2. **Validate Geometry**
   - Check for invalid geometries
   - Fix topology errors
   ```python
   from app.utils.validation import validate_geometry
   
   validation_result = validate_geometry(
       spatial_data,
       fix_invalid=True,
       check_topology=True
   )
   ```

3. **Project Your Data**
   - Use appropriate coordinate systems
   - Consider the analysis requirements
   ```python
   from app.utils.projection import project_data
   
   projected_data = project_data(
       spatial_data,
       target_crs="EPSG:3857",
       preserve_attributes=True
   )
   ```

### Performance Optimization

1. **Spatial Indexing**
   ```python
   from app.utils.optimization import create_spatial_index
   
   indexed_data = create_spatial_index(
       spatial_data,
       index_type="rtree"
   )
   ```

2. **Chunking Large Datasets**
   ```python
   from app.utils.optimization import process_in_chunks
   
   results = await process_in_chunks(
       spatial_data,
       chunk_size=1000,
       analysis_func=calculate_geostatistics
   )
   ```

3. **Caching Results**
   ```python
   from app.utils.caching import cache_analysis_result
   
   cached_result = await cache_analysis_result(
       key="analysis_123",
       func=perform_spatial_regression,
       expire=3600  # seconds
   )
   ```

### Error Handling

1. **Input Validation**
   ```python
   from app.utils.validation import validate_analysis_inputs
   
   is_valid = validate_analysis_inputs(
       spatial_data,
       required_fields=["population", "income"],
       geometry_type="polygon"
   )
   ```

2. **Progress Monitoring**
   ```python
   from app.utils.monitoring import track_analysis_progress
   
   async with track_analysis_progress() as progress:
       result = await long_running_analysis(
           spatial_data,
           progress_callback=progress.update
       )
   ```

3. **Error Recovery**
   ```python
   from app.utils.error_handling import handle_analysis_error
   
   try:
       result = await perform_analysis()
   except Exception as e:
       handled_result = handle_analysis_error(
           error=e,
           fallback_method="simple_average"
       )
   ```

## Advanced Topics

### Custom Analysis Methods
```python
from app.core.spatial_analysis import register_analysis_method

@register_analysis_method("custom_analysis")
async def my_custom_analysis(spatial_data, **kwargs):
    # Implementation
    return result
```

### Analysis Pipelines
```python
from app.core.pipeline import AnalysisPipeline

pipeline = AnalysisPipeline([
    ("clean", clean_spatial_data),
    ("analyze", perform_spatial_regression),
    ("visualize", create_visualization)
])

result = await pipeline.execute(spatial_data)
```

### Parallel Processing
```python
from app.utils.parallel import parallel_analysis

results = await parallel_analysis(
    spatial_data,
    analysis_func=calculate_geostatistics,
    n_workers=4
)
``` 