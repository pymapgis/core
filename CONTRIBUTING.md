# Contributing to PyMapGIS

Thank you for your interest in contributing to PyMapGIS! This document provides guidelines and information for contributors.

## 🎯 **Contributor Funnel** - Your Journey to PyMapGIS Mastery

**New to PyMapGIS?** Follow our proven contributor funnel designed to help you become a valuable team member:

### 🎮 **Level 1: Explorer** - Try Our Showcase Demos
**Goal:** Experience PyMapGIS in action
**Time:** 15-30 minutes

1. **🌍 [Quake Impact Now](showcases/quake-impact/)** - Real-time earthquake assessment
2. **📦 [Border Flow Analytics](showcases/border-flow/)** - Trade flow visualization
3. **🏠 [Housing Cost Burden](showcases/housing-cost-burden/)** - Affordability analysis
4. **🚛 [Supply Chain Dashboard](showcases/supply-chain/)** - Logistics optimization

**✅ Level Complete:** You've tried at least 2 demos and understand PyMapGIS capabilities

### 🐛 **Level 2: Reporter** - Find and Report Issues
**Goal:** Help improve existing demos
**Time:** 30-60 minutes

**Good First Issues:**
- [🐛 Bug reports](https://github.com/pymapgis/core/labels/good-first-issue) - Found something broken?
- [📝 Documentation gaps](https://github.com/pymapgis/core/labels/documentation) - Missing or unclear docs?
- [✨ UI/UX improvements](https://github.com/pymapgis/core/labels/ui-ux) - Better user experience ideas?

**✅ Level Complete:** You've reported 1+ issues with detailed descriptions

### 🔧 **Level 3: Fixer** - Contribute Code
**Goal:** Fix bugs and enhance existing features
**Time:** 2-4 hours

**Recommended First Contributions:**
- Fix bugs you reported in Level 2
- Improve documentation based on your experience
- Enhance showcase demo features
- Add tests for existing functionality

**✅ Level Complete:** You've submitted 1+ pull request that gets merged

### 🚀 **Level 4: Builder** - Create New Features
**Goal:** Add significant new capabilities
**Time:** 1-2 weeks

**Advanced Contributions:**
- [⚡ Performance optimizations](https://github.com/pymapgis/core/labels/performance)
- [🌐 New data source integrations](https://github.com/pymapgis/core/labels/data-sources)
- [🔧 Advanced features](https://github.com/pymapgis/core/labels/stretch)
- Create new showcase demos

**✅ Level Complete:** You've contributed major features and are recognized as a core contributor

### 🏆 **Level 5: Leader** - Community Leadership
**Goal:** Help guide PyMapGIS direction
**Time:** Ongoing

**Leadership Opportunities:**
- Mentor new contributors through the funnel
- Lead showcase demo development
- Participate in architectural decisions
- Represent PyMapGIS at conferences/events

**✅ Level Complete:** You're a PyMapGIS team member with commit access

## 🎁 **Contributor Recognition**

### **🌟 Showcase Contributor Badge**
Contribute to any showcase demo and get featured:
- GitHub profile badge
- Recognition in release notes
- Showcase demo credits

### **📈 Impact Tracking**
Your contributions directly impact:
- PyMapGIS adoption rates
- Community growth
- Enterprise adoption
- Open source ecosystem

### **🤝 Team Membership**
Top contributors are invited to join the core PyMapGIS team with:
- Commit access to repositories
- Voice in project direction
- Recognition as maintainer
- Conference speaking opportunities

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- [Poetry](https://python-poetry.org/) for dependency management
- Git for version control

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/core.git
   cd core
   ```

2. **Install dependencies**
   ```bash
   poetry install --with dev
   ```

3. **Install pre-commit hooks**
   ```bash
   poetry run pre-commit install
   ```

4. **Run tests to verify setup**
   ```bash
   poetry run pytest
   ```

## 🔄 Development Workflow

### Branch Strategy

- **`main`**: Production-ready code (protected)
- **`dev`**: Development branch for integration
- **`feature/*`**: Feature branches for new functionality
- **`fix/*`**: Bug fix branches

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, documented code
   - Follow existing code style
   - Add tests for new functionality

3. **Run quality checks**
   ```bash
   poetry run pytest          # Run tests
   poetry run ruff check      # Linting
   poetry run black .         # Code formatting
   poetry run mypy pymapgis   # Type checking
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add amazing new feature"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📝 Code Style

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Use [Ruff](https://docs.astral.sh/ruff/) for linting
- Use type hints where appropriate

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Maintenance tasks

### Documentation

- Use docstrings for all public functions and classes
- Follow [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) docstrings
- Update README.md for user-facing changes

## 🧪 Testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=pymapgis

# Run specific test file
poetry run pytest tests/test_cache.py

# Run tests matching pattern
poetry run pytest -k "test_cache"
```

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies

Example:
```python
def test_cache_stores_and_retrieves_data():
    """Test that cache can store and retrieve data correctly."""
    cache = Cache()
    cache.put("key", "value")
    assert cache.get("key") == "value"
```

## 📦 Package Structure

```
pymapgis/
├── __init__.py          # Package exports
├── cache.py             # Caching functionality
├── acs.py              # Census ACS data source
├── tiger.py            # TIGER/Line data source
├── plotting.py         # Visualization utilities
├── settings.py         # Configuration
├── io/                 # Input/output modules
├── network/            # Network utilities
├── plugins/            # Plugin system
├── raster/             # Raster data handling
├── serve/              # Server components
├── vector/             # Vector data handling
└── viz/                # Visualization components
```

## 🐛 Reporting Issues

### Bug Reports

Include:
- Python version
- PyMapGIS version
- Operating system
- Minimal code example
- Error messages/stack traces

### Feature Requests

Include:
- Use case description
- Proposed API design
- Examples of usage

## 📋 Pull Request Guidelines

### Before Submitting

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated (if applicable)

### PR Description

Include:
- Summary of changes
- Related issue numbers
- Breaking changes (if any)
- Testing instructions

## 🏷️ Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release PR to `main`
4. Tag release after merge
5. Publish to PyPI

## 💬 Community

- **GitHub Discussions**: For questions and ideas
- **Issues**: For bug reports and feature requests
- **Email**: nicholaskarlson@gmail.com for maintainer contact

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to PyMapGIS! 🗺️✨
