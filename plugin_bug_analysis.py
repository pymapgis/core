#!/usr/bin/env python3
"""
Comprehensive bug analysis for the PyMapGIS QGIS plugin.
This script analyzes the plugin code for potential issues and bugs.
"""

import sys
import os
from pathlib import Path
import ast
import re

def analyze_plugin_code():
    """Analyze the plugin code for potential bugs and issues."""
    print("🔍 PyMapGIS QGIS Plugin Bug Analysis")
    print("=" * 50)
    
    plugin_dir = Path("qgis_plugin/pymapgis_qgis_plugin")
    
    issues_found = []
    
    # Analyze each plugin file
    files_to_analyze = [
        "pymapgis_plugin.py",
        "pymapgis_dialog.py",
        "__init__.py"
    ]
    
    for filename in files_to_analyze:
        filepath = plugin_dir / filename
        if filepath.exists():
            print(f"\n📄 Analyzing {filename}...")
            file_issues = analyze_file(filepath)
            if file_issues:
                issues_found.extend([(filename, issue) for issue in file_issues])
            else:
                print(f"   ✅ No obvious issues found in {filename}")
    
    # Print summary
    print(f"\n📊 Analysis Summary")
    print("=" * 30)
    
    if issues_found:
        print(f"⚠️  Found {len(issues_found)} potential issues:")
        for filename, issue in issues_found:
            print(f"   📁 {filename}: {issue}")
    else:
        print("🎉 No obvious bugs found in the plugin code!")
    
    return issues_found

def analyze_file(filepath):
    """Analyze a specific file for potential issues."""
    issues = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Check for common issues
    issues.extend(check_error_handling(content, lines))
    issues.extend(check_resource_management(content, lines))
    issues.extend(check_qt_issues(content, lines))
    issues.extend(check_plugin_specific_issues(content, lines, filepath.name))
    
    return issues

def check_error_handling(content, lines):
    """Check for error handling issues."""
    issues = []
    
    # Check for bare except clauses
    for i, line in enumerate(lines, 1):
        if re.search(r'except\s*:', line):
            issues.append(f"Line {i}: Bare except clause - should specify exception type")
    
    # Check for missing error handling in critical sections
    if 'pymapgis.read(' in content and 'except' not in content:
        issues.append("Missing error handling for pymapgis.read() calls")
    
    return issues

def check_resource_management(content, lines):
    """Check for resource management issues."""
    issues = []
    
    # Check for temporary file cleanup
    if 'tempfile' in content:
        if 'deleteLater' not in content and 'os.remove' not in content:
            issues.append("Temporary files may not be properly cleaned up")
    
    # Check for dialog cleanup
    if 'QDialog' in content:
        if 'deleteLater' in content:
            # Check if deleteLater is commented out
            for i, line in enumerate(lines, 1):
                if 'deleteLater' in line and line.strip().startswith('#'):
                    issues.append(f"Line {i}: deleteLater() is commented out - may cause memory leaks")
    
    return issues

def check_qt_issues(content, lines):
    """Check for Qt-specific issues."""
    issues = []
    
    # Check for signal/slot connection issues
    signal_connections = []
    signal_disconnections = []
    
    for i, line in enumerate(lines, 1):
        if '.connect(' in line:
            signal_connections.append(i)
        if '.disconnect(' in line:
            signal_disconnections.append(i)
    
    # Check for potential signal connection leaks
    if len(signal_connections) > len(signal_disconnections):
        issues.append(f"Potential signal connection leak: {len(signal_connections)} connections vs {len(signal_disconnections)} disconnections")
    
    # Check for proper exception handling in signal handlers
    for i, line in enumerate(lines, 1):
        if '.disconnect(' in line and 'except' not in lines[i:i+3]:
            # Check if there's a try-except around the disconnect
            found_try = False
            for j in range(max(0, i-3), min(len(lines), i+3)):
                if 'try:' in lines[j] or 'except' in lines[j]:
                    found_try = True
                    break
            if not found_try:
                issues.append(f"Line {i}: Signal disconnection without exception handling")
    
    return issues

