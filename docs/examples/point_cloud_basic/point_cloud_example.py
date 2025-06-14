# Attempt to use a hypothetical pymapgis interface first
# If pymapgis has a specific point cloud module or function:
# from pymapgis import pointcloud as pmpc
# or from pymapgis import read_point_cloud

# As a fallback, and for concrete implementation, we'll use pdal directly,
# assuming pymapgis would wrap or expose this.
import pdal
import json
import numpy as np

def inspect_point_cloud_data():
    """
    Loads a LAS file and demonstrates basic inspection of point cloud data
    using PDAL, which pymapgis would likely wrap.
    """
    las_filepath = "docs/examples/point_cloud_basic/sample.las"
    print(f"Attempting to load point cloud data from: {las_filepath}")

    try:
        # Construct a PDAL pipeline to read the LAS file
        # This is how one might use PDAL's Python API.
        # pymapgis.read(las_filepath) or pymapgis.PointCloud(las_filepath)
        # would ideally simplify this.

        pipeline_json = f"""
        {{
            "pipeline": [
                "{las_filepath}"
            ]
        }}
        """
        pipeline = pdal.Pipeline(pipeline_json)

        # Execute the pipeline to load the data
        count = pipeline.execute() # Returns the number of points if successful

        if not count > 0:
            print("Pipeline executed, but read zero points. Check file or PDAL setup.")
            # If pipeline.arrays is empty, it means no data was processed or returned.
            # This can happen if the pipeline didn't properly configure a reader stage
            # or if the file is empty/corrupt.
            # For a simple file read, execute() should load data.
            # If pipeline.arrays is empty, let's try to get metadata differently.
            # For simple file reads, metadata is usually available after execute or from get_metadata
            metadata = pipeline.metadata
            if metadata:
                 print("\\n--- Metadata (from pipeline.metadata post-execute) ---")
                 # PDAL metadata is a JSON string, parse it for pretty printing
                 meta_json = json.loads(metadata)
                 print(json.dumps(meta_json, indent=2))

                 # Extract some specific metadata if available (paths might vary)
                 if meta_json.get("metadata", {}).get("readers.las", [{}])[0].get("point_format_name"):
                     print(f"Point Format: {meta_json['metadata']['readers.las'][0]['point_format_name']}")
                 if meta_json.get("metadata", {}).get("readers.las", [{}])[0].get("count"):
                     num_points_meta = meta_json['metadata']['readers.las'][0]['count']
                     print(f"Number of points (from metadata): {num_points_meta}")
                     if num_points_meta == 0:
                         print("Metadata also reports zero points. The file might be empty or have issues.")
                         return # Exit if no points
                 else:
                     print("Could not retrieve point count from metadata using expected path.")
            else:
                print("Could not retrieve metadata after execute. The file may be invalid or empty.")
            return


        print(f"Successfully loaded data: {count} points read.")

        # 1. Print Header Information / Metadata
        print("\\n--- Metadata ---")
        # PDAL metadata is a JSON string, parse it for pretty printing
        metadata = json.loads(pipeline.metadata)
        print(json.dumps(metadata, indent=2))

        # Extract some specific metadata (example)
        # The exact structure of metadata can vary. Inspect the output to find correct paths.
        # Typically, for LAS files, it's under 'metadata' -> 'readers.las' (or similar)
        las_reader_metadata = None
        if "metadata" in metadata and isinstance(metadata["metadata"], list):
            # This case might occur if metadata is a list of stages
            for stage_meta in metadata["metadata"]:
                if "readers.las" in stage_meta:
                    las_reader_metadata = stage_meta["readers.las"]
                    break
        elif "metadata" in metadata and "readers.las" in metadata["metadata"]:
             las_reader_metadata = metadata["metadata"]["readers.las"]
        elif "stages" in metadata: # Another common PDAL metadata structure
            if "readers.las" in metadata["stages"]:
                 las_reader_metadata = metadata["stages"]["readers.las"]

        if las_reader_metadata:
            # If it's a list, take the first element
            if isinstance(las_reader_metadata, list):
                las_reader_metadata = las_reader_metadata[0] if las_reader_metadata else {}

            print(f"Software Version: {las_reader_metadata.get('software_id', 'N/A')}")
            print(f"Creation Date: {las_reader_metadata.get('creation_doy', 'N/A')}/{las_reader_metadata.get('creation_year', 'N/A')}")
            print(f"Point Format ID: {las_reader_metadata.get('point_format_id', 'N/A')}")
            print(f"Point Count (from header): {las_reader_metadata.get('count', 'N/A')}")
            print(f"Scale X/Y/Z: {las_reader_metadata.get('scale_x')}, {las_reader_metadata.get('scale_y')}, {las_reader_metadata.get('scale_z')}")
            print(f"Offset X/Y/Z: {las_reader_metadata.get('offset_x')}, {las_reader_metadata.get('offset_y')}, {las_reader_metadata.get('offset_z')}")
        else:
            print("LAS reader specific metadata not found at expected path in JSON. Full metadata printed above.")


        # 2. Get the number of points
        # pipeline.execute() returns the count, or it's in the metadata.
        # The actual points are in pipeline.arrays
        num_points_array = len(pipeline.arrays[0]) if pipeline.arrays else 0
        print(f"\\n--- Number of Points ---")
        print(f"Number of points (from pipeline.execute()): {count}")
        print(f"Number of points (from pipeline.arrays[0].shape): {num_points_array}")


        # 3. Access a small subset of points and their attributes
        print("\\n--- Sample Points (First 5) ---")
        if pipeline.arrays and num_points_array > 0:
            points_array = pipeline.arrays[0] # Data is typically in the first array

            # List available dimensions/attributes
            print(f"Available dimensions: {points_array.dtype.names}")

            num_to_show = min(5, num_points_array)
            for i in range(num_to_show):
                point = points_array[i]
                # Adjust attribute names based on available dimensions
                # Common names: X, Y, Z, Intensity, ReturnNumber, NumberOfReturns, Classification
                print(f"Point {i+1}: ", end="")
                for dim_name in points_array.dtype.names:
                    print(f"{dim_name}={point[dim_name]} ", end="")
                print() # Newline for next point
        else:
            print("No point data available in pipeline.arrays to display.")

    except ImportError:
        print("Error: PDAL Python bindings not found.")
        print("If pymapgis relies on 'pdal' package, please ensure it's installed:")
        print("  pip install pdal")
        print("Alternatively, pymapgis might have its own installation method for PDAL support.")
    except RuntimeError as e:
        print(f"PDAL Runtime Error: {e}")
        print("This can happen if PDAL is not correctly installed or if there's an issue with the LAS file or pipeline.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    print("Starting Basic Point Cloud Example (LAS/LAZ)...")
    inspect_point_cloud_data()
    print("\\nPoint cloud example finished.")
