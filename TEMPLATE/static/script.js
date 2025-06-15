// PyMapGIS Showcase Demo Template - JavaScript

/**
 * Demo utility functions and interactive features
 */

// Global demo configuration
const DEMO_CONFIG = {
    mapCenter: [39.8283, -98.5795], // Center of US
    mapZoom: 4,
    apiEndpoint: '/api',
    updateInterval: 30000 // 30 seconds
};

/**
 * Initialize the demo when page loads
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 PyMapGIS Demo Template initialized');
    
    // Initialize components
    initializeControls();
    initializeMap();
    initializeCharts();
    
    // Start periodic updates if needed
    startPeriodicUpdates();
});

/**
 * Initialize interactive controls
 */
function initializeControls() {
    // Add event listeners to form controls
    const controls = document.querySelectorAll('.control-group select, .control-group input');
    controls.forEach(control => {
        control.addEventListener('change', handleControlChange);
    });
    
    // Initialize buttons
    const buttons = document.querySelectorAll('.demo-button');
    buttons.forEach(button => {
        button.addEventListener('click', handleButtonClick);
    });
}

/**
 * Handle control changes
 */
function handleControlChange(event) {
    const control = event.target;
    const value = control.value;
    const name = control.name || control.id;
    
    console.log(`Control changed: ${name} = ${value}`);
    
    // Update visualization based on control change
    updateVisualization(name, value);
}

/**
 * Handle button clicks
 */
function handleButtonClick(event) {
    const button = event.target;
    const action = button.dataset.action;
    
    console.log(`Button clicked: ${action}`);
    
    switch(action) {
        case 'refresh':
            refreshData();
            break;
        case 'export':
            exportData();
            break;
        case 'reset':
            resetDemo();
            break;
        default:
            console.log('Unknown button action:', action);
    }
}

/**
 * Initialize map (placeholder - replace with your map library)
 */
function initializeMap() {
    const mapContainer = document.getElementById('map-container');
    if (!mapContainer) return;
    
    console.log('Initializing map...');
    
    // Example with Leaflet (uncomment if using Leaflet)
    /*
    const map = L.map('map-container').setView(DEMO_CONFIG.mapCenter, DEMO_CONFIG.mapZoom);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    */
    
    // Example with MapLibre GL JS (uncomment if using MapLibre)
    /*
    const map = new maplibregl.Map({
        container: 'map-container',
        style: 'https://demotiles.maplibre.org/style.json',
        center: DEMO_CONFIG.mapCenter,
        zoom: DEMO_CONFIG.mapZoom
    });
    */
}

/**
 * Initialize charts (placeholder - replace with your chart library)
 */
function initializeCharts() {
    const chartContainers = document.querySelectorAll('.chart-container');
    if (chartContainers.length === 0) return;
    
    console.log('Initializing charts...');
    
    // Example with Chart.js (uncomment if using Chart.js)
    /*
    chartContainers.forEach((container, index) => {
        const ctx = container.getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Sample 1', 'Sample 2', 'Sample 3'],
                datasets: [{
                    label: 'Sample Data',
                    data: [12, 19, 3],
                    backgroundColor: 'rgba(46, 134, 171, 0.8)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    });
    */
}

/**
 * Update visualization based on user input
 */
function updateVisualization(controlName, value) {
    showLoading();
    
    // Simulate API call or data processing
    setTimeout(() => {
        console.log(`Updating visualization: ${controlName} = ${value}`);
        
        // Update map, charts, metrics, etc.
        updateMetrics();
        hideLoading();
        
        showMessage('Visualization updated successfully', 'success');
    }, 1000);
}

/**
 * Refresh data from API or data source
 */
function refreshData() {
    showLoading();
    
    // Example API call
    fetch(`${DEMO_CONFIG.apiEndpoint}/data`)
        .then(response => response.json())
        .then(data => {
            console.log('Data refreshed:', data);
            updateVisualization('refresh', 'all');
        })
        .catch(error => {
            console.error('Error refreshing data:', error);
            showMessage('Error refreshing data', 'error');
        })
        .finally(() => {
            hideLoading();
        });
}

