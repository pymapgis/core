"""
Point cloud processing capabilities for PyMapGIS using PDAL.

This module provides functions to read point cloud data (LAS/LAZ files),
extract metadata, points, and spatial reference system information.

**Important Note on PDAL Installation:**
PDAL is a powerful library for point cloud processing, but it can be
challenging to install correctly with all its drivers and dependencies using pip alone.
It is highly recommended to install PDAL using Conda:

  ```bash
  conda install -c conda-forge pdal python-pdal
  ```

If you have installed PDAL via Conda, ensure the Python environment running
PyMapGIS has access to the `pdal` Python bindings installed by Conda.
"""

import json
from typing import Dict, Any, List, Optional

try:
    import numpy as np
    import pdal  # Import PDAL Python bindings

    PDAL_AVAILABLE = True
except ImportError:
    PDAL_AVAILABLE = False
    np = None
    pdal = None

__all__ = [
    "read_point_cloud",
    "get_point_cloud_metadata",
    "get_point_cloud_points",
    "get_point_cloud_srs",
    "create_las_from_numpy",  # Added for testing
]


def read_point_cloud(filepath: str, **kwargs: Any) -> Any:
    """
    Reads a point cloud file (e.g., LAS, LAZ) using a PDAL pipeline.

    This function constructs a basic PDAL pipeline with a reader for the
    specified file and executes it. The returned pipeline object can then
    be used to extract points, metadata, etc.

    Args:
        filepath (str): Path to the point cloud file (LAS, LAZ, etc.).
        **kwargs: Additional options to pass to the PDAL reader stage.
                  For example, `count=1000` for `readers.las` to read only
                  the first 1000 points.

    Returns:
        pdal.Pipeline: The executed PDAL pipeline object.

    Raises:
        RuntimeError: If PDAL fails to read the file or execute the pipeline.
                      This often indicates an issue with the file, PDAL installation,
                      or driver availability.
        ImportError: If PDAL is not available.
    """
    if not PDAL_AVAILABLE:
        raise ImportError(
            "PDAL is not available. Install it with: poetry install --extras pointcloud"
        )
    pipeline_stages = [
        {
            "type": "readers.las",  # Default reader, PDAL auto-detects LAZ as well
            "filename": filepath,
            **kwargs,
        }
        # Example: Add a statistics filter if always desired by default
        # {
        #     "type": "filters.stats",
        #     "dimensions": "X,Y,Z" # Calculate stats for these dimensions
        # }
    ]

    pipeline_json = json.dumps(pipeline_stages)

    try:
        pipeline = pdal.Pipeline(pipeline_json)
        pipeline.execute()
    except RuntimeError as e:
        raise RuntimeError(
            f"PDAL pipeline execution failed for file '{filepath}'. "
            f"Ensure PDAL is correctly installed with necessary drivers and the file is valid. "
            f"Original error: {e}"
        ) from e

    return pipeline


def get_point_cloud_metadata(pipeline: Any) -> Dict[str, Any]:
    """
    Extracts metadata from an executed PDAL pipeline.

    Args:
        pipeline (pdal.Pipeline): An executed PDAL pipeline object.

    Returns:
        Dict[str, Any]: A dictionary containing metadata. This typically includes
                        information like point counts, schema, spatial reference, etc.
                        The exact content depends on the PDAL version and the source file.
    """
    if not PDAL_AVAILABLE:
        raise ImportError(
            "PDAL is not available. Install it with: poetry install --extras pointcloud"
        )
    if not isinstance(pipeline, pdal.Pipeline):
        raise TypeError("Input must be an executed pdal.Pipeline object.")

    # PDAL metadata is typically a list of dictionaries, one per stage.
    # The reader's metadata is usually the most relevant for file-level info.
    # pipeline.metadata should be JSON-like.
    # pipeline.quickinfo gives some high-level info from the first reader.
    # pipeline.metadata is a more comprehensive JSON string from all stages.

    try:
        # For PDAL Python bindings, metadata is often accessed as a dictionary
        # or a JSON string that needs parsing.
        # The `pipeline.metadata` attribute holds the full metadata of the pipeline.
        # Let's try to parse it as JSON.
        full_metadata = json.loads(pipeline.metadata)

        # We are typically interested in the reader's metadata or consolidated view.
        # 'quickinfo' provides some of this from the primary reader.
        # 'schema' provides the dimensions and types.
        metadata = {
            "quickinfo": (
                pipeline.quickinfo.get(next(iter(pipeline.quickinfo)))
                if pipeline.quickinfo
                else {}
            ),  # Get first reader's quickinfo
            "schema": pipeline.schema,  # This is often a string representation, might need parsing or use pipeline.dimensions
            "dimensions": pipeline.dimensions,  # JSON string of dimensions
            "metadata": full_metadata.get(
                "metadata", {}
            ),  # The actual metadata section from the JSON
        }
        srs_data = metadata["metadata"].get("readers.las", [{}])[0].get("srs", {})
        if not srs_data and "comp_spatialreference" in metadata["quickinfo"]:
            metadata["srs_wkt"] = metadata["quickinfo"]["comp_spatialreference"]
        elif srs_data.get("wkt"):
            metadata["srs_wkt"] = srs_data.get("wkt")

    except Exception as e:
        # Fallback or simpler metadata if above fails
        return {
            "error": f"Could not parse full metadata, returning basic info. Error: {e}",
            "log": pipeline.log,
            "points_count": len(pipeline.arrays[0]) if pipeline.arrays else 0,
        }
    return metadata


