/**
 * {{DEMO_TITLE}} - Interactive Map
 * 
 * This file contains the MapLibre GL JS configuration for visualizing
 * your geospatial data. Customize the colors, styling, and interactions
 * to match your demo's theme and data characteristics.
 */

// Configuration - Customize these values for your demo
const CONFIG = {
    // Map settings
    center: [{{DEFAULT_LON}}, {{DEFAULT_LAT}}], // [longitude, latitude]
    zoom: {{DEFAULT_ZOOM}},
    
    // Data settings
    layerName: '{{LAYER_NAME}}',
    scoreField: 'score',  // Field name for your calculated score
    nameField: 'name',    // Field name for feature names
    valueField: 'value',  // Field name for raw values
    
    // Color scheme - customize these colors for your theme
    colors: {
        low: '{{COLOR_LOW}}',       // e.g., '#00bfff'
        medium: '{{COLOR_MEDIUM}}', // e.g., '#ffff00' 
        high: '{{COLOR_HIGH}}',     // e.g., '#ff7e00'
        extreme: '{{COLOR_EXTREME}}' // e.g., '#ff0000'
    },
    
    // Score ranges for color mapping
    ranges: {
        low: {{RANGE_LOW_MAX}},      // e.g., 2
        medium: {{RANGE_MEDIUM_MAX}}, // e.g., 4
        high: {{RANGE_HIGH_MAX}},     // e.g., 6
        extreme: {{RANGE_EXTREME_MAX}} // e.g., 8
    }
};

// Initialize the map
const map = new maplibregl.Map({
    container: 'map',
    style: {
        version: 8,
        sources: {
            'osm': {
                type: 'raster',
                tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
                tileSize: 256,
                attribution: '© OpenStreetMap contributors'
            }
        },
        layers: [{
            id: 'osm',
            type: 'raster',
            source: 'osm'
        }]
    },
    center: CONFIG.center,
    zoom: CONFIG.zoom
});

// Add navigation controls
map.addControl(new maplibregl.NavigationControl(), 'top-right');

// Hide loading indicator when map loads
map.on('load', () => {
    document.getElementById('loading').style.display = 'none';
    
    // Add the data source
    map.addSource('data', {
        type: 'vector',
        tiles: [window.location.origin + `/public/tiles/{z}/{x}/{y}.mvt`],
        minzoom: 0,
        maxzoom: 14
    });

    // Add the main data layer
    map.addLayer({
        id: 'data-circles',
        type: 'circle',
        source: 'data',
        'source-layer': CONFIG.layerName,
        paint: {
            // Circle radius based on score
            'circle-radius': [
                'interpolate',
                ['linear'],
                ['get', CONFIG.scoreField],
                0, 4,                           // Minimum size
                CONFIG.ranges.low, 8,
                CONFIG.ranges.medium, 12,
                CONFIG.ranges.high, 18,
                CONFIG.ranges.extreme, 25       // Maximum size
            ],
            
            // Circle color based on score
            'circle-color': [
                'interpolate',
                ['linear'],
                ['get', CONFIG.scoreField],
                0, CONFIG.colors.low,
                CONFIG.ranges.low, CONFIG.colors.low,
                CONFIG.ranges.medium, CONFIG.colors.medium,
                CONFIG.ranges.high, CONFIG.colors.high,
                CONFIG.ranges.extreme, CONFIG.colors.extreme
            ],
            
            // Circle styling
            'circle-opacity': 0.8,
            'circle-stroke-width': 2,
            'circle-stroke-color': '#ffffff',
            'circle-stroke-opacity': 0.8
        }
    });

    // Add hover effects
    map.on('mouseenter', 'data-circles', () => {
        map.getCanvas().style.cursor = 'pointer';
    });

    map.on('mouseleave', 'data-circles', () => {
        map.getCanvas().style.cursor = '';
    });

    // Add click interactions
    map.on('click', 'data-circles', (e) => {
        const feature = e.features[0];
        const props = feature.properties;
        
        // Create popup content
        const popupContent = `
            <div class="p-3">
                <h3 class="font-bold text-lg text-gray-800 mb-2">${props[CONFIG.nameField] || 'Feature'}</h3>
                <div class="space-y-1 text-sm">
                    <div class="flex justify-between">
                        <span class="text-gray-600">Score:</span>
                        <span class="font-semibold">${parseFloat(props[CONFIG.scoreField] || 0).toFixed(1)}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600">Value:</span>
                        <span class="font-semibold">${parseFloat(props[CONFIG.valueField] || 0).toFixed(1)}</span>
                    </div>
                    ${props.id ? `<div class="flex justify-between">
                        <span class="text-gray-600">ID:</span>
                        <span class="font-mono text-xs">${props.id}</span>
                    </div>` : ''}
                </div>
            </div>
        `;

        // Show popup
        new maplibregl.Popup({
            closeButton: true,
            closeOnClick: true,
            maxWidth: '300px'
        })
        .setLngLat(e.lngLat)
        .setHTML(popupContent)
        .addTo(map);
    });

    // Load metadata and update UI
    loadMetadata();
});

// Function to load and display metadata
async function loadMetadata() {
    try {
        const response = await fetch('/health');
        const health = await response.json();
        
        // Update feature count
        document.getElementById('feature-count').textContent = 
            health.checks.features_count.toLocaleString();
        
        // Update last update time
        const updateTime = new Date(health.timestamp);
        document.getElementById('last-update').textContent = 
            updateTime.toLocaleString();
            
    } catch (error) {
        console.error('Error loading metadata:', error);
        document.getElementById('feature-count').textContent = 'Error';
        document.getElementById('last-update').textContent = 'Error';
    }
}

// Optional: Auto-refresh data every 15 minutes
setInterval(() => {
    // Refresh the map source
    if (map.getSource('data')) {
        map.getSource('data').setTiles([
            window.location.origin + `/public/tiles/{z}/{x}/{y}.mvt?t=${Date.now()}`
        ]);
    }
    
    // Refresh metadata
    loadMetadata();
}, 15 * 60 * 1000); // 15 minutes

// Optional: Fit map to data bounds when data loads
map.on('sourcedata', (e) => {
    if (e.sourceId === 'data' && e.isSourceLoaded) {
        // You can add logic here to fit the map to your data bounds
        // This requires knowing the extent of your data
    }
});

// Error handling
map.on('error', (e) => {
    console.error('Map error:', e);
    document.getElementById('loading').innerHTML = 
        '<div class="text-red-500 text-center">Map loading error</div>';
});

// Export for debugging
window.mapConfig = CONFIG;
window.map = map;
