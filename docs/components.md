# Component Library

## Map Components

### MapContainer
The main container component that orchestrates all map-related functionality.

```typescript
import { MapContainer } from '@/components/Map/MapContainer';

<MapContainer
  config={{
    center: [-98.5795, 39.8283],
    zoom: 4,
    projection: 'EPSG:3857'
  }}
  initialLayers={[
    {
      id: 'states',
      name: 'US States',
      source: {
        type: 'vector',
        url: 'path/to/states.geojson'
      }
    }
  ]}
  onMapLoad={(map) => {}}
  onMapClick={(coords) => {}}
/>
```

### LayerManager
Controls layer visibility, opacity, and ordering.

```typescript
import { LayerManager } from '@/components/Map/LayerManager';

<LayerManager
  layers={layers}
  onLayerChange={(updatedLayers) => {}}
  onStyleChange={(layerId, style) => {}}
/>
```

### DrawingTools
Provides tools for drawing and measuring on the map.

```typescript
import { DrawingTools } from '@/components/Map/DrawingTools';

<DrawingTools
  map={map}
  onDrawComplete={(feature) => {}}
  onMeasureComplete={(measurement) => {}}
/>
```

## Analysis Components

### SpatialAnalysis
Tools for performing spatial analysis operations.

```typescript
import { SpatialAnalysis } from '@/components/Analysis/SpatialAnalysis';

<SpatialAnalysis
  map={map}
  layers={layers}
  onAnalysisComplete={(result) => {}}
/>
```

### NetworkAnalysis
Network-specific analysis tools.

```typescript
import { NetworkAnalysis } from '@/components/Analysis/NetworkAnalysis';

<NetworkAnalysis
  data={networkData}
  onAnalysisComplete={(result) => {}}
  settings={{
    method: 'shortest-path',
    weightField: 'distance'
  }}
/>
```

### StatisticalAnalysis
Statistical analysis and visualization tools.

```typescript
import { StatisticalAnalysis } from '@/components/Analysis/StatisticalAnalysis';

<StatisticalAnalysis
  data={spatialData}
  field="population"
  method="regression"
  onComplete={(stats) => {}}
/>
```

## Visualization Components

### Choropleth
Creates choropleth maps with various classification methods.

```typescript
import { Choropleth } from '@/components/Visualization/Choropleth';

<Choropleth
  data={spatialData}
  field="population"
  classification={{
    method: 'quantile',
    classes: 5
  }}
  colorScheme="YlOrRd"
/>
```

### Heatmap
Generates heatmap visualizations from point data.

```typescript
import { Heatmap } from '@/components/Visualization/Heatmap';

<Heatmap
  points={pointData}
  weightField="intensity"
  radius={30}
  blur={15}
  gradient={{
    0.4: 'blue',
    0.6: 'cyan',
    0.8: 'lime',
    0.9: 'yellow',
    1.0: 'red'
  }}
/>
```

### TimeSeriesVisualization
Animated visualization for temporal data.

```typescript
import { TimeSeriesVisualization } from '@/components/Visualization/TimeSeries';

<TimeSeriesVisualization
  data={temporalData}
  timeField="date"
  valueField="measurement"
  playbackSpeed={1000}
  onTimeChange={(timestamp) => {}}
/>
```

## UI Components

### ControlPanel
Configurable control panel for map tools and settings.

```typescript
import { ControlPanel } from '@/components/UI/ControlPanel';

<ControlPanel
  position="top-right"
  tools={['draw', 'measure', 'analysis']}
  onToolSelect={(tool) => {}}
/>
```

### Legend
Dynamic legend component for map layers.

```typescript
import { Legend } from '@/components/UI/Legend';

<Legend
  layers={visibleLayers}
  style={{
    position: 'bottom-left',
    maxHeight: '200px'
  }}
/>
```

### DataTable
Interactive table for spatial data attributes.

```typescript
import { DataTable } from '@/components/UI/DataTable';

<DataTable
  data={featureCollection}
  columns={[
    { field: 'id', header: 'ID' },
    { field: 'name', header: 'Name' },
    { field: 'population', header: 'Population' }
  ]}
  onRowSelect={(feature) => {}}
  pagination={{
    pageSize: 10,
    totalRecords: 100
  }}
/>
```

## Hooks

### useMap
Custom hook for map interactions.

```typescript
import { useMap } from '@/hooks/useMap';

const {
  map,
  layers,
  handleMapLoad,
  handleMapClick,
  handleMapMove,
  handleLayersChange
} = useMap({
  onMapLoad,
  onMapClick,
  onMapMove,
  onLayersChange
});
```

### useSpatialAnalysis
Hook for spatial analysis operations.

```typescript
import { useSpatialAnalysis } from '@/hooks/useSpatialAnalysis';

const {
  analyze,
  loading,
  results,
  error
} = useSpatialAnalysis({
  method: 'buffer',
  options: {
    distance: 1000,
    units: 'meters'
  }
});
```

### useVisualization
Hook for managing visualizations.

```typescript
import { useVisualization } from '@/hooks/useVisualization';

const {
  style,
  updateStyle,
  createChoropleth,
  createHeatmap,
  loading
} = useVisualization(layer);
```

## Styling

All components support theme customization through:
- TailwindCSS classes
- CSS Modules
- Styled Components
- CSS-in-JS solutions

### Example Theme Customization

```typescript
import { MapContainer } from '@/components/Map/MapContainer';

<MapContainer
  className="custom-map"
  style={{
    height: '500px',
    borderRadius: '8px'
  }}
  theme={{
    primary: '#3B82F6',
    secondary: '#10B981',
    background: '#1F2937'
  }}
/>
```

## Best Practices

1. **Component Composition**
   - Keep components focused and single-responsibility
   - Use composition over inheritance
   - Implement proper prop drilling or context

2. **Performance**
   - Use React.memo for expensive renders
   - Implement proper dependency arrays in hooks
   - Lazy load components when possible

3. **Accessibility**
   - Include ARIA labels
   - Ensure keyboard navigation
   - Maintain proper contrast ratios

4. **Error Handling**
   - Implement error boundaries
   - Provide meaningful error messages
   - Include fallback UI components 