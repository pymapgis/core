#!/usr/bin/env python3
"""
PyMapGIS Showcase Demo Validator

Validates that a showcase demo meets all requirements before submission.

Usage:
    python scripts/validate_demo.py showcases/demo-name
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple


class DemoValidator:
    """Validates showcase demos against quality standards."""
    
    def __init__(self, demo_path: Path):
        self.demo_path = demo_path
        self.demo_name = demo_path.name
        self.errors = []
        self.warnings = []
        self.info = []
    
    def validate(self) -> bool:
        """Run all validation checks."""
        print(f"🔍 Validating demo: {self.demo_name}")
        print(f"📁 Path: {self.demo_path}")
        print("=" * 60)
        
        # Required file structure
        self._check_file_structure()
        
        # Code quality
        self._check_code_quality()
        
        # Docker requirements
        self._check_docker_requirements()
        
        # Metadata and documentation
        self._check_documentation()
        
        # API endpoints
        self._check_api_requirements()
        
        # Print results
        self._print_results()
        
        return len(self.errors) == 0
    
    def _check_file_structure(self):
        """Check required files exist."""
        required_files = [
            "worker.py",
            "app.py", 
            "Dockerfile",
            "README.md",
            "static/index.html",
            "static/app.js"
        ]
        
        for file_path in required_files:
            full_path = self.demo_path / file_path
            if not full_path.exists():
                self.errors.append(f"Missing required file: {file_path}")
            else:
                self.info.append(f"✅ Found: {file_path}")
    
    def _check_code_quality(self):
        """Check Python code quality."""
        python_files = list(self.demo_path.glob("*.py"))
        
        if not python_files:
            self.errors.append("No Python files found")
            return
        
        for py_file in python_files:
            # Check for metadata header in worker.py
            if py_file.name == "worker.py":
                self._check_metadata_header(py_file)
            
            # Check file size (should be concise)
            line_count = len(py_file.read_text().splitlines())
            if py_file.name == "worker.py" and line_count > 150:
                self.warnings.append(f"worker.py is {line_count} lines (consider simplifying)")
            
            # Check for basic imports
            content = py_file.read_text()
            if "import pymapgis" not in content and "from pymapgis" not in content:
                self.warnings.append(f"{py_file.name} doesn't import pymapgis")
    
    def _check_metadata_header(self, worker_file: Path):
        """Check for required metadata header in worker.py."""
        content = worker_file.read_text()
        
        # Look for metadata header
        if "# ---" not in content:
            self.warnings.append("worker.py missing metadata header")
            return
        
        # Extract metadata section
        lines = content.splitlines()
        in_metadata = False
        metadata = {}
        
        for line in lines:
            if line.strip() == "# ---":
                if in_metadata:
                    break
                in_metadata = True
                continue
            
            if in_metadata and line.startswith("# "):
                if ":" in line:
                    key, value = line[2:].split(":", 1)
                    metadata[key.strip()] = value.strip()
        
        # Check required metadata fields
        required_fields = ["title", "feed", "category", "license"]
        for field in required_fields:
            if field not in metadata:
                self.warnings.append(f"Missing metadata field: {field}")
            else:
                self.info.append(f"✅ Metadata: {field} = {metadata[field]}")
    
    def _check_docker_requirements(self):
        """Check Docker configuration."""
        dockerfile = self.demo_path / "Dockerfile"
        
        if not dockerfile.exists():
            self.errors.append("Missing Dockerfile")
            return
        
        content = dockerfile.read_text()
        
        # Check for required elements
        required_elements = [
            ("FROM", "Base image specified"),
            ("WORKDIR", "Working directory set"),
            ("COPY", "Files copied"),
            ("EXPOSE", "Port exposed"),
            ("CMD", "Start command defined")
        ]
        
        for element, description in required_elements:
            if element in content:
                self.info.append(f"✅ Dockerfile: {description}")
            else:
                self.warnings.append(f"Dockerfile missing: {element}")
        
        # Check for health check
        if "HEALTHCHECK" in content:
            self.info.append("✅ Dockerfile: Health check configured")
        else:
            self.warnings.append("Dockerfile missing HEALTHCHECK")
    
    def _check_documentation(self):
        """Check documentation quality."""
        readme = self.demo_path / "README.md"
        
        if not readme.exists():
            self.errors.append("Missing README.md")
            return
        
        content = readme.read_text()
        
        # Check for required sections
        required_sections = [
            ("# ", "Title"),
            ("## ", "Sections"),
            ("```", "Code examples"),
            ("http", "URLs or links")
        ]
        
        for pattern, description in required_sections:
            if pattern in content:
                self.info.append(f"✅ README: {description} present")
            else:
                self.warnings.append(f"README missing: {description}")
        
        # Check length
        line_count = len(content.splitlines())
        if line_count < 20:
            self.warnings.append(f"README is short ({line_count} lines)")
        else:
            self.info.append(f"✅ README: {line_count} lines")
    
    def _check_api_requirements(self):
        """Check API endpoint requirements."""
        app_file = self.demo_path / "app.py"
        
        if not app_file.exists():
            return
        
        content = app_file.read_text()
        
        # Check for required endpoints
        required_endpoints = [
            ("/health", "Health check endpoint"),
            ("/public/tiles", "Vector tiles endpoint"),
            ("@app.get(\"/\")", "Root endpoint")
        ]
        
        for endpoint, description in required_endpoints:
            if endpoint in content:
                self.info.append(f"✅ API: {description}")
            else:
                self.warnings.append(f"API missing: {description}")
        
        # Check for FastAPI usage
        if "from fastapi import" in content:
            self.info.append("✅ API: Uses FastAPI")
        else:
            self.warnings.append("API: Not using FastAPI")
    
    def _check_build_requirements(self):
        """Check if demo can be built (optional, requires Docker)."""
        try:
            # Try to build the Docker image
            result = subprocess.run(
                ["docker", "build", "-t", f"test-{self.demo_name}", "."],
                cwd=self.demo_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                self.info.append("✅ Docker: Build successful")
                
                # Check image size
                size_result = subprocess.run(
                    ["docker", "images", f"test-{self.demo_name}", "--format", "{{.Size}}"],
                    capture_output=True,
                    text=True
                )
                
                if size_result.returncode == 0:
                    size = size_result.stdout.strip()
                    self.info.append(f"✅ Docker: Image size {size}")
                    
                    # Parse size and check if under 200MB
                    if "GB" in size or (float(size.split("MB")[0]) > 200 if "MB" in size else False):
                        self.warnings.append(f"Docker image large: {size} (target: <200MB)")
                
                # Clean up test image
                subprocess.run(["docker", "rmi", f"test-{self.demo_name}"], 
                             capture_output=True)
                
            else:
                self.errors.append(f"Docker build failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.errors.append("Docker build timed out (>5 minutes)")
        except FileNotFoundError:
            self.warnings.append("Docker not available - skipping build test")
        except Exception as e:
            self.warnings.append(f"Docker build test failed: {e}")
    
    def _print_results(self):
        """Print validation results."""
        print("\n" + "=" * 60)
        print("📊 VALIDATION RESULTS")
        print("=" * 60)
        
        if self.info:
            print(f"\n✅ PASSED ({len(self.info)} checks):")
            for item in self.info:
                print(f"  {item}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)} items):")
            for item in self.warnings:
                print(f"  ⚠️  {item}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)} items):")
            for item in self.errors:
                print(f"  ❌ {item}")
        
        print("\n" + "=" * 60)
        
        if self.errors:
            print("❌ VALIDATION FAILED")
            print("Fix the errors above before submitting your PR.")
        elif self.warnings:
            print("⚠️  VALIDATION PASSED WITH WARNINGS")
            print("Consider addressing warnings for better quality.")
        else:
            print("✅ VALIDATION PASSED")
            print("Demo meets all requirements!")
        
        print("=" * 60)


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python scripts/validate_demo.py showcases/demo-name")
        sys.exit(1)
    
    demo_path = Path(sys.argv[1])
    
    if not demo_path.exists():
        print(f"❌ Demo path not found: {demo_path}")
        sys.exit(1)
    
    if not demo_path.is_dir():
        print(f"❌ Path is not a directory: {demo_path}")
        sys.exit(1)
    
    validator = DemoValidator(demo_path)
    success = validator.validate()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
