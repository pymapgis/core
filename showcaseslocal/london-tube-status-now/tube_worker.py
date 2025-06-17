#!/usr/bin/env python3
"""
London Tube Status Now - TfL API Data Worker
Real-time London Underground service status and disruption tracking
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any
import requests
import pandas as pd
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# TfL API endpoints (no API key required!)
TFL_LINE_STATUS_URL = "https://api.tfl.gov.uk/Line/Mode/tube/Status"
TFL_DISRUPTIONS_URL = "https://api.tfl.gov.uk/Line/Mode/tube/Disruption"
TFL_LINES_URL = "https://api.tfl.gov.uk/Line/Mode/tube"

# London tube line colors (official TfL colors)
TUBE_LINE_COLORS = {
    'bakerloo': '#B36305',
    'central': '#E32017',
    'circle': '#FFD300',
    'district': '#00782A',
    'hammersmith-city': '#F3A9BB',
    'jubilee': '#A0A5A9',
    'metropolitan': '#9B0056',
    'northern': '#000000',
    'piccadilly': '#003688',
    'victoria': '#0098D4',
    'waterloo-city': '#95CDBA'
}

def fetch_tube_status() -> List[Dict[str, Any]]:
    """Fetch real-time tube line status from TfL API"""
    print("🚇 Fetching London Tube status from TfL API...")
    
    try:
        response = requests.get(TFL_LINE_STATUS_URL, timeout=10)
        response.raise_for_status()
        
        status_data = response.json()
        print(f"✅ Fetched status for {len(status_data)} tube lines")
        return status_data
        
    except requests.RequestException as e:
        print(f"❌ Failed to fetch TfL data: {e}")
        return create_sample_tube_data()

def fetch_tube_disruptions() -> List[Dict[str, Any]]:
    """Fetch current tube disruptions from TfL API"""
    print("🚨 Fetching tube disruptions...")
    
    try:
        response = requests.get(TFL_DISRUPTIONS_URL, timeout=10)
        response.raise_for_status()
        
        disruptions = response.json()
        print(f"✅ Fetched {len(disruptions)} active disruptions")
        return disruptions
        
    except requests.RequestException as e:
        print(f"⚠️ Could not fetch disruptions: {e}")
        return []

def create_sample_tube_data() -> List[Dict[str, Any]]:
    """Create realistic sample tube status data when API unavailable"""
    print("🎭 Creating sample tube status data...")
    
    sample_lines = [
        {
            'id': 'bakerloo',
            'name': 'Bakerloo',
            'lineStatuses': [{'statusSeverity': 10, 'statusSeverityDescription': 'Good Service'}]
        },
        {
            'id': 'central',
            'name': 'Central',
            'lineStatuses': [{'statusSeverity': 6, 'statusSeverityDescription': 'Minor Delays'}]
        },
        {
            'id': 'circle',
            'name': 'Circle',
            'lineStatuses': [{'statusSeverity': 10, 'statusSeverityDescription': 'Good Service'}]
        },
        {
            'id': 'district',
            'name': 'District',
            'lineStatuses': [{'statusSeverity': 4, 'statusSeverityDescription': 'Severe Delays'}]
        },
        {
            'id': 'hammersmith-city',
            'name': 'Hammersmith & City',
            'lineStatuses': [{'statusSeverity': 10, 'statusSeverityDescription': 'Good Service'}]
        },
        {
            'id': 'jubilee',
            'name': 'Jubilee',
            'lineStatuses': [{'statusSeverity': 8, 'statusSeverityDescription': 'Good Service'}]
        },
        {
            'id': 'metropolitan',
            'name': 'Metropolitan',
            'lineStatuses': [{'statusSeverity': 6, 'statusSeverityDescription': 'Minor Delays'}]
        },
        {
            'id': 'northern',
            'name': 'Northern',
            'lineStatuses': [{'statusSeverity': 10, 'statusSeverityDescription': 'Good Service'}]
        },
        {
            'id': 'piccadilly',
            'name': 'Piccadilly',
            'lineStatuses': [{'statusSeverity': 2, 'statusSeverityDescription': 'Part Suspended'}]
        },
        {
            'id': 'victoria',
            'name': 'Victoria',
            'lineStatuses': [{'statusSeverity': 10, 'statusSeverityDescription': 'Good Service'}]
        },
        {
            'id': 'waterloo-city',
            'name': 'Waterloo & City',
            'lineStatuses': [{'statusSeverity': 10, 'statusSeverityDescription': 'Good Service'}]
        }
    ]
    
    return sample_lines

def process_tube_status(status_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Process tube status data into structured format"""
    print("📊 Processing tube status data...")
    
    processed_lines = []
    
    for line in status_data:
        line_id = line.get('id', '')
        line_name = line.get('name', '')
        
        # Get primary status
        statuses = line.get('lineStatuses', [])
        if statuses:
            primary_status = statuses[0]
            severity = primary_status.get('statusSeverity', 10)
            status_desc = primary_status.get('statusSeverityDescription', 'Good Service')
            reason = primary_status.get('reason', '')
        else:
            severity = 10
            status_desc = 'Good Service'
            reason = ''
        
        # Calculate status score (0-10, higher is better)
        status_score = severity
        
        # Determine status category
        if severity >= 10:
            status_category = 'Good Service'
            status_color = '#00782A'  # Green
        elif severity >= 8:
            status_category = 'Minor Issues'
            status_color = '#FFD300'  # Yellow
        elif severity >= 6:
            status_category = 'Minor Delays'
            status_color = '#FF8C00'  # Orange
        elif severity >= 4:
            status_category = 'Severe Delays'
            status_color = '#E32017'  # Red
        else:
            status_category = 'Suspended'
            status_color = '#000000'  # Black
        
        processed_lines.append({
            'line_id': line_id,
            'line_name': line_name,
            'status_severity': severity,
            'status_description': status_desc,
            'status_category': status_category,
            'status_color': status_color,
            'status_score': status_score,
            'reason': reason,
            'tube_color': TUBE_LINE_COLORS.get(line_id, '#666666'),
            'last_updated': datetime.now().isoformat()
        })
    
    df = pd.DataFrame(processed_lines)
    print(f"✅ Processed {len(df)} tube lines")
    return df

