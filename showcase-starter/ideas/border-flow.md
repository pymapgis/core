# 🚛 Border Flow Now

**Status**: 🚧 **Open for Implementation** - [Claim this issue →](https://github.com/pymapgis/core/issues/new?title=[Showcase]%20Border%20Flow%20Now&labels=showcase,good%20first%20issue)

## Overview
Real-time visualization of truck wait times at US border crossings, helping logistics companies optimize routing and timing for cross-border freight operations.

## Why This Demo?
- **High Business Value** - Directly impacts $700B+ in US-Mexico trade
- **Real-time Data** - CBP updates every 15 minutes
- **Clear Visualization** - Color-coded wait times are immediately actionable
- **Simple Processing** - Straightforward data transformation, perfect for beginners

## Data Sources

| Dataset | Format & URL | Update Frequency |
|---------|--------------|------------------|
| **CBP Border Wait Times** | JSON API - https://bwt.cbp.gov/api/bwtdata | Every 15 minutes |
| **Border Crossing Locations** | Static GeoJSON - https://hifld-geoplatform.opendata.arcgis.com/ | Monthly |

## Core Logic (~35 lines)

```python
# 1. Fetch live wait time data
wait_data = pmg.read("https://bwt.cbp.gov/api/bwtdata")

# 2. Fetch crossing locations (static)
crossings = pmg.read("border_crossings.geojson")

# 3. Join wait times with geographic locations
combined = crossings.merge(wait_data, on='crossing_id')

# 4. Calculate delay score (minutes + congestion factor)
combined['delay_score'] = combined['wait_minutes'] * combined['volume_factor']

# 5. Export for web visualization
combined.to_mvt("tiles/borders/{z}/{x}/{y}.mvt")
combined.to_file("border_status.geojson")
```

## Scoring Formula
**DelayScore = wait_minutes × volume_factor**

Where:
- **wait_minutes** - Current reported wait time
- **volume_factor** - Traffic volume multiplier (1.0-2.5)
  - Light traffic: 1.0
  - Moderate traffic: 1.5  
  - Heavy traffic: 2.0
  - Extreme congestion: 2.5

## Visualization

### Color Scheme
- 🟢 **Green (0-30 min)** - Free flowing, optimal crossing time
- 🟡 **Yellow (30-60 min)** - Moderate delays, plan accordingly
- 🟠 **Orange (60-120 min)** - Significant delays, consider alternatives
- 🔴 **Red (120+ min)** - Severe delays, avoid if possible

### Map Features
- **Border crossing markers** sized by traffic volume
- **Wait time labels** directly on map
- **Trend indicators** (improving/worsening arrows)
- **Facility details** (commercial vs. passenger lanes)

## Sample Data Structure

```json
{
  "crossing_name": "Laredo - World Trade Bridge",
  "crossing_id": "LRD_WTB",
  "state": "TX",
  "coordinates": [-99.4803, 27.4467],
  "commercial_wait": 45,
  "passenger_wait": 15,
  "last_updated": "2024-01-15T14:30:00Z",
  "volume_level": "moderate",
  "delay_score": 67.5
}
```

## Business Impact

### Use Cases
- **Freight Logistics** - Route optimization for time-sensitive cargo
- **Supply Chain** - Just-in-time delivery planning
- **Trade Analysis** - Border efficiency monitoring
- **Economic Research** - Cross-border commerce patterns

### Target Users
- Trucking companies and freight brokers
- Supply chain managers
- Border trade analysts
- Government transportation planners

## Technical Implementation

### Data Processing
1. **API Polling** - Fetch CBP data every 15 minutes
2. **Geocoding** - Match crossing names to coordinates
3. **Trend Analysis** - Calculate wait time changes
4. **Volume Estimation** - Infer traffic levels from patterns

### Web Interface
- **Real-time updates** with WebSocket connections
- **Filtering options** by crossing type, state, wait time
- **Historical charts** showing daily/weekly patterns
- **Export features** for logistics planning

### Performance Considerations
- **Caching** - Store crossing locations locally
- **Rate Limiting** - Respect CBP API limits
- **Fallback Data** - Handle API outages gracefully

## Extensions & Variations

### Enhanced Features
- **Weather Integration** - Factor in border weather conditions
- **Historical Analysis** - Seasonal and daily patterns
- **Predictive Modeling** - Forecast wait times based on trends
- **Mobile Optimization** - Trucker-friendly mobile interface

### Additional Data Sources
- **Traffic Cameras** - Visual confirmation of conditions
- **Social Media** - Real-time reports from drivers
- **Economic Indicators** - Trade volume correlations
- **Holiday Calendars** - Predictable surge periods

### Alternative Visualizations
- **Heatmaps** - Regional delay patterns
- **Flow Lines** - Trade volume visualization
- **Time Series** - Historical wait time trends
- **Comparison Charts** - Crossing efficiency rankings

## Getting Started

### Prerequisites
- Basic Python knowledge
- Understanding of REST APIs
- Familiarity with GeoJSON format

### Implementation Steps
1. **Generate scaffold**: `python scripts/new_demo.py border-flow`
2. **Study CBP API**: Understand data structure and rate limits
3. **Implement worker.py**: Data fetching and processing logic
4. **Customize colors**: Update map styling for wait time ranges
5. **Test locally**: Verify data processing and visualization
6. **Submit PR**: Include screenshot and documentation

### Estimated Time
- **Beginner**: 4-6 hours
- **Intermediate**: 2-3 hours
- **Advanced**: 1-2 hours

## Success Criteria

### Functional Requirements
- ✅ Fetches live CBP wait time data
- ✅ Displays all major border crossings
- ✅ Color-codes by current wait times
- ✅ Updates automatically every 15 minutes
- ✅ Handles API failures gracefully

### Quality Standards
- ✅ Processing completes in < 30 seconds
- ✅ Docker image < 200MB
- ✅ All linting passes (black, flake8)
- ✅ Health check endpoint responds
- ✅ Interactive map loads without errors

## Resources

### Data Documentation
- [CBP Border Wait Times API](https://bwt.cbp.gov/)
- [HIFLD Border Crossings](https://hifld-geoplatform.opendata.arcgis.com/)
- [US-Mexico Border Facts](https://www.trade.gov/us-mexico-border-facts)

### Domain Knowledge
- [Cross-Border Trade Statistics](https://www.bts.gov/browse-statistical-products-and-data/border-crossing-data)
- [NAFTA/USMCA Trade Flows](https://ustr.gov/trade-agreements/free-trade-agreements/united-states-mexico-canada-agreement)
- [Border Infrastructure](https://www.cbp.gov/border-security/ports-entry)

### Technical References
- [REST API Best Practices](https://restfulapi.net/)
- [GeoJSON Specification](https://geojson.org/)
- [MapLibre Styling](https://maplibre.org/maplibre-style-spec/)

## Community Notes

### Difficulty Level
⭐ **Easy** - Great first showcase project!

### Skills Developed
- REST API integration
- Real-time data processing
- Business intelligence visualization
- Cross-border trade domain knowledge

### Potential Mentors
- @logistics-expert - Supply chain industry experience
- @border-analyst - Government trade data specialist
- @pymapgis-team - Technical implementation support

---

**Ready to implement this demo?** 🚀

👉 **[Claim the issue](https://github.com/pymapgis/core/issues/new?title=[Showcase]%20Border%20Flow%20Now&labels=showcase,good%20first%20issue)** - Start your contribution  
👉 **[Generate scaffold](../scripts/new_demo.py)** - `python scripts/new_demo.py border-flow`  
👉 **[Join discussion](https://github.com/pymapgis/core/discussions)** - Get help from the community
