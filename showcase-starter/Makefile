# PyMapGIS Showcase Development Makefile
# Common tasks for developing and testing showcase demos

.PHONY: help lint test build clean new-demo list-demos run-quake run-all

# Default target
help:
	@echo "PyMapGIS Showcase Development Commands"
	@echo "======================================"
	@echo ""
	@echo "Development:"
	@echo "  new-demo NAME=demo-name    Create new demo scaffold"
	@echo "  lint                       Run code linting (black, flake8, isort)"
	@echo "  test                       Run all tests"
	@echo "  build DEMO=demo-name       Build Docker image for specific demo"
	@echo ""
	@echo "Running Demos:"
	@echo "  run-quake                  Run the quake impact demo"
	@echo "  run-demo DEMO=demo-name    Run specific demo"
	@echo "  run-all                    Run all implemented demos"
	@echo ""
	@echo "Utilities:"
	@echo "  list-demos                 List all available demos"
	@echo "  clean                      Clean up Docker images and volumes"
	@echo "  validate DEMO=demo-name    Validate demo meets requirements"
	@echo ""
	@echo "Examples:"
	@echo "  make new-demo NAME=border-flow"
	@echo "  make build DEMO=quake-impact"
	@echo "  make run-demo DEMO=border-flow"

# Create new demo scaffold
new-demo:
	@if [ -z "$(NAME)" ]; then \
		echo "❌ Error: NAME parameter required"; \
		echo "Usage: make new-demo NAME=demo-name"; \
		exit 1; \
	fi
	@echo "🚀 Creating new demo: $(NAME)"
	python scripts/new_demo.py $(NAME)

# List all available demos
list-demos:
	@echo "📋 Available Showcase Demos:"
	@echo "============================"
	@if [ -d "showcases" ]; then \
		for demo in showcases/*/; do \
			if [ -d "$$demo" ]; then \
				demo_name=$$(basename "$$demo"); \
				if [ -f "$$demo/README.md" ]; then \
					title=$$(head -1 "$$demo/README.md" | sed 's/# //'); \
					echo "  ✅ $$demo_name - $$title"; \
				else \
					echo "  🚧 $$demo_name - (no README)"; \
				fi; \
			fi; \
		done; \
	else \
		echo "  (No demos found - run 'make new-demo NAME=demo-name' to create one)"; \
	fi
	@echo ""
	@echo "💡 Ideas available for implementation:"
	@for idea in ideas/*.md; do \
		if [ -f "$$idea" ]; then \
			idea_name=$$(basename "$$idea" .md); \
			title=$$(head -1 "$$idea" | sed 's/# //'); \
			status=$$(grep -o "Status.*" "$$idea" | head -1 || echo "Status: 🚧 Open"); \
			echo "  $$idea_name - $$title ($$status)"; \
		fi; \
	done

# Code linting
lint:
	@echo "🔍 Running code linting..."
	@if [ -d "showcases" ]; then \
		for demo in showcases/*/; do \
			if [ -d "$$demo" ]; then \
				echo "Linting $$demo..."; \
				cd "$$demo" && \
				black --check *.py 2>/dev/null || echo "⚠️  Black formatting needed in $$demo"; \
				flake8 *.py 2>/dev/null || echo "⚠️  Flake8 issues in $$demo"; \
				isort --check-only *.py 2>/dev/null || echo "⚠️  Import sorting needed in $$demo"; \
				cd - > /dev/null; \
			fi; \
		done; \
	fi
	@echo "✅ Linting complete"

# Fix code formatting
format:
	@echo "🔧 Fixing code formatting..."
	@if [ -d "showcases" ]; then \
		for demo in showcases/*/; do \
			if [ -d "$$demo" ]; then \
				echo "Formatting $$demo..."; \
				cd "$$demo" && \
				black *.py 2>/dev/null || true; \
				isort *.py 2>/dev/null || true; \
				cd - > /dev/null; \
			fi; \
		done; \
	fi
	@echo "✅ Formatting complete"

# Build Docker image for specific demo
build:
	@if [ -z "$(DEMO)" ]; then \
		echo "❌ Error: DEMO parameter required"; \
		echo "Usage: make build DEMO=demo-name"; \
		exit 1; \
	fi
	@if [ ! -d "showcases/$(DEMO)" ]; then \
		echo "❌ Error: Demo 'showcases/$(DEMO)' not found"; \
		echo "Available demos:"; \
		make list-demos; \
		exit 1; \
	fi
	@echo "🐳 Building Docker image for $(DEMO)..."
	cd showcases/$(DEMO) && docker build -t pymapgis-$(DEMO) .
	@echo "✅ Built image: pymapgis-$(DEMO)"

# Test specific demo
test:
	@echo "🧪 Running tests..."
	@if [ -d "showcases" ]; then \
		for demo in showcases/*/; do \
			if [ -d "$$demo" ]; then \
				demo_name=$$(basename "$$demo"); \
				echo "Testing $$demo_name..."; \
				cd "$$demo" && \
				if [ -f "test_*.py" ]; then \
					python -m pytest test_*.py -v; \
				else \
					echo "  No tests found for $$demo_name"; \
				fi; \
				cd - > /dev/null; \
			fi; \
		done; \
	fi
	@echo "✅ Tests complete"