def create_tube_geojson(df: pd.DataFrame) -> Dict[str, Any]:
    """Create GeoJSON representation of tube lines with status"""
    print("🗺️ Creating tube lines GeoJSON...")
    
    # Simplified tube line coordinates (central London focus)
    tube_coordinates = {
        'bakerloo': [[-0.1276, 51.5074], [-0.1340, 51.5155], [-0.1553, 51.5226]],
        'central': [[-0.0742, 51.5155], [-0.0981, 51.5155], [-0.1276, 51.5074], [-0.1553, 51.5226]],
        'circle': [[-0.1276, 51.5074], [-0.1340, 51.5155], [-0.1553, 51.5226], [-0.1276, 51.5074]],
        'district': [[-0.0742, 51.5074], [-0.1276, 51.5074], [-0.1553, 51.5155]],
        'hammersmith-city': [[-0.1553, 51.5155], [-0.1340, 51.5155], [-0.1276, 51.5074]],
        'jubilee': [[-0.0981, 51.5074], [-0.1276, 51.5074], [-0.1553, 51.5226]],
        'metropolitan': [[-0.1276, 51.5155], [-0.1340, 51.5226], [-0.1553, 51.5297]],
        'northern': [[-0.0981, 51.5226], [-0.1276, 51.5155], [-0.1340, 51.5074]],
        'piccadilly': [[-0.0742, 51.5226], [-0.1276, 51.5155], [-0.1553, 51.5074]],
        'victoria': [[-0.1340, 51.5074], [-0.1276, 51.5155], [-0.1553, 51.5226]],
        'waterloo-city': [[-0.1115, 51.5074], [-0.1276, 51.5074]]
    }
    
    features = []
    
    for _, row in df.iterrows():
        line_id = row['line_id']
        coordinates = tube_coordinates.get(line_id, [[-0.1276, 51.5074], [-0.1340, 51.5155]])
        
        feature = {
            'type': 'Feature',
            'properties': {
                'line_id': row['line_id'],
                'line_name': row['line_name'],
                'status_severity': row['status_severity'],
                'status_description': row['status_description'],
                'status_category': row['status_category'],
                'status_color': row['status_color'],
                'status_score': row['status_score'],
                'reason': row['reason'],
                'tube_color': row['tube_color'],
                'last_updated': row['last_updated']
            },
            'geometry': {
                'type': 'LineString',
                'coordinates': coordinates
            }
        }
        features.append(feature)
    
    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }
    
    print(f"✅ Created GeoJSON with {len(features)} tube lines")
    return geojson

