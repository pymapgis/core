# Cloud-Native Zarr Analysis Example

This example demonstrates how to use `pymapgis` to access and perform a simple analysis on a publicly available Zarr store, showcasing cloud-native geospatial data handling. The specific dataset used is the ERA5 air temperature data, accessed from an AWS S3 bucket.

## Functionality

The `zarr_example.py` script performs the following actions:

1.  **Connects to a Zarr store:** It uses `pymapgis` to open a Zarr dataset representing air temperature at 2 metres from the ERA5 collection, specifically for January 2022. The data is stored on AWS S3 and accessed publicly.
2.  **Inspects dataset metadata:** It prints the name of the dataset and its dimensions.
3.  **Performs lazy windowed reading and analysis:**
    *   It selects a small spatial slice (10x10 grid points) for the first time step.
    *   It calculates the mean and maximum temperature within this slice. The calculation is "lazy," meaning data is only loaded from the cloud when the `.compute()` method is called.
    *   It demonstrates accessing a single data point from a different time step and location, further highlighting the ability to efficiently read small windows of data without downloading the entire dataset.
4.  **Prints results:** The script outputs the dataset information, the shape of the selected slice, the calculated mean and maximum temperatures, and the value of the single data point.

## Dependencies

To run this example, you will need:

*   `pymapgis`: The core library for geospatial data analysis.
*   `xarray[zarr]`: `pymapgis` uses `xarray` under the hood, and `xarray[zarr]` provides Zarr support.
*   `s3fs`: Required by `xarray` to access Zarr stores hosted on AWS S3.
*   `aiohttp`: Often a dependency for asynchronous operations with `s3fs`.

You can typically install these using pip:

```bash
pip install pymapgis xarray[zarr] s3fs aiohttp
```

Ensure your environment is configured with AWS credentials if you were accessing private S3 buckets. However, this example uses a public dataset, so anonymous access should be sufficient (as configured in the script with `storage_options={'anon': True}`).

## How to Run

1.  **Navigate to the example directory:**
    ```bash
    cd path/to/your/pymapgis/docs/examples/cloud_native_zarr/
    ```
2.  **Run the script:**
    ```bash
    python zarr_example.py
    ```

## Expected Output

The script will print information similar to the following (exact temperature values may vary slightly depending on the dataset version or if the specific slice chosen has no data):

```
Starting Zarr example for cloud-native analysis...
Successfully opened Zarr dataset: air_temperature_at_2_metres
\nDataset dimensions:
- lat: 721
- lon: 1440
- time1: 744
\nSelected data slice shape: (10, 10)
\nMean temperature in the selected slice: XXX.XX K
Max temperature in the selected slice: YYY.YY K
\nTemperature at a specific point (time1=5, lat=20, lon=30): ZZZ.ZZ K
\nZarr example finished.
```

If you encounter errors related to missing modules (e.g., `No module named 's3fs'`), please ensure you have installed all the required dependencies as listed above. If there are errors accessing the data, it might be due to network issues or changes in the public dataset's availability or structure.
