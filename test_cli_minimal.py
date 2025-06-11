#!/usr/bin/env python3
"""
Minimal CLI test to identify hanging issues.
"""

import sys
import time

def test_cli_import():
    """Test importing CLI components."""
    print("Testing CLI imports...")
    
    try:
        print("1. Importing typer...")
        import typer
        print("✅ typer imported")
        
        print("2. Importing CLI main...")
        from pymapgis.cli.main import app
        print("✅ CLI main imported")
        
        print("3. Testing basic CLI help...")
        # Don't actually run the CLI, just test that it can be imported
        print("✅ CLI app created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic PyMapGIS functionality without CLI."""
    print("\nTesting basic functionality...")
    
    try:
        print("1. Importing PyMapGIS...")
        import pymapgis as pmg
        print(f"✅ PyMapGIS imported, version: {pmg.__version__}")
        
        print("2. Testing cache stats...")
        stats = pmg.stats()
        print(f"✅ Cache stats: {len(stats)} items")
        
        print("3. Testing read function...")
        # Just check if it's callable, don't actually read anything
        print(f"✅ Read function available: {callable(pmg.read)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("PyMapGIS CLI Minimal Test")
    print("=" * 40)
    
    # Test basic functionality first
    basic_ok = test_basic_functionality()
    
    # Test CLI imports
    cli_ok = test_cli_import()
    
    print("\n" + "=" * 40)
    print("Summary:")
    print(f"Basic functionality: {'✅ OK' if basic_ok else '❌ FAILED'}")
    print(f"CLI imports: {'✅ OK' if cli_ok else '❌ FAILED'}")
    
    if basic_ok and cli_ok:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
