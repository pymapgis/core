#!/usr/bin/env python3
"""
Open311 Pothole Now - San Francisco civic issues tracking
A 35-line microservice that turns SF Open311 data into live civic issue maps
"""

import json
import time
import requests
import pandas as pd
import geopandas as gpd
from pathlib import Path
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def main():
    print("🕳️ Starting Open311 Pothole Now processing...")
    start_time = time.time()
    
    # 1. Fetch live SF Open311 requests data
    print("🚧 Fetching SF Open311 requests data...")
    try:
        requests_data = fetch_sf_open311_requests()
        print(f"✅ Fetched {len(requests_data)} civic requests")
    except Exception as e:
        print(f"⚠️ Error fetching Open311 data: {e}")
        requests_data = create_mock_requests_data()
    
    # 2. Filter for street/sidewalk defects (potholes, etc.)
    print("🛣️ Filtering for street and sidewalk defects...")
    street_defects = filter_street_defects(requests_data)
    print(f"✅ Found {len(street_defects)} street/sidewalk issues")
    
    if len(street_defects) == 0:
        print("🎭 No street defects found, creating sample data...")
        street_defects = create_sample_defects()
    
    # 3. Convert to GeoDataFrame and calculate age
    defects_df = pd.DataFrame(street_defects)
    defects_gdf = gpd.GeoDataFrame(
        defects_df,
        geometry=gpd.points_from_xy(defects_df.longitude, defects_df.latitude),
        crs='EPSG:4326'
    )
    
    # 4. Calculate issue age and priority
    print("📊 Calculating issue age and priority...")
    for idx, issue in defects_gdf.iterrows():
        age_days = calculate_issue_age(issue.get('requested_datetime', ''))
        priority = calculate_priority(age_days, issue.get('service_name', ''))
        
        defects_gdf.at[idx, 'age_days'] = age_days
        defects_gdf.at[idx, 'priority'] = priority
        defects_gdf.at[idx, 'age_category'] = classify_age_category(age_days)
        defects_gdf.at[idx, 'status_category'] = classify_status(issue.get('status', 'Open'))
    
    # 5. Export results
    print("📤 Exporting results...")
    
    # Export street defects
    defects_output = "sf_street_defects.geojson"
    defects_gdf.to_file(defects_output, driver="GeoJSON")
    print(f"✅ Exported street defects: {defects_output}")
    
    # Export combined JSON for API
    api_data = {
        "street_defects": json.loads(defects_gdf.to_json()),
        "summary": {
            "total_issues": int(len(defects_gdf)),
            "open_issues": int(len(defects_gdf[defects_gdf['status_category'] == 'Open'])),
            "closed_issues": int(len(defects_gdf[defects_gdf['status_category'] == 'Closed'])),
            "high_priority": int(len(defects_gdf[defects_gdf['priority'] == 'High'])),
            "avg_age_days": float(round(defects_gdf['age_days'].mean(), 1)),
            "oldest_issue_days": float(defects_gdf['age_days'].max())
        }
    }
    
    with open("open311_latest.json", "w") as f:
        json.dump(api_data, f, indent=2)
    
    # Create visualization with lighter styling
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.patch.set_facecolor('white')
    
    # Plot 1: Issues by age
    defects_gdf.plot(
        column='age_days',
        cmap='Reds',
        alpha=0.7,
        legend=True,
        ax=ax1,
        markersize=30
    )
    ax1.set_title("SF Street Defects - Age Analysis", fontsize=14, fontweight='bold', color='#2c3e50')
    ax1.set_xlabel("Longitude", color='#34495e')
    ax1.set_ylabel("Latitude", color='#34495e')
    ax1.set_facecolor('#f8f9fa')
    
    # Plot 2: Issues by priority
    defects_gdf.plot(
        column='priority',
        categorical=True,
        legend=True,
        ax=ax2,
        markersize=30,
        alpha=0.8,
        cmap='Set3'
    )
    ax2.set_title("Priority Analysis", fontsize=14, fontweight='bold', color='#2c3e50')
    ax2.set_xlabel("Longitude", color='#34495e')
    ax2.set_ylabel("Latitude", color='#34495e')
    ax2.set_facecolor('#f8f9fa')
    
    plt.tight_layout()
    plt.savefig("sf_street_defects.png", dpi=120, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✅ Exported visualization: sf_street_defects.png")
    
    # 6. Summary statistics
    processing_time = time.time() - start_time
    open_issues = len(defects_gdf[defects_gdf['status_category'] == 'Open'])
    high_priority = len(defects_gdf[defects_gdf['priority'] == 'High'])
    avg_age = defects_gdf['age_days'].mean()
    
    print("🎉 Open311 Pothole Now processing completed!")
    print(f"🕳️ Processed {len(defects_gdf)} street defects")
    print(f"🚧 Open issues: {open_issues}")
    print(f"⏱️ Processing time: {processing_time:.2f} seconds")
    print(f"📈 Average age: {avg_age:.1f} days")
    print(f"🔴 High priority: {high_priority}")

def fetch_sf_open311_requests():
    """Fetch live SF Open311 requests data"""
    try:
        url = "https://mobile311.sfgov.org/open311/v2/requests.json?service_code=STREET_OR_SIDEWALK_DEFECT"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"⚠️ SF Open311 API error: {e}")
        return []

