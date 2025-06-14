import pymapgis

def analyze_era5_data():
    """
    Accesses and analyzes a slice of the ERA5 weather dataset from a public Zarr store.
    """
    # Zarr store URL for ERA5 air temperature data
    era5_zarr_url = "s3://era5-pds/zarr/2022/01/data/air_temperature_at_2_metres.zarr"

    # Open the Zarr store using pymapgis
    # We need to specify the s3 storage option for Zarr
    try:
        dataset = pymapgis.open_dataset(era5_zarr_url, engine="zarr", storage_options={'anon': True})
    except Exception as e:
        print(f"Error opening Zarr dataset: {e}")
        print("Please ensure you have the necessary dependencies installed (e.g., s3fs, zarr).")
        print("You might need to install them using: pip install s3fs zarr")
        return

    print(f"Successfully opened Zarr dataset: {dataset.name}")
    print("\\nDataset dimensions:")
    for dim_name, size in dataset.dims.items():
        print(f"- {dim_name}: {size}")

    # Example: Load a small spatial and temporal slice of the data
    # Let's select data for the first time step, and a small latitude/longitude window
    # The exact dimension names might vary, you may need to inspect `dataset.coords` or `dataset.dims`
    # Common names are 'time', 'lat', 'lon' or 'latitude', 'longitude'
    # For ERA5, common names are 'time1', 'lat', 'lon'
    try:
        # Assuming these are the correct dimension names for ERA5 data.
        # If you encounter errors, print dataset.coords or dataset.variables to check.
        data_slice = dataset['air_temperature_at_2_metres'].isel(time1=0, lat=slice(0, 10), lon=slice(0, 10))
        print("\\nSelected data slice shape:", data_slice.shape)

        # Perform a simple calculation (e.g., mean temperature)
        # This demonstrates lazy loading - data is only loaded when compute() or load() is called.
        mean_temp = data_slice.mean().compute() # .compute() triggers the actual data loading and calculation
        max_temp = data_slice.max().compute()

        print(f"\\nMean temperature in the selected slice: {mean_temp.item():.2f} K")
        print(f"Max temperature in the selected slice: {max_temp.item():.2f} K")

        # Demonstrate lazy windowed reading by accessing a specific point
        # This shows that we don't need to load the whole slice to get a small part
        point_data = dataset['air_temperature_at_2_metres'].isel(time1=5, lat=20, lon=30).compute()
        print(f"\\nTemperature at a specific point (time1=5, lat=20, lon=30): {point_data.item():.2f} K")

    except KeyError as e:
        print(f"\\nError accessing data variable or dimension: {e}")
        print("Please check the variable and dimension names in the Zarr store.")
        print("Available variables:", list(dataset.variables))
        print("Available coordinates:", list(dataset.coords))
    except Exception as e:
        print(f"\\nAn error occurred during data analysis: {e}")

    dataset.close()

if __name__ == "__main__":
    print("Starting Zarr example for cloud-native analysis...")
    analyze_era5_data()
    print("\\nZarr example finished.")
