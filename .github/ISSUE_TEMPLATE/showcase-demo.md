---
name: 🚀 Showcase Demo
about: Propose or claim a new showcase demo implementation
title: '[Showcase] Demo Name - Brief Description'
labels: ['showcase', 'good first issue']
assignees: ''
---

## 🎯 Demo Overview

**Demo Name**: <!-- e.g., "Border Flow Now" -->
**Category**: <!-- logistics/emergency/environment/transportation/other -->
**Difficulty**: <!-- ⭐ Easy / ⭐⭐ Medium / ⭐⭐⭐ Hard -->

**Brief Description**: 
<!-- One sentence describing what this demo does -->

## 📊 Data Source

**Primary Data**: 
- **URL**: <!-- https://api.example.com/data -->
- **Format**: <!-- JSON/GeoJSON/CSV/XML -->
- **Update Frequency**: <!-- Real-time/Hourly/Daily -->
- **API Key Required**: <!-- Yes/No -->

**Secondary Data** (if applicable):
- **URL**: <!-- https://static.example.com/reference.geojson -->
- **Format**: <!-- GeoJSON/Shapefile/etc. -->
- **Purpose**: <!-- Geographic boundaries, reference data, etc. -->

## 🎨 Visualization Concept

**Map Type**: <!-- Point markers/Polygons/Heatmap/Flow lines -->
**Color Scheme**: 
- Low: <!-- #color1 - description -->
- Medium: <!-- #color2 - description -->
- High: <!-- #color3 - description -->
- Extreme: <!-- #color4 - description -->

**Scoring Formula**: 
<!-- e.g., impact = log10(population) × magnitude -->

## 💼 Business Value

**Target Users**: <!-- Who would use this? -->
**Use Cases**: <!-- What problems does it solve? -->
**Impact**: <!-- Why is this valuable? -->

## 🔧 Implementation Plan

### Core Processing (~40 lines)
```python
# Rough pseudocode for the main logic
# 1. Fetch data from API
data = pmg.read("https://api.example.com/data")

# 2. Process/analyze data
# Your domain-specific logic here

# 3. Calculate scores
data['score'] = calculate_score(data)

# 4. Export results
data.to_mvt("tiles/layer/{z}/{x}/{y}.mvt")
data.to_file("output.geojson")
```

### Technical Challenges
<!-- Any specific technical hurdles? -->

### PyMapGIS Features Demonstrated
- [ ] Multi-format data ingestion (`pmg.read`)
- [ ] Async processing (`AsyncGeoProcessor`)
- [ ] Vector tile export (`to_mvt`)
- [ ] Spatial analysis (buffers, joins, etc.)
- [ ] Visualization (`plot.save_png`)

## ✅ Implementation Checklist

**Claiming this issue**: Comment "🚀 starting" to claim
**Estimated time**: <!-- hours for beginner/intermediate/advanced -->

- [ ] Fork TEMPLATE → new folder `/showcases/demo-name/`
- [ ] Implement `worker.py` (≤ 60 LOC core logic)
- [ ] Update `static/app.js` color ramp and styling
- [ ] Customize `static/index.html` with demo-specific content
- [ ] Build `docker build .` (passes, <200MB)
- [ ] Test locally: `docker run -p 8000:8000 demo-name`
- [ ] Add 200×120 screenshot to PR
- [ ] Update root docs table
- [ ] Pass all CI checks (lint, build, health check)

## 📚 Resources

**Domain Knowledge**:
<!-- Links to understand the problem domain -->

**Data Documentation**:
<!-- API docs, data dictionaries, etc. -->

**Similar Projects**:
<!-- Existing tools or visualizations for reference -->

## 🤝 Mentorship

**Looking for help with**:
- [ ] Domain expertise (understanding the data/problem)
- [ ] Technical implementation (PyMapGIS usage)
- [ ] Visualization design (colors, styling)
- [ ] Testing and validation

**Available to mentor others**: <!-- Yes/No and areas of expertise -->

---

**Ready to implement?** Comment "🚀 starting" to claim this issue!

**Need help?** Ask questions in [GitHub Discussions](https://github.com/pymapgis/core/discussions) or tag @pymapgis-team
