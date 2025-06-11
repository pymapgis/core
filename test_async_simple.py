#!/usr/bin/env python3
"""
Simple test for async processing without progress bars.
"""

import asyncio
import tempfile
import pandas as pd
import numpy as np
from pathlib import Path

def create_simple_test_data():
    """Create simple test data."""
    print("Creating simple test data...")
    
    data = {
        'id': range(1000),
        'value': np.random.randint(1, 100, 1000),
        'category': np.random.choice(['A', 'B', 'C'], 1000)
    }
    
    df = pd.DataFrame(data)
    temp_file = Path(tempfile.gettempdir()) / "simple_test.csv"
    df.to_csv(temp_file, index=False)
    
    print(f"Created {len(df)} rows at {temp_file}")
    return temp_file

async def test_simple_async():
    """Simple async test."""
    print("Testing simple async functionality...")
    
    try:
        # Test basic import
        import pymapgis as pmg
        print(f"✅ PyMapGIS imported: {pmg.__version__}")
        
        # Test async processing import
        from pymapgis.async_processing import AsyncGeoProcessor
        print("✅ AsyncGeoProcessor imported")
        
        # Create test data
        test_file = create_simple_test_data()
        
        # Simple processing function
        def double_values(chunk):
            chunk['doubled'] = chunk['value'] * 2
            return chunk
        
        # Test without progress bar
        processor = AsyncGeoProcessor()
        
        result = await processor.process_large_dataset(
            filepath=test_file,
            operation=double_values,
            chunk_size=100,
            show_progress=False  # Disable progress bar
        )
        
        print(f"✅ Processed {len(result)} rows successfully")
        print(f"Sample result: {result.head(3).to_dict('records')}")
        
        # Clean up
        await processor.close()
        test_file.unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run simple test."""
    print("Simple Async Processing Test")
    print("=" * 30)
    
    success = await test_simple_async()
    
    if success:
        print("\n✅ Simple async test PASSED!")
        return 0
    else:
        print("\n❌ Simple async test FAILED!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
