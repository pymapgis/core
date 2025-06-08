import pdal
import numpy as np
import json # For constructing pipeline if using JSON string
from typing import List, Any # Any for pipeline arrays if structure varies

# Define what is accessible when importing * from this module
__all__ = ["read_las"]


def read_las(filepath: str) -> List[np.ndarray]:
    """
    Reads a LAS or LAZ file using a PDAL pipeline and returns the point data as NumPy arrays.

    This function creates a simple PDAL pipeline to read the specified LAS/LAZ file.
    The pipeline is then executed, and the resulting point cloud data is returned.
    PDAL (Point Data Abstraction Library) must be installed and configured correctly
    for this function to work. See https://pdal.io/ for more information.

    Args:
        filepath (str): The path to the LAS or LAZ file to be read.

    Returns:
        List[np.ndarray]: A list containing one or more NumPy structured arrays.
                          Each array represents a point view from the PDAL pipeline
                          (typically one for a simple read operation). The fields in
                          the structured array correspond to the dimensions found in
                          the LAS/LAZ file (e.g., X, Y, Z, Intensity, ReturnNumber).

    Raises:
        FileNotFoundError: If the specified `filepath` does not exist.
        RuntimeError: If PDAL encounters an error during pipeline creation or
                      execution (e.g., invalid file format, PDAL configuration issue).
                      The original PDAL error message will be included.
    """
    try:
        # Construct the PDAL pipeline as a Python dictionary (or JSON string)
        # Using a dictionary is often cleaner in Python.
        pipeline_config = {
            "pipeline": [
                {
                    "type": "readers.las",
                    "filename": filepath
                }
                # Add other stages here if needed, e.g., filters, writers
            ]
        }

        # Create a PDAL Pipeline object from the configuration
        # pdal.Pipeline expects a JSON string, so convert dict to JSON
        pipeline = pdal.Pipeline(json.dumps(pipeline_config))

    except FileNotFoundError as e: # Should be caught by Python if filepath is invalid before PDAL
        raise FileNotFoundError(f"The LAS/LAZ file was not found: {filepath}") from e
    except Exception as e: # Catch errors during pipeline construction (e.g. bad JSON if built manually)
        raise RuntimeError(f"Failed to create PDAL pipeline for file '{filepath}'. Error: {e}")

    try:
        # Execute the pipeline
        count = pipeline.execute()
        if count == 0 and not pipeline.arrays: # Check if any points were actually read
             # PDAL might execute successfully but read 0 points from an empty or bad file.
             # pipeline.arrays would be empty.
             # Depending on desired behavior, this could be a warning or an error.
             # For now, we'll let it return an empty list if PDAL does so.
             pass

        # Get the data as a list of NumPy structured arrays
        arrays = pipeline.arrays
        return arrays

    except RuntimeError as e: # PDAL often raises RuntimeError for execution issues
        # Attempt to get more specific error from PDAL log if possible
        log = pipeline.log
        error_message = f"PDAL pipeline execution failed for file '{filepath}'. PDAL Error: {e}"
        if log:
            error_message += f"\nPDAL Log:\n{log}"
        raise RuntimeError(error_message) from e
    except Exception as e: # Catch any other unexpected errors during execution
        raise RuntimeError(f"An unexpected error occurred during PDAL pipeline execution for '{filepath}'. Error: {e}")

# Example usage (not part of the library code, for testing/illustration):
# if __name__ == '__main__':
#     # Create a dummy LAS file for testing (requires a library like 'laspy')
#     # Or have a sample LAS file available.
#     # For now, this example assumes a file 'test.las' exists.
#     try:
#         # data = read_las("path_to_your_file.las")
#         # if data:
#         #     print(f"Read {len(data[0])} points from the LAS file.")
#         #     print(f"Point data fields: {data[0].dtype.names}")
#         # else:
#         #     print("No data returned from LAS file.")
#         pass # Placeholder for example
#     except Exception as e:
#         print(f"Error: {e}")
