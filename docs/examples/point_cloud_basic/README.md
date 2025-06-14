# Basic Point Cloud Example (LAS/LAZ)

This example aims to demonstrate basic loading and inspection of point cloud data from LAS/LAZ files using `pymapgis`, which would typically rely on the PDAL (Point Data Abstraction Library) in the backend.

**IMPORTANT NOTE:** As of the current environment setup, the core PDAL C++ library (a prerequisite for its Python bindings) is not available in the standard system repositories. This prevents the successful installation of `pdal` Python package and thus hinders the execution of the example script (`point_cloud_example.py`) as intended. The script is provided to illustrate how one might interact with point cloud data via PDAL's Python API (which `pymapgis` would likely wrap or expose).

## Functionality (Intended)

The `point_cloud_example.py` script is designed to:

1.  **Load Data:** Read a sample LAS file (`sample.las`) using PDAL's pipeline mechanism.
2.  **Print Metadata:** Display header information and metadata from the LAS file.
3.  **Count Points:** Show the total number of points in the file.
4.  **Access Points:** Retrieve and print a small subset of points along with their attributes (e.g., X, Y, Z, Intensity).

## `sample.las`

The `sample.las` file included in this directory is a small, simple LAS file from the PDAL repository, intended for basic testing and demonstration. It contains 1065 points.

## Dependencies (Required for the script to work)

To run this example successfully, a full PDAL installation is required:

*   **PDAL Core Library (C++)**: This must be installed on your system. Installation methods vary by OS (e.g., `apt-get install libpdal-dev pdal` on some Ubuntu versions, or building from source).
    *   *Currently, this is the blocking dependency in the provided environment.*
*   **PDAL Python Bindings**: The `pdal` Python package. This can typically be installed via pip, but requires the C++ library to be present.
    ```bash
    pip install pdal numpy
    ```
*   `pymapgis`: The core library (assumed to be in your environment, and would ideally handle PDAL integration).
*   `numpy`: For array manipulations.

## How to Run (Requires successful PDAL installation)

1.  **Ensure PDAL is installed:** Verify that both the PDAL C++ library and the Python bindings are correctly installed on your system. This is currently not possible in the automated test environment.
2.  **Navigate to the example directory:**
    ```bash
    cd path/to/your/pymapgis/docs/examples/point_cloud_basic/
    ```
3.  **Run the script:**
    ```bash
    python point_cloud_example.py
    ```

## Expected Output (If PDAL were functional)

If PDAL were correctly installed and operational, the script would output:

*   Status messages about loading the point cloud data.
*   **Metadata:** A JSON representation of the LAS file's header and metadata, including software version, creation date, point format, point count, and coordinate system information or scale/offset values.
*   **Number of Points:** The total count of points read from the file (e.g., "Number of points: 1065").
*   **Sample Points:** Attributes (like X, Y, Z, Intensity, ReturnNumber, Classification) for the first few points in the file.

Due to the current inability to install PDAL, running the script will likely result in import errors or PDAL runtime errors.
