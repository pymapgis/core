#!/usr/bin/env python3
"""
PyMapGIS Vector Operations Demonstration

This script demonstrates the vector operations functionality implemented
for Phase 1 - Part 5 of PyMapGIS. It shows both standalone functions
and accessor methods.

Note: This is a demonstration script that requires the full PyMapGIS
environment with dependencies installed.
"""

def demo_vector_operations():
    """Demonstrate PyMapGIS vector operations."""
    
    print("=" * 60)
    print("PyMapGIS Vector Operations Demo")
    print("=" * 60)
    
    try:
        import geopandas as gpd
        import pymapgis as pmg
        from shapely.geometry import Point, Polygon
        
        print("✓ Dependencies imported successfully")
        
        # Create sample data
        print("\n1. Creating sample data...")
        
        # Sample points
        points_data = {
            'id': [1, 2, 3, 4],
            'name': ['Point A', 'Point B', 'Point C', 'Point D'],
            'geometry': [Point(0, 0), Point(1, 1), Point(2, 2), Point(3, 3)]
        }
        points = gpd.GeoDataFrame(points_data, crs="EPSG:4326")
        print(f"  Created {len(points)} points")
        
        # Sample polygons
        polygons_data = {
            'id': [1, 2],
            'name': ['Area 1', 'Area 2'],
            'geometry': [
                Polygon([(0, 0), (2, 0), (2, 2), (0, 2)]),
                Polygon([(1.5, 1.5), (3.5, 1.5), (3.5, 3.5), (1.5, 3.5)])
            ]
        }
        polygons = gpd.GeoDataFrame(polygons_data, crs="EPSG:4326")
        print(f"  Created {len(polygons)} polygons")
        
        # Study area for clipping
        study_area = Polygon([(0.5, 0.5), (2.5, 0.5), (2.5, 2.5), (0.5, 2.5)])
        print("  Created study area polygon")
        
        # 2. Demonstrate standalone functions
        print("\n2. Testing standalone vector functions...")
        
        # Buffer operation
        buffered_points = pmg.vector.buffer(points, distance=0.3)
        print(f"  ✓ Buffer: {len(buffered_points)} buffered points created")
        
        # Clip operation
        clipped_points = pmg.vector.clip(points, study_area)
        print(f"  ✓ Clip: {len(clipped_points)} points after clipping")
        
        # Overlay operation
        overlay_result = pmg.vector.overlay(
            polygons.iloc[[0]], 
            polygons.iloc[[1]], 
            how='intersection'
        )
        print(f"  ✓ Overlay: {len(overlay_result)} intersection features")
        
        # Spatial join operation
        joined = pmg.vector.spatial_join(points, polygons, op='intersects')
        print(f"  ✓ Spatial Join: {len(joined)} joined features")
        
        # 3. Demonstrate accessor methods
        print("\n3. Testing accessor methods...")
        
        # Buffer via accessor
        buffered_accessor = points.pmg.buffer(0.3)
        print(f"  ✓ Accessor Buffer: {len(buffered_accessor)} buffered points")
        
        # Clip via accessor
        clipped_accessor = points.pmg.clip(study_area)
        print(f"  ✓ Accessor Clip: {len(clipped_accessor)} clipped points")
        
        # Spatial join via accessor
        joined_accessor = points.pmg.spatial_join(polygons, op='intersects')
        print(f"  ✓ Accessor Spatial Join: {len(joined_accessor)} joined features")
        
        # 4. Demonstrate method chaining
        print("\n4. Testing method chaining...")
        
        chained_result = (points
                         .pmg.buffer(0.2)
                         .pmg.clip(study_area)
                         .pmg.spatial_join(polygons, how='left'))
        print(f"  ✓ Chained Operations: {len(chained_result)} final features")
        
        # 5. Demonstrate integration workflow
        print("\n5. Testing integration workflow...")
        
        # Realistic workflow: buffer points, clip to study area, join with polygons
        workflow_result = pmg.vector.spatial_join(
            pmg.vector.clip(
                pmg.vector.buffer(points, distance=0.25),
                study_area
            ),
            polygons,
            how='left'
        )
        print(f"  ✓ Integration Workflow: {len(workflow_result)} final features")
        
        print("\n" + "=" * 60)
        print("✅ All vector operations completed successfully!")
        print("✅ Both standalone functions and accessor methods work!")
        print("✅ Method chaining and integration workflows work!")
        print("=" * 60)
        
    except ImportError as e:
        print(f"✗ Import Error: {e}")
        print("  This demo requires PyMapGIS dependencies to be installed.")
        print("  Run: poetry install")
        
    except Exception as e:
        print(f"✗ Error during demo: {e}")
        import traceback
        traceback.print_exc()

def demo_error_handling():
    """Demonstrate error handling in vector operations."""
    
    print("\n" + "=" * 60)
    print("Error Handling Demonstration")
    print("=" * 60)
    
    try:
        import geopandas as gpd
        import pymapgis as pmg
        from shapely.geometry import Point
        
        # Create sample data
        gdf = gpd.GeoDataFrame({'geometry': [Point(0, 0)]}, crs="EPSG:4326")
        
        # Test invalid overlay operation
        try:
            pmg.vector.overlay(gdf, gdf, how='invalid_operation')
        except ValueError as e:
            print(f"✓ Caught expected error for invalid overlay: {e}")
        
        # Test invalid spatial join predicate
        try:
            pmg.vector.spatial_join(gdf, gdf, op='invalid_predicate')
        except ValueError as e:
            print(f"✓ Caught expected error for invalid predicate: {e}")
        
        # Test invalid spatial join type
        try:
            pmg.vector.spatial_join(gdf, gdf, how='invalid_join')
        except ValueError as e:
            print(f"✓ Caught expected error for invalid join type: {e}")
        
        print("✅ Error handling works correctly!")
        
    except ImportError:
        print("✗ Cannot test error handling - dependencies not available")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

if __name__ == "__main__":
    demo_vector_operations()
    demo_error_handling()