/**
 * Export current data or visualization
 */
function exportData() {
    console.log('Exporting data...');
    
    // Example: Create and download CSV
    const csvData = generateCSV();
    downloadFile(csvData, 'demo-data.csv', 'text/csv');
    
    showMessage('Data exported successfully', 'success');
}

/**
 * Reset demo to initial state
 */
function resetDemo() {
    console.log('Resetting demo...');
    
    // Reset all controls to default values
    const controls = document.querySelectorAll('.control-group select, .control-group input');
    controls.forEach(control => {
        if (control.type === 'checkbox') {
            control.checked = false;
        } else {
            control.selectedIndex = 0;
        }
    });
    
    // Reset visualization
    updateVisualization('reset', 'default');
    
    showMessage('Demo reset to initial state', 'success');
}

/**
 * Update metrics display
 */
function updateMetrics() {
    const metricCards = document.querySelectorAll('.metric-card');
    metricCards.forEach(card => {
        const valueElement = card.querySelector('.metric-value');
        if (valueElement) {
            // Simulate metric update with random values
            const currentValue = parseInt(valueElement.textContent.replace(/,/g, ''));
            const newValue = Math.floor(currentValue * (0.9 + Math.random() * 0.2));
            valueElement.textContent = newValue.toLocaleString();
        }
    });
}

/**
 * Show loading indicator
 */
function showLoading() {
    const loadingElements = document.querySelectorAll('.loading-spinner');
    loadingElements.forEach(element => {
        element.classList.remove('hidden');
    });
}

/**
 * Hide loading indicator
 */
function hideLoading() {
    const loadingElements = document.querySelectorAll('.loading-spinner');
    loadingElements.forEach(element => {
        element.classList.add('hidden');
    });
}

/**
 * Show message to user
 */
function showMessage(message, type = 'info') {
    const messageContainer = document.getElementById('message-container') || createMessageContainer();
    
    const messageElement = document.createElement('div');
    messageElement.className = `${type}-message`;
    messageElement.textContent = message;
    
    messageContainer.appendChild(messageElement);
    
    // Auto-remove message after 5 seconds
    setTimeout(() => {
        messageElement.remove();
    }, 5000);
}

/**
 * Create message container if it doesn't exist
 */
function createMessageContainer() {
    const container = document.createElement('div');
    container.id = 'message-container';
    container.style.position = 'fixed';
    container.style.top = '20px';
    container.style.right = '20px';
    container.style.zIndex = '1000';
    document.body.appendChild(container);
    return container;
}

/**
 * Generate CSV data for export
 */
function generateCSV() {
    // Example CSV generation - replace with actual data
    const headers = ['Name', 'Value', 'Category'];
    const rows = [
        ['Sample 1', '100', 'Type A'],
        ['Sample 2', '200', 'Type B'],
        ['Sample 3', '150', 'Type A']
    ];
    
    const csvContent = [headers, ...rows]
        .map(row => row.map(field => `"${field}"`).join(','))
        .join('\n');
    
    return csvContent;
}

/**
 * Download file to user's computer
 */
function downloadFile(content, filename, contentType) {
    const blob = new Blob([content], { type: contentType });
    const url = window.URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    window.URL.revokeObjectURL(url);
}

/**
 * Start periodic updates if needed
 */
function startPeriodicUpdates() {
    if (DEMO_CONFIG.updateInterval > 0) {
        setInterval(() => {
            console.log('Periodic update...');
            updateMetrics();
        }, DEMO_CONFIG.updateInterval);
    }
}

/**
 * Utility function to format numbers
 */
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

/**
 * Utility function to format dates
 */
function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Export functions for use in other scripts
window.DemoUtils = {
    updateVisualization,
    refreshData,
    exportData,
    resetDemo,
    showMessage,
    formatNumber,
    formatDate
};