def get_point_cloud_points(pipeline: Any) -> Any:
    """
    Extracts points as a NumPy structured array from an executed PDAL pipeline.

    Args:
        pipeline (pdal.Pipeline): An executed PDAL pipeline object.

    Returns:
        np.ndarray: A NumPy structured array containing the point data.
                    Each row is a point, and fields correspond to dimensions
                    (e.g., 'X', 'Y', 'Z', 'Intensity').
                    Returns an empty array if the pipeline has no points.
    """
    if not isinstance(pipeline, pdal.Pipeline):
        raise TypeError("Input must be an executed pdal.Pipeline object.")

    if not pipeline.arrays:
        return np.array([])  # Return empty array if no data

    return pipeline.arrays[0]  # PDAL pipelines typically return one array


def get_point_cloud_srs(pipeline: Any) -> str:
    """
    Extracts Spatial Reference System (SRS) information from an executed PDAL pipeline.

    Args:
        pipeline (pdal.Pipeline): An executed PDAL pipeline object.

    Returns:
        str: The SRS information, typically in WKT (Well-Known Text) format.
             Returns an empty string if SRS information is not found.
    """
    if not isinstance(pipeline, pdal.Pipeline):
        raise TypeError("Input must be an executed pdal.Pipeline object.")

    # Attempt to get SRS from different metadata locations PDAL might use.
    # 1. From the consolidated metadata (often contains 'comp_spatialreference')
    try:
        meta = json.loads(pipeline.metadata)  # Full pipeline metadata
        # Check common places for SRS info
        # Reader specific metadata:
        if meta.get("metadata") and meta["metadata"].get("readers.las"):
            srs_info = meta["metadata"]["readers.las"][0].get("srs", {})
            if isinstance(srs_info, dict) and srs_info.get("wkt"):
                return srs_info["wkt"]
            # Sometimes it's directly 'comp_spatialreference' under the reader
            if isinstance(srs_info, dict) and srs_info.get(
                "compoundwkt"
            ):  # PDAL might use this
                return srs_info["compoundwkt"]

        # Quickinfo (often has compound WKT)
        # pipeline.quickinfo is a dict where keys are stage names.
        # Find the reader stage (usually the first one or 'readers.las')
        reader_stage_key = next(
            (k for k in pipeline.quickinfo if k.startswith("readers.")), None
        )
        if reader_stage_key and "srs" in pipeline.quickinfo[reader_stage_key]:
            srs_dict = pipeline.quickinfo[reader_stage_key]["srs"]
            if isinstance(srs_dict, dict) and srs_dict.get(
                "wkt"
            ):  # Newer PDAL versions
                return srs_dict["wkt"]
            if isinstance(srs_dict, dict) and srs_dict.get("compoundwkt"):
                return srs_dict["compoundwkt"]

        # Fallback to comp_spatialreference if available in quickinfo (older PDAL versions behavior)
        if (
            reader_stage_key
            and "comp_spatialreference" in pipeline.quickinfo[reader_stage_key]
        ):
            return pipeline.quickinfo[reader_stage_key]["comp_spatialreference"]

    except Exception:
        # If parsing fails or keys are not found, try to gracefully return empty or log error
        pass  # Fall through to other methods or return empty

    # If not found in structured metadata, sometimes it's in the general log (less reliable)
    # This is a last resort and might not be standard WKT.
    # For now, returning empty if not found in standard metadata fields.
    return ""


# Helper function for creating a dummy LAS file for testing purposes
def create_las_from_numpy(
    points_array: Any, output_filepath: str, srs_wkt: Optional[str] = None
) -> None:
    """
    Creates a LAS file from a NumPy structured array using a PDAL pipeline.
    This is primarily intended for testing.

    Args:
        points_array (np.ndarray): NumPy structured array of points. Must have
                                   fields like 'X', 'Y', 'Z'.
        output_filepath (str): The path where the LAS file will be saved.
        srs_wkt (Optional[str]): Spatial Reference System in WKT format to assign.

    Raises:
        RuntimeError: If PDAL fails to write the file.
    """
    if not isinstance(points_array, np.ndarray):
        raise TypeError("points_array must be a NumPy structured array.")
    if not output_filepath.lower().endswith(".las"):
        raise ValueError("output_filepath must end with .las")

    pipeline_stages: List[Dict[str, Any]] = [
        {"type": "readers.numpy", "array": points_array},
        {"type": "writers.las", "filename": output_filepath},
    ]

    if srs_wkt:
        # Add SRS to the writer stage
        pipeline_stages[-1]["spatialreference"] = srs_wkt
        # Or, use filters.assign to set SRS if writer doesn't handle it well for all PDAL versions
        # pipeline_stages.insert(1, {"type": "filters.assign", "value": f"EPSG:{epsg_code}"}) # if EPSG
        # pipeline_stages.insert(1, {"type": "filters.assign", "value": srs_wkt}) # if WKT

    pipeline_json = json.dumps(pipeline_stages)

    try:
        pipeline = pdal.Pipeline(pipeline_json)
        pipeline.execute()
    except RuntimeError as e:
        raise RuntimeError(
            f"PDAL pipeline failed to create LAS file '{output_filepath}'. "
            f"Ensure PDAL is correctly installed. Original error: {e}"
        ) from e
