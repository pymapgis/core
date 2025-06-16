#!/usr/bin/env python3
"""
Documentation Verification Script for Quake Impact Now

This script verifies that all documentation files exist, are properly linked,
and contain the expected content structure.
"""

import os
import re
from pathlib import Path

def verify_documentation():
    """Verify all documentation files and their cross-references."""
    
    # Define expected documentation files
    expected_docs = {
        'README.md': {
            'min_lines': 300,
            'required_sections': [
                '# 🌍 Quake Impact Now',
                '## 📚 Documentation',
                '## 🚀 Quick Start',
                '## 🔧 What the Service Does'
            ]
        },
        'DOCUMENTATION_INDEX.md': {
            'min_lines': 100,
            'required_sections': [
                '# 📚 Quake Impact Now - Complete Documentation Index',
                '## 📖 Documentation Structure',
                '## 🎯 Quick Navigation by Use Case'
            ]
        },
        'POETRY_SETUP.md': {
            'min_lines': 400,
            'required_sections': [
                '# 🎭 Poetry Setup Guide',
                '## 🎭 What is Poetry and Why Use It?',
                '## 🚀 Quick Start with Poetry'
            ]
        },
        'UBUNTU_SETUP.md': {
            'min_lines': 300,
            'required_sections': [
                '# 🐧 Ubuntu Setup Guide',
                '## 🚀 Quick Start (Docker Method)',
                '## 🛠️ Local Development Setup'
            ]
        },
        'ARCHITECTURE.md': {
            'min_lines': 150,
            'required_sections': [
                '# 🏗️ Quake Impact Now - Architecture Overview',
                '## 🔧 System Architecture',
                '## 🧩 Component Breakdown'
            ]
        },
        'PYMAPGIS_INTEGRATION.md': {
            'min_lines': 250,
            'required_sections': [
                '# 🗺️ PyMapGIS Integration Guide',
                '## 🧩 PyMapGIS Components Used',
                '## 🔗 Integration with Python Ecosystem'
            ]
        }
    }
    
    # Define expected application files
    expected_files = [
        'app.py',
        'quake_impact.py',
        'requirements.txt',
        'Dockerfile',
        'static/index.html'
    ]
    
    print("🔍 Verifying Quake Impact Now Documentation...")
    print("=" * 60)
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    if not (current_dir / 'app.py').exists():
        print("❌ Error: Please run this script from the showcases/quake-impact-now directory")
        return False
    
    all_checks_passed = True
    
    # Verify documentation files
    print("\n📚 Checking Documentation Files:")
    for doc_file, requirements in expected_docs.items():
        if not os.path.exists(doc_file):
            print(f"❌ Missing: {doc_file}")
            all_checks_passed = False
            continue
        
        # Check file size and content
        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Check minimum lines
        if len(lines) < requirements['min_lines']:
            print(f"⚠️  {doc_file}: Only {len(lines)} lines (expected ≥{requirements['min_lines']})")
            all_checks_passed = False
        else:
            print(f"✅ {doc_file}: {len(lines)} lines")
        
        # Check required sections
        missing_sections = []
        for section in requirements['required_sections']:
            if section not in content:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"❌ {doc_file}: Missing sections: {missing_sections}")
            all_checks_passed = False
    
    # Verify application files
    print("\n🔧 Checking Application Files:")
    for app_file in expected_files:
        if os.path.exists(app_file):
            print(f"✅ {app_file}")
        else:
            print(f"❌ Missing: {app_file}")
            all_checks_passed = False
    
    # Check cross-references in README
    print("\n🔗 Checking Cross-References:")
    if os.path.exists('README.md'):
        with open('README.md', 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        # Check for documentation links
        doc_links = [
            'DOCUMENTATION_INDEX.md',
            'ARCHITECTURE.md',
            'UBUNTU_SETUP.md',
            'POETRY_SETUP.md',
            'PYMAPGIS_INTEGRATION.md'
        ]
        
        for link in doc_links:
            if link in readme_content:
                print(f"✅ README links to {link}")
            else:
                print(f"❌ README missing link to {link}")
                all_checks_passed = False
    
    # Check Poetry setup references
    print("\n🎭 Checking Poetry Integration:")
    poetry_indicators = [
        'poetry run python',
        'poetry install',
        'poetry env info'
    ]
    
    files_to_check = ['README.md', 'POETRY_SETUP.md']
    for file_name in files_to_check:
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8') as f:
                content = f.read()
            
            found_indicators = [indicator for indicator in poetry_indicators if indicator in content]
            if found_indicators:
                print(f"✅ {file_name}: Contains Poetry commands ({len(found_indicators)}/3)")
            else:
                print(f"⚠️  {file_name}: No Poetry commands found")
    
    # Summary
    print("\n" + "=" * 60)
    if all_checks_passed:
        print("🎉 All documentation checks PASSED!")
        print("📚 Documentation is complete and properly organized.")
        print("🚀 Ready for GitHub and user consumption!")
    else:
        print("❌ Some documentation checks FAILED!")
        print("🔧 Please review and fix the issues above.")
    
    return all_checks_passed

if __name__ == "__main__":
    success = verify_documentation()
    exit(0 if success else 1)