def filter_street_defects(requests_data):
    """Filter for street and sidewalk defects"""
    if not requests_data:
        return []
    
    street_defects = []
    for request in requests_data:
        # Check if request has required fields
        if not all(key in request for key in ['lat', 'long']):
            continue
        
        # Check if it's a street/sidewalk defect
        service_name = request.get('service_name', '').lower()
        if not any(keyword in service_name for keyword in ['street', 'sidewalk', 'pothole', 'pavement']):
            continue
            
        try:
            lat = float(request['lat'])
            lon = float(request['long'])
            
            # Basic SF bounds check
            if not (37.7 <= lat <= 37.8 and -122.5 <= lon <= -122.3):
                continue
                
            street_defects.append({
                'service_request_id': request.get('service_request_id', 'Unknown'),
                'service_name': request.get('service_name', 'Street Defect'),
                'description': request.get('description', 'Street or sidewalk issue'),
                'status': request.get('status', 'Open'),
                'requested_datetime': request.get('requested_datetime', ''),
                'updated_datetime': request.get('updated_datetime', ''),
                'address': request.get('address', 'SF Location'),
                'latitude': lat,
                'longitude': lon
            })
        except (ValueError, TypeError):
            continue
    
    return street_defects

def calculate_issue_age(requested_datetime):
    """Calculate age of issue in days"""
    if not requested_datetime:
        return 30  # Default age
    
    try:
        # Parse datetime (format may vary)
        if 'T' in requested_datetime:
            request_date = datetime.fromisoformat(requested_datetime.replace('Z', '+00:00'))
        else:
            request_date = datetime.strptime(requested_datetime, '%Y-%m-%d %H:%M:%S')
        
        age = (datetime.now() - request_date.replace(tzinfo=None)).days
        return max(0, age)
    except:
        return 30  # Default age if parsing fails

def calculate_priority(age_days, service_name):
    """Calculate priority based on age and service type"""
    service_lower = service_name.lower()
    
    # Base priority on service type
    if 'pothole' in service_lower or 'pavement' in service_lower:
        base_priority = 'High'
    elif 'sidewalk' in service_lower:
        base_priority = 'Medium'
    else:
        base_priority = 'Low'
    
    # Increase priority based on age
    if age_days > 90:
        return 'High'
    elif age_days > 30 and base_priority != 'Low':
        return 'High'
    elif age_days > 14:
        return 'Medium'
    else:
        return base_priority

def classify_age_category(age_days):
    """Classify age into categories"""
    if age_days <= 7:
        return 'Fresh'
    elif age_days <= 30:
        return 'Recent'
    elif age_days <= 90:
        return 'Old'
    else:
        return 'Very Old'

def classify_status(status):
    """Classify status into simplified categories"""
    status_lower = status.lower()
    if 'closed' in status_lower or 'resolved' in status_lower:
        return 'Closed'
    elif 'progress' in status_lower or 'assigned' in status_lower:
        return 'In Progress'
    else:
        return 'Open'

def create_sample_defects():
    """Create sample street defect data for demo"""
    sample_defects = [
        {'service_request_id': 'SF001', 'service_name': 'Pothole Repair', 'description': 'Large pothole on Market Street', 'status': 'Open', 'requested_datetime': '2024-05-15T10:00:00', 'address': 'Market St & 4th St', 'latitude': 37.7749, 'longitude': -122.4194},
        {'service_request_id': 'SF002', 'service_name': 'Sidewalk Repair', 'description': 'Cracked sidewalk near bus stop', 'status': 'In Progress', 'requested_datetime': '2024-05-20T14:30:00', 'address': 'Mission St & 2nd St', 'latitude': 37.7849, 'longitude': -122.4094},
        {'service_request_id': 'SF003', 'service_name': 'Street Defect', 'description': 'Uneven pavement causing safety hazard', 'status': 'Open', 'requested_datetime': '2024-05-10T09:15:00', 'address': 'Folsom St & 3rd St', 'latitude': 37.7649, 'longitude': -122.4294},
        {'service_request_id': 'SF004', 'service_name': 'Pothole Repair', 'description': 'Multiple potholes in intersection', 'status': 'Closed', 'requested_datetime': '2024-04-25T16:45:00', 'address': 'Howard St & 1st St', 'latitude': 37.7949, 'longitude': -122.3994},
        {'service_request_id': 'SF005', 'service_name': 'Sidewalk Repair', 'description': 'Broken sidewalk tiles', 'status': 'Open', 'requested_datetime': '2024-05-25T11:20:00', 'address': 'Brannan St & 5th St', 'latitude': 37.7549, 'longitude': -122.4394}
    ]
    return sample_defects

def create_mock_requests_data():
    """Create mock Open311 requests data for demo"""
    return [
        {'service_request_id': 'MOCK001', 'service_name': 'Street or Sidewalk Defect', 'description': 'Demo pothole', 'status': 'Open', 'requested_datetime': '2024-05-15T10:00:00', 'lat': '37.7749', 'long': '-122.4194', 'address': 'Market St'},
        {'service_request_id': 'MOCK002', 'service_name': 'Street or Sidewalk Defect', 'description': 'Demo sidewalk issue', 'status': 'Open', 'requested_datetime': '2024-05-20T14:30:00', 'lat': '37.7849', 'long': '-122.4094', 'address': 'Mission St'},
    ]

if __name__ == "__main__":
    main()