def check_plugin_specific_issues(content, lines, filename):
    """Check for plugin-specific issues."""
    issues = []
    
    if filename == "pymapgis_dialog.py":
        # Check for CRS handling issues
        if 'rio.crs is None' in content:
            # This is actually correct, but let's check if there's proper handling
            crs_check_found = False
            for line in lines:
                if 'rio.crs is None' in line:
                    crs_check_found = True
                    break
            if crs_check_found:
                # Check if there's proper error handling after the CRS check
                crs_line_idx = None
                for i, line in enumerate(lines):
                    if 'rio.crs is None' in line:
                        crs_line_idx = i
                        break
                
                if crs_line_idx is not None:
                    # Check next few lines for proper handling
                    next_lines = lines[crs_line_idx:crs_line_idx+5]
                    if not any('return' in line or 'messageBar' in line for line in next_lines):
                        issues.append("CRS check may not have proper error handling")
        
        # Check for proper data type validation
        if 'isinstance(data, gpd.GeoDataFrame)' in content and 'isinstance(data, xr.DataArray)' in content:
            # Good - both types are handled
            pass
        else:
            issues.append("Missing comprehensive data type validation")
        
        # Check for URI validation
        if 'uri.strip()' in content:
            # Good - URI is being validated
            pass
        else:
            issues.append("Missing URI validation")
    
    elif filename == "pymapgis_plugin.py":
        # Check for proper plugin cleanup
        if 'unload' in content:
            unload_found = False
            for line in lines:
                if 'def unload(' in line:
                    unload_found = True
                    break
            if not unload_found:
                issues.append("Missing unload method for proper plugin cleanup")
        
        # Check for import error handling
        if 'import pymapgis' in content:
            import_error_handled = False
            for line in lines:
                if 'ImportError' in line and 'pymapgis' in line:
                    import_error_handled = True
                    break
            if not import_error_handled:
                issues.append("Missing import error handling for pymapgis")
    
    return issues

def check_code_quality():
    """Check for code quality issues."""
    print(f"\n🔧 Code Quality Analysis")
    print("-" * 30)
    
    plugin_dir = Path("qgis_plugin/pymapgis_qgis_plugin")
    quality_issues = []
    
    for py_file in plugin_dir.glob("*.py"):
        print(f"   📄 Checking {py_file.name}...")
        
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Check for long lines
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                quality_issues.append(f"{py_file.name}:{i} - Line too long ({len(line)} chars)")
        
        # Check for missing docstrings
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        quality_issues.append(f"{py_file.name}:{node.lineno} - Missing docstring for {node.name}")
        except SyntaxError:
            quality_issues.append(f"{py_file.name} - Syntax error in file")
    
    if quality_issues:
        print(f"   ⚠️  Found {len(quality_issues)} code quality issues")
        for issue in quality_issues[:10]:  # Show first 10
            print(f"      - {issue}")
        if len(quality_issues) > 10:
            print(f"      ... and {len(quality_issues) - 10} more")
    else:
        print("   ✅ No major code quality issues found")
    
    return quality_issues

def check_metadata_consistency():
    """Check metadata file for consistency."""
    print(f"\n📋 Metadata Analysis")
    print("-" * 20)
    
    metadata_file = Path("qgis_plugin/pymapgis_qgis_plugin/metadata.txt")
    issues = []
    
    if metadata_file.exists():
        with open(metadata_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required fields
        required_fields = ['name', 'qgisMinimumVersion', 'description', 'version', 'author']
        for field in required_fields:
            if f"{field}=" not in content:
                issues.append(f"Missing required field: {field}")
        
        # Check if experimental is set appropriately
        if 'experimental=True' in content:
            print("   ⚠️  Plugin is marked as experimental")
        
        # Check version consistency
        if 'version=0.1.0' in content:
            print("   ℹ️  Plugin version is 0.1.0 (early development)")
        
        if issues:
            print(f"   ⚠️  Found {len(issues)} metadata issues:")
            for issue in issues:
                print(f"      - {issue}")
        else:
            print("   ✅ Metadata appears consistent")
    else:
        issues.append("metadata.txt file not found")
        print("   ❌ metadata.txt file not found")
    
    return issues

def main():
    """Run the complete bug analysis."""
    print("🧪 PyMapGIS QGIS Plugin Comprehensive Analysis\n")
    
    # Change to the correct directory
    os.chdir(Path(__file__).parent)
    
    # Run all analyses
    plugin_issues = analyze_plugin_code()
    quality_issues = check_code_quality()
    metadata_issues = check_metadata_consistency()
    
    # Final summary
    total_issues = len(plugin_issues) + len(quality_issues) + len(metadata_issues)
    
    print(f"\n🎯 Final Summary")
    print("=" * 20)
    print(f"Plugin Logic Issues: {len(plugin_issues)}")
    print(f"Code Quality Issues: {len(quality_issues)}")
    print(f"Metadata Issues: {len(metadata_issues)}")
    print(f"Total Issues Found: {total_issues}")
    
    if total_issues == 0:
        print("\n🎉 Excellent! No significant issues found in the plugin.")
        return 0
    else:
        print(f"\n⚠️  Found {total_issues} issues that should be reviewed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
