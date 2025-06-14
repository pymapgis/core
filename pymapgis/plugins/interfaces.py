"""
Defines the Abstract Base Classes (ABCs) for PyMapGIS plugins.

These interfaces ensure that plugins conform to a standard API,
allowing PyMapGIS to discover and integrate them seamlessly.
"""

from abc import ABC, abstractmethod
from typing import Any


class PymapgisDriver(ABC):
    """
    Abstract Base Class for data driver plugins.

    Driver plugins are responsible for reading data from various sources
    and formats into a common PyMapGIS representation (e.g., GeoDataFrame).
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the unique name of the driver (e.g., 'shapefile', 'geopackage').
        """
        pass

    @abstractmethod
    def load_data(self, source: str, **kwargs: Any) -> Any:
        """
        Load data from the specified source.

        Args:
            source: Path or connection string to the data source.
            **kwargs: Driver-specific keyword arguments.

        Returns:
            Loaded data, typically a GeoDataFrame or similar structure.
        """
        pass


class PymapgisAlgorithm(ABC):
    """
    Abstract Base Class for algorithm plugins.

    Algorithm plugins provide specific geospatial processing capabilities
    that can be applied to data objects.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the unique name of the algorithm (e.g., 'buffer', 'overlay').
        """
        pass

    @abstractmethod
    def execute(self, data: Any, **kwargs: Any) -> Any:
        """
        Execute the algorithm on the given data.

        Args:
            data: Input data for the algorithm.
            **kwargs: Algorithm-specific parameters.

        Returns:
            Result of the algorithm execution.
        """
        pass


class PymapgisVizBackend(ABC):
    """
    Abstract Base Class for visualization backend plugins.

    Visualization plugins provide different ways to render and display
    geospatial data (e.g., using Matplotlib, Folium, etc.).
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the unique name of the visualization backend (e.g., 'matplotlib', 'folium').
        """
        pass

    @abstractmethod
    def plot(self, data: Any, **kwargs: Any) -> Any:
        """
        Generate a plot or map of the given data.

        Args:
            data: Data to be visualized.
            **kwargs: Plotting-specific parameters.

        Returns:
            A plot object, figure, map instance, or None.
        """
        pass