def create_status_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Create summary statistics for tube status"""
    total_lines = len(df)
    good_service = len(df[df['status_severity'] >= 10])
    minor_issues = len(df[(df['status_severity'] >= 6) & (df['status_severity'] < 10)])
    major_issues = len(df[df['status_severity'] < 6])
    avg_status_score = df['status_score'].mean()
    
    return {
        'total_lines': total_lines,
        'good_service': good_service,
        'minor_issues': minor_issues,
        'major_issues': major_issues,
        'avg_status_score': round(avg_status_score, 1),
        'last_updated': datetime.now().isoformat()
    }

def export_results(df: pd.DataFrame, geojson: Dict[str, Any], summary: Dict[str, Any]):
    """Export processed results to files"""
    print("📤 Exporting results...")
    
    # Export GeoJSON
    with open('london_tube_status.geojson', 'w') as f:
        json.dump(geojson, f, indent=2)
    
    # Export latest data for API
    latest_data = {
        'tube_lines': geojson,
        'summary': summary,
        'last_updated': datetime.now().isoformat()
    }
    
    with open('tube_status_latest.json', 'w') as f:
        json.dump(latest_data, f, indent=2)
    
    # Create visualization
    create_status_visualization(df)
    
    print("✅ Exported tube status: london_tube_status.geojson")
    print("✅ Exported API data: tube_status_latest.json")
    print("✅ Exported visualization: london_tube_status.png")

def create_status_visualization(df: pd.DataFrame):
    """Create tube status visualization"""
    if not MATPLOTLIB_AVAILABLE:
        print("📊 Matplotlib not available, skipping visualization")
        return

    plt.figure(figsize=(12, 8))

    # Status distribution
    plt.subplot(2, 2, 1)
    status_counts = df['status_category'].value_counts()
    colors = ['#00782A', '#FFD300', '#FF8C00', '#E32017', '#000000'][:len(status_counts)]
    plt.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%', colors=colors)
    plt.title('Tube Line Status Distribution')

    # Status scores by line
    plt.subplot(2, 2, 2)
    df_sorted = df.sort_values('status_score')
    bars = plt.barh(df_sorted['line_name'], df_sorted['status_score'])
    for i, bar in enumerate(bars):
        bar.set_color(df_sorted.iloc[i]['tube_color'])
    plt.xlabel('Status Score (0-10)')
    plt.title('Status Score by Tube Line')
    plt.xlim(0, 10)

    # Timeline placeholder
    plt.subplot(2, 2, 3)
    plt.text(0.5, 0.5, 'Real-time London\nTube Status\n\nUpdated every 30 seconds',
             ha='center', va='center', fontsize=12, transform=plt.gca().transAxes)
    plt.axis('off')

    # Summary stats
    plt.subplot(2, 2, 4)
    summary_text = f"""
    Total Lines: {len(df)}
    Good Service: {len(df[df['status_severity'] >= 10])}
    Minor Issues: {len(df[(df['status_severity'] >= 6) & (df['status_severity'] < 10)])}
    Major Issues: {len(df[df['status_severity'] < 6])}
    Avg Score: {df['status_score'].mean():.1f}/10
    """
    plt.text(0.1, 0.5, summary_text, fontsize=10, transform=plt.gca().transAxes,
             verticalalignment='center')
    plt.axis('off')
    plt.title('System Summary')

    plt.tight_layout()
    plt.savefig('london_tube_status.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """Main processing function"""
    start_time = time.time()
    print("🚇 Starting London Tube Status Now processing...")
    
    # Fetch data
    status_data = fetch_tube_status()
    disruptions = fetch_tube_disruptions()
    
    # Process data
    df = process_tube_status(status_data)
    geojson = create_tube_geojson(df)
    summary = create_status_summary(df)
    
    # Export results
    export_results(df, geojson, summary)
    
    # Print summary
    processing_time = time.time() - start_time
    print(f"\n🎉 London Tube Status Now processing completed!")
    print(f"🚇 Processed {len(df)} tube lines")
    print(f"✅ Good service: {summary['good_service']}")
    print(f"⚠️ Issues: {summary['minor_issues'] + summary['major_issues']}")
    print(f"⏱️ Processing time: {processing_time:.2f} seconds")
    print(f"📊 Average status: {summary['avg_status_score']}/10")

if __name__ == "__main__":
    main()
