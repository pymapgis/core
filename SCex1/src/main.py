"""
Main entry point for the Supply Chain Optimization Example

This module provides command-line interface and main execution logic
for the supply chain optimization demonstration.

Author: Nicholas Karlson
License: MIT
"""

import argparse
import sys
import os
from pathlib import Path
import json
from typing import Optional

from .supply_chain_optimizer import SimpleSupplyChainOptimizer
from .api import app


def run_demo(num_customers: int = 30, 
             num_warehouses: int = 3, 
             output_dir: str = "output",
             random_seed: int = 42):
    """
    Run the supply chain optimization demo.
    
    Args:
        num_customers: Number of customers to generate
        num_warehouses: Number of warehouses to optimize for
        output_dir: Directory to save output files
        random_seed: Random seed for reproducibility
    """
    print("🚚 Supply Chain Optimization Demo")
    print("=" * 50)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize optimizer
    optimizer = SimpleSupplyChainOptimizer(random_seed=random_seed)
    
    # Generate sample data
    print(f"📍 Generating {num_customers} customers and potential warehouse locations...")
    optimizer.generate_sample_data(
        num_customers=num_customers,
        num_potential_warehouses=num_warehouses * 3,  # More options for optimization
        region_bounds=(40.0, 45.0, -85.0, -75.0)  # Great Lakes region
    )
    
    # Optimize warehouse locations
    print(f"🔧 Optimizing for {num_warehouses} warehouse locations...")
    solution = optimizer.optimize_warehouse_locations(num_warehouses=num_warehouses)
    
    # Generate report
    print("📊 Generating optimization report...")
    report = optimizer.generate_report()
    
    # Print summary
    print("\n📈 Optimization Results:")
    print(f"  • Total Cost: ${report['optimization_summary']['total_cost']:,.2f}")
    print(f"  • Total Distance: {report['optimization_summary']['total_distance']:.2f} units")
    print(f"  • Utilization Rate: {report['optimization_summary']['utilization_rate']:.1%}")
    print(f"  • Average Cost per Customer: ${report['optimization_summary']['average_cost_per_customer']:,.2f}")
    
    print("\n🏭 Warehouse Details:")
    for warehouse_info in report['warehouse_details']:
        print(f"  • {warehouse_info['name']}: "
              f"{warehouse_info['assigned_customers']} customers, "
              f"{warehouse_info['utilization']:.1%} utilization")
    
    # Create visualization
    print("🗺️  Creating interactive map...")
    map_path = os.path.join(output_dir, "supply_chain_map.html")
    optimizer.create_visualization(save_path=map_path)
    print(f"   Map saved as '{map_path}'")
    
    # Save report
    report_path = os.path.join(output_dir, "optimization_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"   Report saved as '{report_path}'")
    
    print("\n✅ Demo completed successfully!")
    print(f"📁 Output files saved in '{output_dir}' directory")
    
    return optimizer, solution, report


def run_api_server(host: str = "0.0.0.0", port: int = 8000):
    """
    Run the FastAPI web server.
    
    Args:
        host: Host address to bind to
        port: Port number to listen on
    """
    import uvicorn
    
    print("🌐 Starting Supply Chain Optimization API Server")
    print("=" * 50)
    print(f"🚀 Server will start at http://{host}:{port}")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🗺️  Interactive UI: http://localhost:8000")
    print("\nPress Ctrl+C to stop the server")
    
    uvicorn.run(app, host=host, port=port)


def main():
    """Main command-line interface."""
    parser = argparse.ArgumentParser(
        description="Supply Chain Optimization Example using PyMapGIS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s demo                          # Run basic demo
  %(prog)s demo --customers 50 --warehouses 4  # Custom parameters
  %(prog)s server                        # Start web API server
  %(prog)s server --port 8080            # Start server on custom port
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run optimization demo")
    demo_parser.add_argument(
        "--customers", 
        type=int, 
        default=30, 
        help="Number of customers to generate (default: 30)"
    )
    demo_parser.add_argument(
        "--warehouses", 
        type=int, 
        default=3, 
        help="Number of warehouses to optimize for (default: 3)"
    )
    demo_parser.add_argument(
        "--output", 
        type=str, 
        default="output", 
        help="Output directory for results (default: output)"
    )
    demo_parser.add_argument(
        "--seed", 
        type=int, 
        default=42, 
        help="Random seed for reproducibility (default: 42)"
    )
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Start web API server")
    server_parser.add_argument(
        "--host", 
        type=str, 
        default="0.0.0.0", 
        help="Host address to bind to (default: 0.0.0.0)"
    )
    server_parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port number to listen on (default: 8000)"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command == "demo":
        try:
            run_demo(
                num_customers=args.customers,
                num_warehouses=args.warehouses,
                output_dir=args.output,
                random_seed=args.seed
            )
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            sys.exit(1)
    
    elif args.command == "server":
        try:
            run_api_server(host=args.host, port=args.port)
        except KeyboardInterrupt:
            print("\n👋 Server stopped by user")
        except Exception as e:
            print(f"❌ Server failed: {e}")
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
