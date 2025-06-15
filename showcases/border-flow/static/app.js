/**
 * Border Flow Now - Interactive Map
 *
 * Real-time CBP truck wait map powered by PyMapGIS.
 * Shows live border crossing congestion with color-coded wait times.
 */

// Configuration for border crossing visualization
const CONFIG = {
    // Map settings - focused on US-Mexico border
    center: [-103, 29], // Centered on border region
    zoom: 4,

    // Data settings
    layerName: 'bwt',           // Border Wait Times layer
    scoreField: 'Score',        // Congestion score field
    waitField: 'wait',          // Wait time in minutes
    nameField: 'name',          // Crossing name
    lanesField: 'lanes',        // Number of commercial lanes

    // Color scheme - traffic light colors for wait times
    colors: {
        low: '#00d084',      // Green - free flowing
        medium: '#ffdd00',   // Yellow - moderate delays
        high: '#ff6f00',     // Orange - heavy delays
        extreme: '#e60000'   // Red - severe delays
    },

    // Wait time ranges (minutes) for color mapping
    ranges: {
        low: 20,        // 0-20 minutes
        medium: 40,     // 20-40 minutes
        high: 60,       // 40-60 minutes
        extreme: 120    // 60+ minutes
    }
};

// Initialize the map with dark theme for logistics/professional look
const map = new maplibregl.Map({
    container: 'map',
    style: {
        version: 8,
        sources: {
            'carto-dark': {
                type: 'raster',
                tiles: ['https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png'],
                tileSize: 256,
                attribution: '© CARTO © OpenStreetMap contributors'
            }
        },
        layers: [{
            id: 'background',
            type: 'raster',
            source: 'carto-dark'
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

    // Add the border wait times data source
    map.addSource('bwt', {
        type: 'vector',
        tiles: [window.location.origin + `/public/tiles/{z}/{x}/{y}.pbf`],
        minzoom: 0,
        maxzoom: 10
    });

    // Add the border crossing wait time layer
    map.addLayer({
        id: 'wait-circles',
        type: 'circle',
        source: 'bwt',
        'source-layer': CONFIG.layerName,
        paint: {
            // Circle radius based on congestion score (log1p(wait) * lanes)
            'circle-radius': [
                'interpolate',
                ['linear'],
                ['get', CONFIG.scoreField],
                0, 4,                           // Minimum size
                20, 20                          // Maximum size for high congestion
            ],

            // Circle color based on wait time (traffic light scheme)
            'circle-color': [
                'interpolate',
                ['linear'],
                ['get', CONFIG.waitField],
                0, CONFIG.colors.low,           // Green: 0-20 min
                CONFIG.ranges.low, CONFIG.colors.medium,     // Yellow: 20-40 min
                CONFIG.ranges.medium, CONFIG.colors.high,   // Orange: 40-60 min
                CONFIG.ranges.high, CONFIG.colors.extreme   // Red: 60+ min
            ],

            // Circle styling for visibility on dark background
            'circle-opacity': 0.8,
            'circle-stroke-width': 2,
            'circle-stroke-color': '#ffffff',
            'circle-stroke-opacity': 0.9
        }
    });

    // Add hover effects for border crossings
    map.on('mouseenter', 'wait-circles', () => {
        map.getCanvas().style.cursor = 'pointer';
    });

    map.on('mouseleave', 'wait-circles', () => {
        map.getCanvas().style.cursor = '';
    });

    // Add click interactions for border crossing details
    map.on('click', 'wait-circles', (e) => {
        const feature = e.features[0];
        const props = feature.properties;

        // Format wait time with appropriate styling
        const waitTime = parseInt(props[CONFIG.waitField] || 0);
        const waitClass = waitTime > 60 ? 'text-red-600 font-bold' :
                         waitTime > 40 ? 'text-orange-600 font-semibold' :
                         waitTime > 20 ? 'text-yellow-600 font-semibold' : 'text-green-600 font-semibold';

        // Create popup content with border crossing details
        const popupContent = `
            <div class="p-3 min-w-64">
                <h3 class="font-bold text-lg text-gray-800 mb-2">🚛 ${props[CONFIG.nameField] || 'Border Crossing'}</h3>
                <div class="space-y-2 text-sm">
                    <div class="flex justify-between">
                        <span class="text-gray-600">Truck Wait:</span>
                        <span class="${waitClass}">${waitTime} minutes</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600">Commercial Lanes:</span>
                        <span class="font-semibold">${props[CONFIG.lanesField] || 'N/A'}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600">Congestion Score:</span>
                        <span class="font-semibold">${parseFloat(props[CONFIG.scoreField] || 0).toFixed(1)}</span>
                    </div>
                    ${props.state ? `<div class="flex justify-between">
                        <span class="text-gray-600">State:</span>
                        <span class="font-semibold">${props.state}</span>
                    </div>` : ''}
                </div>
                <div class="mt-3 pt-2 border-t border-gray-200">
                    <p class="text-xs text-gray-500">
                        ${waitTime <= 20 ? '✅ Good time to cross' :
                          waitTime <= 40 ? '⚠️ Moderate delays expected' :
                          waitTime <= 60 ? '🚨 Significant delays' : '🛑 Severe congestion'}
                    </p>
                </div>
            </div>
        `;

        // Show popup
        new maplibregl.Popup({
            closeButton: true,
            closeOnClick: true,
            maxWidth: '320px'
        })
        .setLngLat(e.lngLat)
        .setHTML(popupContent)
        .addTo(map);
    });

    // Load metadata and update UI
    loadMetadata();
});

// Function to load and display border crossing metadata
async function loadMetadata() {
    try {
        const response = await fetch('/health');
        const health = await response.json();

        // Update crossing count
        document.getElementById('feature-count').textContent =
            health.checks.crossings_count.toLocaleString();

        // Update last update time
        const updateTime = new Date(health.timestamp);
        document.getElementById('last-update').textContent =
            updateTime.toLocaleString();

    } catch (error) {
        console.error('Error loading border crossing metadata:', error);
        document.getElementById('feature-count').textContent = 'Error';
        document.getElementById('last-update').textContent = 'Error';
    }
}

// Auto-refresh border wait times every 5 minutes (CBP updates every 15 min)
setInterval(() => {
    // Refresh the border wait times source
    if (map.getSource('bwt')) {
        map.getSource('bwt').setTiles([
            window.location.origin + `/public/tiles/{z}/{x}/{y}.pbf?t=${Date.now()}`
        ]);
    }

    // Refresh metadata
    loadMetadata();
}, 5 * 60 * 1000); // 5 minutes

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
