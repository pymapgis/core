# PyMapGIS Examples

This repository contains before/after demonstrations showing the benefits of using PyMapGIS over traditional geospatial workflows.

## Quick-Win Demos

### 🏭 [Labor-Force Participation Gap](./labor_force_gap/)
Compare traditional GeoPandas + requests workflow vs. PyMapGIS for mapping prime-age labor-force participation rates.

### 🏠 [Housing-Cost Burden Explorer](./housing_cost_burden/)
Compare traditional approach vs. PyMapGIS for mapping housing cost burden (30%+ of income spent on housing).

## Structure

Each demo contains:
- **before/** - Traditional approach using GeoPandas, requests, matplotlib
- **after/** - Modern approach using PyMapGIS

## Data

The `data/` directory contains shared geospatial datasets:
- County boundaries from US Census Bureau (TIGER/Line Shapefiles)

## Running the Examples

### Before (Traditional)
```bash
cd labor_force_gap/before
pip install -r requirements.txt
python app.py YOUR_CENSUS_API_KEY
```

### After (PyMapGIS)
```bash
cd labor_force_gap/after
pip install -r requirements.txt
python app.py
```

## Benefits Demonstrated

- **Reduced boilerplate**: 20+ lines → 10 lines
- **Built-in data sources**: No manual API calls
- **Interactive maps**: HTML output vs. static plots
- **Automatic data handling**: No manual merging/cleaning
- **Modern syntax**: Fluent API design
