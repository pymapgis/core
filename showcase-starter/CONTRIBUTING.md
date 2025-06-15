# 🤝 Contributing to PyMapGIS Showcases

**Thank you for contributing to PyMapGIS!** This guide will help you create amazing geospatial showcase demos that inspire others and demonstrate PyMapGIS capabilities.

## 🎯 What Makes a Great Showcase

A great showcase demo:
- ✅ **Solves a real problem** with geospatial data
- ✅ **Uses public data** (no API keys required)
- ✅ **Completes quickly** (< 60 seconds processing)
- ✅ **Shows visual impact** (interactive web map)
- ✅ **Demonstrates PyMapGIS** core features
- ✅ **Is easy to understand** (~40 lines of core logic)

## 🚀 Quick Contribution Workflow

### 1. Pick or Suggest a Demo Idea
- **Browse existing ideas**: Check [ideas/](ideas/) folder
- **Claim an issue**: Comment "🚀 starting" on a [showcase issue](https://github.com/pymapgis/core/issues?q=is%3Aissue+is%3Aopen+label%3Ashowcase)
- **Suggest new ideas**: [Open an issue](https://github.com/pymapgis/core/issues/new) with `showcase` label

### 2. Generate Your Scaffold
```bash
# Use our scaffold generator
python scripts/new_demo.py your-demo-name

# This creates:
# showcases/your-demo-name/
# ├── worker.py      # Your core logic goes here
# ├── app.py         # FastAPI server (usually no changes needed)
# ├── Dockerfile     # Container config (usually no changes needed)
# └── static/        # Frontend files (customize colors/styling)
```

### 3. Implement Your Demo
- **Edit `worker.py`** - Add your data processing logic (~40 lines)
- **Customize `static/app.js`** - Update map colors and styling
- **Test locally** - `docker build . && docker run -p 8000:8000 your-demo`

### 4. Submit Your PR
- **Include screenshot** - 200×120 pixel image of your map
- **Update documentation** - Add your demo to the main table
- **Pass all checks** - CI must be green (build, lint, size limits)

## 📋 Detailed Requirements

### Code Quality Standards

#### Python Code (worker.py)
```python
# Required header with metadata
# ---
# title: Your Demo Name
# feed: https://data-source-url.com/feed.json
# category: logistics|emergency|environment|transportation
# license: CC0|MIT|Apache-2.0
# ---

import pymapgis as pmg
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data source URLs (must be public, no API keys)
DATA_URL = "https://public-data-source.com/feed.json"

async def main():
    """Main processing function - keep this under 40 lines!"""
    try:
        # 1. Fetch data
        data = pmg.read(DATA_URL)
        
        # 2. Process with PyMapGIS
        # Your core logic here...
        
        # 3. Export results
        data.to_mvt("tiles/layer/{z}/{x}/{y}.mvt")
        data.to_file("output.geojson")
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        # Include fallback test data for demos

if __name__ == "__main__":
    asyncio.run(main())
```

#### Linting Requirements
All code must pass:
- **black** - Code formatting
- **flake8** - Style and error checking  
- **isort** - Import sorting
- **pydocstyle** - Docstring conventions

```bash
# Run locally before submitting
make lint
# or
black worker.py app.py
flake8 worker.py app.py
isort worker.py app.py
pydocstyle worker.py app.py
```

### Docker Requirements

#### Size Limits
- **Final image**: < 200MB
- **Build time**: < 5 minutes on GitHub Actions
- **Runtime memory**: < 512MB for typical datasets

#### Required Dockerfile Structure
```dockerfile
FROM pymapgis/core:latest

# Copy application files
COPY worker.py app.py ./
COPY static/ ./static/

# Create output directories
RUN mkdir -p tiles/layer

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run data processing then start server
CMD python worker.py && uvicorn app:app --host 0.0.0.0 --port 8000
```

### Frontend Requirements

#### Map Visualization (static/app.js)
```javascript
// Required: Color ramp based on your data
'circle-color': [
    'interpolate', ['linear'], ['get', 'your_score_field'],
    min_value, '#color1',
    mid_value, '#color2', 
    max_value, '#color3'
]

// Required: Size scaling
'circle-radius': [
    'interpolate', ['linear'], ['get', 'your_score_field'],
    min_value, 3,
    max_value, 20
]

// Required: Click popup with data
map.on('click', 'your-layer', (e) => {
    const props = e.features[0].properties;
    new maplibregl.Popup()
        .setLngLat(e.lngLat)
        .setHTML(`<h3>${props.title}</h3><p>Score: ${props.score}</p>`)
        .addTo(map);
});
```

### API Requirements

#### Required Endpoints
All demos must implement:
- `GET /` - Interactive map viewer
- `GET /health` - Health check returning JSON status
- `GET /public/tiles/{z}/{x}/{y}.mvt` - Vector tiles (public access)
- `GET /internal/latest` - Full data (JWT protected, optional)

#### Health Check Response
```json
{
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "service": "your-demo-name",
    "version": "1.0.0",
    "checks": {
        "data_file": "ok",
        "tiles": "ok",
        "features_count": 42
    }
}
```

## 🧪 Testing Your Demo

### Local Testing Checklist
- [ ] **Build succeeds**: `docker build -t your-demo .`
- [ ] **Container starts**: `docker run -p 8000:8000 your-demo`
- [ ] **Health check passes**: `curl http://localhost:8000/health`
- [ ] **Map loads**: Open `http://localhost:8000` in browser
- [ ] **Data appears**: See markers/features on the map
- [ ] **Interactions work**: Click features for popups
- [ ] **Processing completes**: Check logs for success messages
- [ ] **Files generated**: Verify tiles/, *.geojson, etc. exist

### CI Testing
Our GitHub Actions will automatically test:
- **Docker build** (must complete in < 5 minutes)
- **Image size** (must be < 200MB)
- **Health endpoint** (must return 200 status)
- **Tile endpoint** (must serve valid MVT data)
- **Code quality** (black, flake8, isort, pydocstyle)

## 📸 Documentation Requirements

### Screenshot
Include a 200×120 pixel screenshot showing:
- Your interactive map with data displayed
- Clear visual differentiation (colors, sizes)
- Representative sample of your dataset
- Save as `screenshot.png` in your demo folder

### Demo Description
Update the main README.md table with:
```markdown
| [🎨 Your Demo](ideas/your-demo.md) | ⭐⭐ Medium | Your Data Source | ✅ Complete |
```

### Idea Documentation
If implementing from `ideas/`, mark the idea as complete:
```markdown
**Status**: ✅ **Implemented** - See [showcases/your-demo/](../showcases/your-demo/)
```

## 🔄 PR Submission Process

### Before Submitting
1. **Test thoroughly** using the checklist above
2. **Run linting** and fix all issues
3. **Add screenshot** to your demo folder
4. **Update documentation** (README tables, idea status)
5. **Write clear commit messages** following conventional commits

### PR Template
```markdown
## 🎯 Demo: Your Demo Name

**Implements**: #issue-number
**Data Source**: https://your-data-source.com
**Category**: logistics|emergency|environment|transportation

### ✅ Checklist
- [ ] Docker build passes (< 200MB)
- [ ] Health check endpoint works
- [ ] Interactive map displays data
- [ ] All linting passes
- [ ] Screenshot included (200×120)
- [ ] Documentation updated

### 📸 Screenshot
![Demo Screenshot](showcases/your-demo/screenshot.png)

### 🧪 Testing
```bash
docker build -t your-demo showcases/your-demo/
docker run -p 8000:8000 your-demo
# Open http://localhost:8000
```

### 📊 Demo Stats
- **Processing time**: ~X seconds
- **Features displayed**: ~X points/polygons
- **Data freshness**: Updates every X hours
- **Geographic coverage**: Global|US|Europe|etc.
```

### Review Process
1. **Automated checks** must pass (CI/CD)
2. **One maintainer review** required
3. **Community feedback** welcome
4. **Merge** triggers automatic Docker Hub publishing

## 🎉 After Your Demo is Merged

### Automatic Benefits
- 🐳 **Docker image published** to `pymapgis/your-demo:latest`
- 🏷️ **GitHub release created** as `showcase/your-demo`
- 📖 **Documentation updated** on the main docs site
- 🎊 **Social media feature** in our monthly community update

### Community Recognition
- Your name in the contributors list
- Demo featured in PyMapGIS blog posts
- Portfolio piece for your professional profile
- Invitation to join our contributor Discord

## 🆘 Getting Help

### Before Asking
1. **Check existing issues** for similar problems
2. **Review the QUICKSTART.md** for basic setup
3. **Test with the reference demo** (quake-impact)

### Where to Ask
- 💬 **General questions**: [GitHub Discussions](https://github.com/pymapgis/core/discussions)
- 🐛 **Bug reports**: [GitHub Issues](https://github.com/pymapgis/core/issues/new?template=bug_report.md)
- 💡 **Feature requests**: [GitHub Issues](https://github.com/pymapgis/core/issues/new?template=feature_request.md)
- 🚀 **Showcase ideas**: [GitHub Issues](https://github.com/pymapgis/core/issues/new) with `showcase` label

### Response Times
- **Critical bugs**: 24-48 hours
- **General questions**: 2-5 days
- **Feature requests**: 1-2 weeks
- **PR reviews**: 3-7 days

## 📜 License and Legal

### Code License
All showcase demos are **dual-licensed** under:
- **Apache License 2.0** 
- **MIT License**

By contributing, you agree to license your code under both licenses.

### Data Attribution
- **Always cite data sources** in your demo documentation
- **Respect data licenses** (prefer CC0, CC-BY, or public domain)
- **No API keys** or proprietary data in public demos
- **Include data freshness** information for users

---

**Ready to contribute?** 🚀

👉 **Start with [QUICKSTART.md](QUICKSTART.md)** to test the system  
👉 **Browse [ideas/](ideas/)** to pick your demo  
👉 **Run `python scripts/new_demo.py your-name`** to get started  

Thank you for helping make PyMapGIS awesome! 🌍✨