# Validate demo meets requirements
validate:
	@if [ -z "$(DEMO)" ]; then \
		echo "❌ Error: DEMO parameter required"; \
		echo "Usage: make validate DEMO=demo-name"; \
		exit 1; \
	fi
	@if [ ! -d "showcases/$(DEMO)" ]; then \
		echo "❌ Error: Demo 'showcases/$(DEMO)' not found"; \
		exit 1; \
	fi
	@echo "✅ Validating demo: $(DEMO)"
	python scripts/validate_demo.py showcases/$(DEMO)

# Run the quake impact demo (reference implementation)
run-quake:
	@echo "🌍 Starting Quake Impact demo..."
	docker compose up quake-demo

# Run specific demo
run-demo:
	@if [ -z "$(DEMO)" ]; then \
		echo "❌ Error: DEMO parameter required"; \
		echo "Usage: make run-demo DEMO=demo-name"; \
		exit 1; \
	fi
	@if [ ! -d "showcases/$(DEMO)" ]; then \
		echo "❌ Error: Demo 'showcases/$(DEMO)' not found"; \
		exit 1; \
	fi
	@echo "🚀 Starting $(DEMO) demo..."
	cd showcases/$(DEMO) && docker build -t $(DEMO) . && docker run -p 8000:8000 $(DEMO)

# Run all implemented demos (different ports)
run-all:
	@echo "🚀 Starting all showcase demos..."
	docker compose up -d
	@echo ""
	@echo "📍 Demo URLs:"
	@echo "  Quake Impact:  http://localhost:8000"
	@echo "  Border Flow:   http://localhost:8001 (if implemented)"
	@echo "  Flight Delay:  http://localhost:8002 (if implemented)"
	@echo "  Wildfire Risk: http://localhost:8003 (if implemented)"
	@echo ""
	@echo "🛑 Stop all demos: docker compose down"

# Clean up Docker resources
clean:
	@echo "🧹 Cleaning up Docker resources..."
	docker compose down -v --remove-orphans 2>/dev/null || true
	docker system prune -f
	@echo "✅ Cleanup complete"

# Development setup
setup:
	@echo "🔧 Setting up development environment..."
	@if [ ! -d "showcases" ]; then mkdir showcases; fi
	@if [ ! -f "scripts/validate_demo.py" ]; then \
		echo "Creating validation script..."; \
		echo "#!/usr/bin/env python3" > scripts/validate_demo.py; \
		echo "# Demo validation script - TODO: implement" >> scripts/validate_demo.py; \
		chmod +x scripts/validate_demo.py; \
	fi
	@echo "✅ Development environment ready"

# Install dependencies for local development
install:
	@echo "📦 Installing dependencies..."
	pip install black flake8 isort pydocstyle pytest
	@echo "✅ Dependencies installed"

# Quick start for new contributors
quickstart:
	@echo "🚀 PyMapGIS Showcase Quick Start"
	@echo "==============================="
	@echo ""
	@echo "1. Test the reference demo:"
	@echo "   make run-quake"
	@echo ""
	@echo "2. Create your own demo:"
	@echo "   make new-demo NAME=your-demo-name"
	@echo ""
	@echo "3. Build and test:"
	@echo "   make build DEMO=your-demo-name"
	@echo "   make run-demo DEMO=your-demo-name"
	@echo ""
	@echo "4. Validate and submit:"
	@echo "   make lint"
	@echo "   make validate DEMO=your-demo-name"
	@echo "   git add . && git commit && git push"
	@echo ""
	@echo "📖 See CONTRIBUTING.md for detailed guidelines"
