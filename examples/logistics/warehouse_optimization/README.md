# Warehouse Location Optimization

This example demonstrates how to use PyMapGIS for warehouse location optimization in a logistics network.

## 📖 Backstory

**MegaRetail Corp** operates a chain of stores across the Los Angeles metropolitan area. They currently use multiple small warehouses but want to consolidate into 2-3 strategically located facilities to reduce operational costs while maintaining service levels.

The company has identified 6 potential warehouse sites and needs to determine the optimal combination based on:
- Customer demand volumes and locations
- Delivery distances and transportation costs
- Facility operational costs and capacity constraints
- Transportation network accessibility (highway and rail access)
- Labor availability in different areas

## 🎯 Analysis Objectives

1. **Distance Analysis**: Calculate delivery distances from each potential warehouse to all customers
2. **Efficiency Scoring**: Develop composite efficiency scores considering cost, coverage, and capacity
3. **Service Area Mapping**: Visualize coverage areas for each potential warehouse location
4. **Cost-Benefit Analysis**: Compare monthly operational costs against service coverage
5. **Optimization Recommendations**: Identify the optimal 2-3 warehouse combination

## 📊 Data Description

### Customer Locations (`data/customer_locations.geojson`)
- **12 major customers** across LA metropolitan area
- **Demand volumes** ranging from 720 to 3,200 units
- **Priority levels**: Critical, High, Medium, Low
- **Delivery frequencies**: Multiple daily, Daily, Weekly, Bi-weekly

### Potential Warehouse Sites (`data/potential_warehouses.geojson`)
- **6 candidate locations** strategically positioned
- **Capacity**: 40,000 - 75,000 units
- **Monthly costs**: $65,000 - $120,000
- **Infrastructure**: Highway access, rail connectivity, labor availability

## 🚀 Running the Example

### Prerequisites
```bash
pip install pymapgis geopandas matplotlib folium networkx
```

### Execute the Analysis
```bash
cd examples/logistics/warehouse_optimization
python warehouse_optimization.py
```

### Expected Output
1. **Console Analysis**: Detailed efficiency rankings and recommendations
2. **Visualization**: `warehouse_optimization_analysis.png` with 4 analytical charts:
   - Customer demand distribution map
   - Warehouse service area coverage
   - Efficiency score comparison
   - Cost vs coverage scatter plot

## 📈 Key Metrics Analyzed

### Efficiency Score Calculation
```
Efficiency Score = (Coverage Ratio × 100) / (Weighted Average Distance + Cost per Unit/1000)
```

Where:
- **Coverage Ratio**: Percentage of customers within 25km service radius
- **Weighted Average Distance**: Distance weighted by customer demand volumes
- **Cost per Unit**: Monthly cost divided by warehouse capacity

### Service Coverage
- **Primary Service Area**: 25km radius (optimal delivery zone)
- **Customer Coverage**: Percentage of customers within service area
- **Demand Coverage**: Percentage of total demand volume served

## 🎯 Expected Results

The analysis typically identifies:

1. **Top Performer**: Central LA Industrial Zone (WH_A)
   - Excellent highway access and central location
   - High efficiency score due to balanced cost and coverage

2. **High Capacity Option**: Port Adjacent Facility (WH_B)
   - Largest capacity but higher costs
   - Strategic for import/export operations

3. **Cost-Effective Choice**: East LA Industrial (WH_E)
   - Lowest monthly costs with good rail access
   - Serves eastern customer cluster efficiently

## 🔧 Customization Options

### Modify Analysis Parameters
```python
# Change service area radius
service_areas = create_service_areas(warehouses, max_distance_km=30)

# Adjust efficiency scoring weights
efficiency_score = (coverage_ratio * weight1) / (distance * weight2 + cost * weight3)
```

### Add New Data
- **Customer locations**: Add entries to `customer_locations.geojson`
- **Warehouse sites**: Add candidates to `potential_warehouses.geojson`
- **Demand patterns**: Modify `demand_volume` and `priority` fields

### Enhanced Analysis
- **Network routing**: Replace straight-line distances with road network routing
- **Time-based analysis**: Include traffic patterns and delivery time windows
- **Multi-objective optimization**: Add environmental impact and risk factors

## 🛠️ Technical Implementation

### Core PyMapGIS Features Used
- **`pmg.read()`**: Load GeoJSON data files
- **Geospatial analysis**: Distance calculations and buffer operations
- **Visualization**: Multi-panel analytical charts and maps

### Analysis Workflow
1. **Data Loading**: Import customer and warehouse geospatial data
2. **Distance Matrix**: Calculate all customer-warehouse distances
3. **Efficiency Analysis**: Compute composite efficiency scores
4. **Service Area Modeling**: Create coverage zones around warehouses
5. **Visualization**: Generate comprehensive analytical charts
6. **Recommendations**: Rank and select optimal warehouse combination

## 📋 Business Impact

This analysis helps logistics companies:
- **Reduce operational costs** by 15-25% through optimal facility placement
- **Improve delivery times** with strategic location selection
- **Enhance service coverage** while minimizing infrastructure investment
- **Support data-driven decisions** with quantitative efficiency metrics

## 🔄 Next Steps

1. **Network Analysis**: Integrate real road network data for accurate routing
2. **Demand Forecasting**: Include seasonal and growth projections
3. **Risk Assessment**: Add natural disaster and supply chain risk factors
4. **Multi-period Optimization**: Consider long-term expansion scenarios
