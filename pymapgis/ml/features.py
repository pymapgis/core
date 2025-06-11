"""
Spatial Feature Engineering

Provides comprehensive spatial feature extraction capabilities including
geometric features, spatial statistics, and neighborhood analysis.
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Optional imports for spatial analysis
try:
    import geopandas as gpd
    from shapely.geometry import Point, Polygon, LineString
    from shapely.ops import unary_union

    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False
    logger.warning("GeoPandas not available - spatial features limited")

try:
    from libpysal.weights import Queen, Rook, KNN
    from esda import Moran, Geary, Getis_Ord

    PYSAL_AVAILABLE = True
except ImportError:
    PYSAL_AVAILABLE = False
    logger.warning("PySAL not available - spatial statistics limited")

try:
    from sklearn.neighbors import NearestNeighbors
    from sklearn.cluster import DBSCAN

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("Scikit-learn not available - some features limited")


@dataclass
class GeometricFeatures:
    """Container for geometric features."""

    area: float
    perimeter: float
    centroid_x: float
    centroid_y: float
    bounds_width: float
    bounds_height: float
    convex_hull_area: float
    aspect_ratio: float
    compactness: float
    shape_index: float


@dataclass
class SpatialStatistics:
    """Container for spatial statistics."""

    moran_i: Optional[float]
    geary_c: Optional[float]
    getis_ord_g: Optional[float]
    local_moran: Optional[np.ndarray]
    spatial_lag: Optional[np.ndarray]
    neighbor_count: Optional[np.ndarray]


class SpatialFeatureExtractor:
    """Comprehensive spatial feature extraction system."""

    def __init__(
        self, buffer_distances: List[float] = None, spatial_weights: str = "queen"
    ):
        """
        Initialize spatial feature extractor.

        Args:
            buffer_distances: List of buffer distances for neighborhood analysis
            spatial_weights: Type of spatial weights ('queen', 'rook', 'knn')
        """
        self.buffer_distances = buffer_distances or [100, 500, 1000]
        self.spatial_weights = spatial_weights

    def extract_geometric_features(self, gdf: "gpd.GeoDataFrame") -> pd.DataFrame:
        """
        Extract geometric features from geometries.

        Args:
            gdf: GeoDataFrame with geometries

        Returns:
            DataFrame with geometric features
        """
        if not GEOPANDAS_AVAILABLE:
            raise ImportError("GeoPandas required for geometric feature extraction")

        features = []

        for idx, geom in gdf.geometry.items():
            if geom is None or geom.is_empty:
                # Handle missing geometries
                feature = GeometricFeatures(
                    area=0,
                    perimeter=0,
                    centroid_x=0,
                    centroid_y=0,
                    bounds_width=0,
                    bounds_height=0,
                    convex_hull_area=0,
                    aspect_ratio=0,
                    compactness=0,
                    shape_index=0,
                )
            else:
                # Calculate basic geometric properties
                area = geom.area
                perimeter = geom.length
                centroid = geom.centroid
                bounds = geom.bounds
                convex_hull = geom.convex_hull

                # Calculate derived features
                bounds_width = bounds[2] - bounds[0]
                bounds_height = bounds[3] - bounds[1]
                aspect_ratio = bounds_width / bounds_height if bounds_height > 0 else 0

                # Compactness (isoperimetric quotient)
                compactness = (
                    (4 * np.pi * area) / (perimeter**2) if perimeter > 0 else 0
                )

                # Shape index (perimeter to area ratio)
                shape_index = perimeter / np.sqrt(area) if area > 0 else 0

                feature = GeometricFeatures(
                    area=area,
                    perimeter=perimeter,
                    centroid_x=centroid.x,
                    centroid_y=centroid.y,
                    bounds_width=bounds_width,
                    bounds_height=bounds_height,
                    convex_hull_area=convex_hull.area,
                    aspect_ratio=aspect_ratio,
                    compactness=compactness,
                    shape_index=shape_index,
                )

            features.append(feature)

        # Convert to DataFrame
        feature_df = pd.DataFrame([f.__dict__ for f in features], index=gdf.index)
        return feature_df

    def calculate_spatial_statistics(
        self, gdf: "gpd.GeoDataFrame", values: Optional[pd.Series] = None
    ) -> SpatialStatistics:
        """
        Calculate spatial statistics for the dataset.

        Args:
            gdf: GeoDataFrame with geometries
            values: Values for spatial autocorrelation analysis

        Returns:
            SpatialStatistics object
        """
        if not PYSAL_AVAILABLE:
            logger.warning("PySAL not available - spatial statistics limited")
            return SpatialStatistics(
                moran_i=None,
                geary_c=None,
                getis_ord_g=None,
                local_moran=None,
                spatial_lag=None,
                neighbor_count=None,
            )

        try:
            # Create spatial weights
            if self.spatial_weights == "queen":
                w = Queen.from_dataframe(gdf)
            elif self.spatial_weights == "rook":
                w = Rook.from_dataframe(gdf)
            elif self.spatial_weights == "knn":
                w = KNN.from_dataframe(gdf, k=8)
            else:
                w = Queen.from_dataframe(gdf)

            # Transform weights
            w.transform = "r"  # Row standardization

            # Calculate neighbor counts
            neighbor_count = np.array([len(w.neighbors[i]) for i in w.neighbors.keys()])

            if values is not None and len(values) > 0:
                # Global spatial autocorrelation
                moran = Moran(values, w)
                geary = Geary(values, w)
                getis_ord = Getis_Ord(values, w)

                # Local spatial autocorrelation
                local_moran = moran.Is

                # Spatial lag
                spatial_lag = w.sparse.dot(values)

                return SpatialStatistics(
                    moran_i=moran.I,
                    geary_c=geary.C,
                    getis_ord_g=getis_ord.G,
                    local_moran=local_moran,
                    spatial_lag=spatial_lag,
                    neighbor_count=neighbor_count,
                )
            else:
                return SpatialStatistics(
                    moran_i=None,
                    geary_c=None,
                    getis_ord_g=None,
                    local_moran=None,
                    spatial_lag=None,
                    neighbor_count=neighbor_count,
                )

        except Exception as e:
            logger.error(f"Error calculating spatial statistics: {e}")
            return SpatialStatistics(
                moran_i=None,
                geary_c=None,
                getis_ord_g=None,
                local_moran=None,
                spatial_lag=None,
                neighbor_count=None,
            )

    def analyze_neighborhoods(
        self, gdf: "gpd.GeoDataFrame", target_column: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Analyze neighborhood characteristics using buffer analysis.

        Args:
            gdf: GeoDataFrame with geometries
            target_column: Column to analyze in neighborhoods

        Returns:
            DataFrame with neighborhood features
        """
        if not GEOPANDAS_AVAILABLE:
            raise ImportError("GeoPandas required for neighborhood analysis")

        neighborhood_features = []

        for distance in self.buffer_distances:
            # Create buffers
            buffers = gdf.geometry.buffer(distance)

            # Calculate neighborhood features for each geometry
            for idx, buffer_geom in buffers.items():
                # Find neighbors within buffer
                neighbors = gdf[gdf.geometry.intersects(buffer_geom)]
                neighbors = neighbors[neighbors.index != idx]  # Exclude self

                # Basic neighborhood statistics
                neighbor_count = len(neighbors)
                neighbor_density = (
                    neighbor_count / buffer_geom.area if buffer_geom.area > 0 else 0
                )

                # Target variable statistics in neighborhood
                if (
                    target_column
                    and target_column in gdf.columns
                    and neighbor_count > 0
                ):
                    neighbor_values = neighbors[target_column].dropna()
                    if len(neighbor_values) > 0:
                        neighbor_mean = neighbor_values.mean()
                        neighbor_std = neighbor_values.std()
                        neighbor_min = neighbor_values.min()
                        neighbor_max = neighbor_values.max()
                    else:
                        neighbor_mean = neighbor_std = neighbor_min = neighbor_max = 0
                else:
                    neighbor_mean = neighbor_std = neighbor_min = neighbor_max = 0

                # Distance to nearest neighbor
                if neighbor_count > 0:
                    distances = neighbors.geometry.distance(gdf.geometry.iloc[idx])
                    nearest_distance = distances.min()
                    mean_distance = distances.mean()
                else:
                    nearest_distance = mean_distance = np.inf

                neighborhood_features.append(
                    {
                        f"neighbors_count_{distance}m": neighbor_count,
                        f"neighbors_density_{distance}m": neighbor_density,
                        f"neighbors_mean_{distance}m": neighbor_mean,
                        f"neighbors_std_{distance}m": neighbor_std,
                        f"neighbors_min_{distance}m": neighbor_min,
                        f"neighbors_max_{distance}m": neighbor_max,
                        f"nearest_distance_{distance}m": nearest_distance,
                        f"mean_distance_{distance}m": mean_distance,
                    }
                )

        # Combine all neighborhood features
        combined_features = {}
        for feature_dict in neighborhood_features:
            combined_features.update(feature_dict)

        # Create DataFrame with proper indexing
        feature_df = pd.DataFrame([combined_features] * len(gdf), index=gdf.index)

        # Fill individual rows with correct values
        for i, (idx, _) in enumerate(gdf.iterrows()):
            for j, distance in enumerate(self.buffer_distances):
                start_idx = j * 8  # 8 features per distance
                row_features = neighborhood_features[i * len(self.buffer_distances) + j]
                for k, (key, value) in enumerate(row_features.items()):
                    feature_df.loc[idx, key] = value

        return feature_df

    def extract_all_features(
        self, gdf: "gpd.GeoDataFrame", target_column: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Extract all spatial features.

        Args:
            gdf: GeoDataFrame with geometries
            target_column: Target column for spatial analysis

        Returns:
            DataFrame with all spatial features
        """
        features = []

        # Geometric features
        try:
            geometric_features = self.extract_geometric_features(gdf)
            features.append(geometric_features)
        except Exception as e:
            logger.warning(f"Could not extract geometric features: {e}")

        # Neighborhood features
        try:
            neighborhood_features = self.analyze_neighborhoods(gdf, target_column)
            features.append(neighborhood_features)
        except Exception as e:
            logger.warning(f"Could not extract neighborhood features: {e}")

        # Combine all features
        if features:
            combined_features = pd.concat(features, axis=1)
            return combined_features
        else:
            return pd.DataFrame(index=gdf.index)


class NeighborhoodAnalysis:
    """Specialized neighborhood analysis tools."""

    def __init__(self, method: str = "buffer"):
        """
        Initialize neighborhood analysis.

        Args:
            method: Analysis method ('buffer', 'knn', 'delaunay')
        """
        self.method = method

    def find_neighbors(
        self, gdf: "gpd.GeoDataFrame", distance: float = 1000, k: int = 8
    ) -> Dict[int, List[int]]:
        """
        Find neighbors for each geometry.

        Args:
            gdf: GeoDataFrame with geometries
            distance: Buffer distance for buffer method
            k: Number of neighbors for KNN method

        Returns:
            Dictionary mapping indices to neighbor lists
        """
        if not GEOPANDAS_AVAILABLE:
            raise ImportError("GeoPandas required for neighbor analysis")

        neighbors = {}

        if self.method == "buffer":
            for idx, geom in gdf.geometry.items():
                buffer_geom = geom.buffer(distance)
                neighbor_indices = gdf[
                    gdf.geometry.intersects(buffer_geom)
                ].index.tolist()
                neighbor_indices.remove(idx)  # Remove self
                neighbors[idx] = neighbor_indices

        elif self.method == "knn" and SKLEARN_AVAILABLE:
            # Extract centroids for KNN
            centroids = np.array(
                [[geom.centroid.x, geom.centroid.y] for geom in gdf.geometry]
            )

            # Fit KNN model
            knn = NearestNeighbors(n_neighbors=k + 1)  # +1 to exclude self
            knn.fit(centroids)

            # Find neighbors
            distances, indices = knn.kneighbors(centroids)

            for i, neighbor_indices in enumerate(indices):
                # Exclude self (first neighbor)
                neighbors[gdf.index[i]] = [gdf.index[j] for j in neighbor_indices[1:]]

        return neighbors


# Convenience functions
def extract_geometric_features(gdf: "gpd.GeoDataFrame") -> pd.DataFrame:
    """Extract geometric features using default extractor."""
    extractor = SpatialFeatureExtractor()
    return extractor.extract_geometric_features(gdf)


def calculate_spatial_statistics(
    gdf: "gpd.GeoDataFrame", values: Optional[pd.Series] = None
) -> SpatialStatistics:
    """Calculate spatial statistics using default extractor."""
    extractor = SpatialFeatureExtractor()
    return extractor.calculate_spatial_statistics(gdf, values)


def analyze_neighborhoods(
    gdf: "gpd.GeoDataFrame", target_column: Optional[str] = None
) -> pd.DataFrame:
    """Analyze neighborhoods using default extractor."""
    extractor = SpatialFeatureExtractor()
    return extractor.analyze_neighborhoods(gdf, target_column)
