#!/usr/bin/env python3
"""
Test script for Border Flow Now application
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Import the app
from app import app, load_border_data
import uvicorn

def test_data_loading():
    """Test if data loading works"""
    print("🧪 Testing data loading...")
    data = load_border_data()
    print(f"✅ Data status: {data['status']}")
    print(f"📊 Total ports: {data.get('total_ports', 0)}")
    if data['status'] == 'success':
        print(f"📈 Average wait time: {data.get('avg_wait_time', 0):.1f} minutes")
        print(f"🔴 Maximum wait time: {data.get('max_wait_time', 0):.1f} minutes")
    return data['status'] == 'success'

def main():
    """Main test function"""
    print("🚛 Testing Border Flow Now application...")
    
    # Test data loading
    if test_data_loading():
        print("✅ Data loading test passed!")
        
        # Start the server on port 8002
        print("🚀 Starting Border Flow Now server on port 8002...")
        print("📍 View at: http://localhost:8002")
        print("📊 API test: http://localhost:8002/public/latest")
        print("❤️  Health check: http://localhost:8002/health")
        
        uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
    else:
        print("❌ Data loading test failed!")
        print("💡 Make sure to run 'python border_worker.py' first")

if __name__ == "__main__":
    main()
