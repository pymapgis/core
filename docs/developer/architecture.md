# PyMapGIS Architecture

This document provides a high-level overview of the PyMapGIS library's architecture. Understanding the architecture is crucial for effective contribution and extension.

## Core Components

PyMapGIS is designed with a modular architecture. The key components are:

1.  **`pymapgis.io` (Data I/O)**:
    *   Handles the reading and writing of geospatial data from various sources.
    *   Uses a URI-based system (e.g., `census://`, `tiger://`, `file://`) to identify and access data sources.
    *   Responsible for dispatching requests to appropriate data handlers.

2.  **Data Source Handlers (within `pymapgis.io` or plugins)**:
    *   Specific modules or classes that know how to fetch and parse data from a particular source (e.g., Census API, TIGER/Line shapefiles, local GeoJSON files).
    *   These handlers are registered with the I/O system.

3.  **`pymapgis.acs` / `pymapgis.tiger` (Specific Data Source Clients)**:
    *   Modules that implement the logic for interacting with specific APIs like the Census ACS or TIGER/Line web services.
    *   They handle API-specific parameters, data fetching, and initial parsing.

4.  **`pymapgis.cache` (Caching System)**:
    *   Provides a caching layer for data fetched from remote sources (primarily web APIs).
    *   Helps in reducing redundant API calls and speeding up data retrieval.
    *   Configurable for cache expiration and storage.

5.  **`pymapgis.plotting` (Visualization Engine)**:
    *   Integrates with libraries like Leafmap to provide interactive mapping capabilities.
    *   Offers a simple `.plot` API on GeoDataFrames (or similar structures) for creating common map types (e.g., choropleth maps).

6.  **`pymapgis.settings` (Configuration Management)**:
    *   Manages global settings for the library, such as API keys (if needed), cache configurations, and default behaviors.

## Data Flow Example (Reading Census Data)

1.  **User Call**: `pmg.read("census://acs/acs5?year=2022&variables=B01003_001E")`
2.  **`pymapgis.io`**:
    *   Parses the URI to identify the data source (`census`) and parameters.
    *   Delegates the request to the Census ACS handler.
3.  **Census ACS Handler (e.g., functions in `pymapgis.acs`)**:
    *   Constructs the appropriate API request for the US Census Bureau.
    *   Checks the cache (`pymapgis.cache`) to see if the data is already available and valid.
    *   If not cached or expired, fetches data from the Census API.
    *   Stores the fetched data in the cache.
    *   Parses the API response into a structured format (typically a Pandas DataFrame with a geometry column, i.e., a GeoDataFrame).
4.  **Return**: The GeoDataFrame is returned to the user.

## Extensibility

PyMapGIS is designed to be extensible:

*   **New Data Sources**: Developers can add support for new data sources by creating new data handlers and registering them with the `pymapgis.io` system. This often involves creating a new module similar to `pymapgis.acs` or `pymapgis.tiger` if the source is complex, or a simpler handler if it's straightforward.
*   **New Plotting Functions**: Additional plotting functionalities can be added to `pymapgis.plotting` or by extending the `.plot` accessor.

Understanding these components and their interactions should provide a solid foundation for developing and extending PyMapGIS.
