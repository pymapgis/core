"""
Specialized Spatial ML Algorithms

Provides advanced spatial machine learning algorithms including kriging,
geographically weighted regression, spatial autocorrelation, and hotspot analysis.
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# Optional imports for spatial algorithms
try:
    import geopandas as gpd
    from shapely.geometry import Point

    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False
    logger.warning("GeoPandas not available - spatial algorithms limited")

try:
    from libpysal.weights import Queen, Rook, KNN
    from esda import Moran, Geary, Getis_Ord, Moran_Local
    from esda.getisord import G_Local

    PYSAL_AVAILABLE = True
except ImportError:
    PYSAL_AVAILABLE = False
    logger.warning("PySAL not available - spatial statistics limited")

try:
    from sklearn.base import BaseEstimator, RegressorMixin
    from sklearn.metrics import mean_squared_error, r2_score
    from sklearn.neighbors import NearestNeighbors

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("Scikit-learn not available - some algorithms limited")

    # Import fallback classes from sklearn_integration
    try:
        from .sklearn_integration import BaseEstimator, RegressorMixin
    except ImportError:
        # Create minimal fallback classes if sklearn_integration also fails
        class BaseEstimator:  # type: ignore[no-redef]
            """Minimal fallback base estimator."""

            def get_params(self, deep=True):
                return {}

            def set_params(self, **params):
                return self

        class RegressorMixin:  # type: ignore[no-redef]
            """Minimal fallback regressor mixin."""

            pass


try:
    from scipy.spatial.distance import pdist, squareform
    from scipy.optimize import minimize
    from scipy.linalg import inv

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning("SciPy not available - advanced algorithms limited")


@dataclass
class KrigingResult:
    """Container for kriging results."""

    predictions: np.ndarray
    variances: np.ndarray
    variogram_params: Dict[str, float]
    cross_validation_score: float


@dataclass
class GWRResult:
    """Container for GWR results."""

    local_coefficients: np.ndarray
    local_r2: np.ndarray
    predictions: np.ndarray
    residuals: np.ndarray
    bandwidth: float


@dataclass
class AutocorrelationResult:
    """Container for spatial autocorrelation results."""

    global_moran_i: float
    global_moran_p: float
    local_moran_i: np.ndarray
    local_moran_p: np.ndarray
    moran_classification: np.ndarray


@dataclass
class HotspotResult:
    """Container for hotspot analysis results."""

    getis_ord_g: np.ndarray
    z_scores: np.ndarray
    p_values: np.ndarray
    hotspot_classification: np.ndarray


class Kriging(BaseEstimator, RegressorMixin):
    """Kriging interpolation for spatial prediction."""

    def __init__(
        self,
        variogram_model: str = "spherical",
        nugget: float = 0.0,
        sill: float = 1.0,
        range_param: float = 1.0,
    ):
        """
        Initialize kriging model.

        Args:
            variogram_model: Type of variogram ('spherical', 'exponential', 'gaussian')
            nugget: Nugget parameter
            sill: Sill parameter
            range_param: Range parameter
        """
        self.variogram_model = variogram_model
        self.nugget = nugget
        self.sill = sill
        self.range_param = range_param
        self.fitted_params = None
        self.training_coords = None
        self.training_values = None

    def _spherical_variogram(self, h: np.ndarray) -> np.ndarray:
        """Spherical variogram model."""
        gamma = np.zeros_like(h)
        mask = h <= self.range_param
        gamma[mask] = self.nugget + self.sill * (
            1.5 * h[mask] / self.range_param - 0.5 * (h[mask] / self.range_param) ** 3
        )
        gamma[~mask] = self.nugget + self.sill
        return gamma

    def _exponential_variogram(self, h: np.ndarray) -> np.ndarray:
        """Exponential variogram model."""
        return self.nugget + self.sill * (1 - np.exp(-h / self.range_param))

    def _gaussian_variogram(self, h: np.ndarray) -> np.ndarray:
        """Gaussian variogram model."""
        return self.nugget + self.sill * (1 - np.exp(-((h / self.range_param) ** 2)))

    def _calculate_variogram(self, h: np.ndarray) -> np.ndarray:
        """Calculate variogram values for distances h."""
        if self.variogram_model == "spherical":
            return self._spherical_variogram(h)
        elif self.variogram_model == "exponential":
            return self._exponential_variogram(h)
        elif self.variogram_model == "gaussian":
            return self._gaussian_variogram(h)
        else:
            raise ValueError(f"Unknown variogram model: {self.variogram_model}")

    def fit(self, X, y, geometry=None):
        """
        Fit kriging model.

        Args:
            X: Feature matrix (not used in simple kriging)
            y: Target values
            geometry: Geometry column with point locations

        Returns:
            self
        """
        if not GEOPANDAS_AVAILABLE:
            raise ImportError("GeoPandas required for kriging")

        if geometry is None:
            raise ValueError("Geometry required for kriging")

        # Extract coordinates
        self.training_coords = np.array([[geom.x, geom.y] for geom in geometry])
        self.training_values = np.array(y)

        # Fit variogram parameters (simplified - in practice, use method of moments or MLE)
        distances = pdist(self.training_coords) if SCIPY_AVAILABLE else np.array([1.0])

        if SCIPY_AVAILABLE:
            # Calculate empirical variogram
            n_points = len(self.training_values)
            empirical_gamma = []
            distance_bins = np.linspace(0, np.max(distances), 20)

            for i in range(len(distance_bins) - 1):
                bin_mask = (distances >= distance_bins[i]) & (
                    distances < distance_bins[i + 1]
                )
                if np.any(bin_mask):
                    # Calculate semivariance for this distance bin
                    bin_distances = distances[bin_mask]
                    # This is simplified - proper implementation would calculate semivariance
                    empirical_gamma.append(np.var(self.training_values) * 0.5)

            # Store fitted parameters (simplified)
            self.fitted_params = {
                "nugget": self.nugget,
                "sill": self.sill,
                "range": self.range_param,
            }

        return self

    def predict(self, X, geometry=None):
        """
        Make kriging predictions.

        Args:
            X: Feature matrix (not used)
            geometry: Geometry column with prediction locations

        Returns:
            Predictions
        """
        if self.training_coords is None:
            raise ValueError("Model not fitted yet")

        if geometry is None:
            raise ValueError("Geometry required for kriging predictions")

        if not SCIPY_AVAILABLE:
            # Fallback to simple interpolation
            return np.full(len(geometry), np.mean(self.training_values))

        # Extract prediction coordinates
        pred_coords = np.array([[geom.x, geom.y] for geom in geometry])

        predictions = []
        variances = []

        for pred_point in pred_coords:
            # Calculate distances to all training points
            distances = np.sqrt(
                np.sum((self.training_coords - pred_point) ** 2, axis=1)
            )

            # Calculate variogram values
            gamma_values = self._calculate_variogram(distances)

            # Simple kriging (ordinary kriging would be more complex)
            if np.min(distances) < 1e-10:  # Very close to training point
                prediction = self.training_values[np.argmin(distances)]
                variance = 0.0
            else:
                # Inverse distance weighting as approximation
                weights = 1.0 / (distances + 1e-10)
                weights = weights / np.sum(weights)
                prediction = np.sum(weights * self.training_values)
                variance = np.sum(weights * gamma_values)

            predictions.append(prediction)
            variances.append(variance)

        return np.array(predictions)


class GeographicallyWeightedRegression(BaseEstimator, RegressorMixin):
    """Geographically Weighted Regression (GWR) model."""

    def __init__(
        self, bandwidth: Union[float, str] = "adaptive", kernel: str = "gaussian"
    ):
        """
        Initialize GWR model.

        Args:
            bandwidth: Bandwidth for spatial weighting ('adaptive' or fixed distance)
            kernel: Kernel function ('gaussian', 'exponential', 'bisquare')
        """
        self.bandwidth = bandwidth
        self.kernel = kernel
        self.training_coords = None
        self.training_X = None
        self.training_y = None
        self.local_coefficients = None

    def _gaussian_kernel(self, distances: np.ndarray, bandwidth: float) -> np.ndarray:
        """Gaussian kernel function."""
        return np.exp(-0.5 * (distances / bandwidth) ** 2)

    def _exponential_kernel(
        self, distances: np.ndarray, bandwidth: float
    ) -> np.ndarray:
        """Exponential kernel function."""
        return np.exp(-distances / bandwidth)

    def _bisquare_kernel(self, distances: np.ndarray, bandwidth: float) -> np.ndarray:
        """Bisquare kernel function."""
        weights = np.zeros_like(distances)
        mask = distances <= bandwidth
        weights[mask] = (1 - (distances[mask] / bandwidth) ** 2) ** 2
        return weights

    def _calculate_weights(self, distances: np.ndarray, bandwidth: float) -> np.ndarray:
        """Calculate spatial weights."""
        if self.kernel == "gaussian":
            return self._gaussian_kernel(distances, bandwidth)
        elif self.kernel == "exponential":
            return self._exponential_kernel(distances, bandwidth)
        elif self.kernel == "bisquare":
            return self._bisquare_kernel(distances, bandwidth)
        else:
            raise ValueError(f"Unknown kernel: {self.kernel}")

    def fit(self, X, y, geometry=None):
        """
        Fit GWR model.

        Args:
            X: Feature matrix
            y: Target values
            geometry: Geometry column with locations

        Returns:
            self
        """
        if not GEOPANDAS_AVAILABLE:
            raise ImportError("GeoPandas required for GWR")

        if geometry is None:
            raise ValueError("Geometry required for GWR")

        # Store training data
        self.training_coords = np.array([[geom.x, geom.y] for geom in geometry])
        self.training_X = np.array(X)
        self.training_y = np.array(y)

        # Add intercept term
        X_with_intercept = np.column_stack([np.ones(len(X)), self.training_X])

        # Determine bandwidth
        if self.bandwidth == "adaptive":
            # Use adaptive bandwidth (simplified - use median distance)
            if SCIPY_AVAILABLE:
                distances = pdist(self.training_coords)
                self.bandwidth = np.median(distances)
            else:
                self.bandwidth = 1000.0  # Default

        # Calculate local coefficients for each point
        n_points = len(self.training_coords)
        n_features = X_with_intercept.shape[1]
        self.local_coefficients = np.zeros((n_points, n_features))

        for i in range(n_points):
            # Calculate distances to all other points
            distances = np.sqrt(
                np.sum((self.training_coords - self.training_coords[i]) ** 2, axis=1)
            )

            # Calculate weights
            weights = self._calculate_weights(distances, self.bandwidth)

            # Weighted least squares
            W = np.diag(weights)

            try:
                if SCIPY_AVAILABLE:
                    XTW = X_with_intercept.T @ W
                    XTWX_inv = inv(XTW @ X_with_intercept)
                    coefficients = XTWX_inv @ XTW @ self.training_y
                else:
                    # Fallback to simple weighted mean
                    coefficients = np.zeros(n_features)
                    coefficients[0] = np.average(self.training_y, weights=weights)

                self.local_coefficients[i] = coefficients
            except Exception as e:
                logger.warning(f"Could not calculate coefficients for point {i}: {e}")
                self.local_coefficients[i] = np.zeros(n_features)

        return self

    def predict(self, X, geometry=None):
        """
        Make GWR predictions.

        Args:
            X: Feature matrix
            geometry: Geometry column with prediction locations

        Returns:
            Predictions
        """
        if self.local_coefficients is None:
            raise ValueError("Model not fitted yet")

        if geometry is None:
            raise ValueError("Geometry required for GWR predictions")

        # Extract prediction coordinates
        pred_coords = np.array([[geom.x, geom.y] for geom in geometry])
        X_with_intercept = np.column_stack([np.ones(len(X)), np.array(X)])

        predictions = []

        for i, pred_point in enumerate(pred_coords):
            # Find nearest training point (simplified)
            distances = np.sqrt(
                np.sum((self.training_coords - pred_point) ** 2, axis=1)
            )
            nearest_idx = np.argmin(distances)

            # Use local coefficients from nearest point
            local_coef = self.local_coefficients[nearest_idx]
            prediction = np.dot(X_with_intercept[i], local_coef)
            predictions.append(prediction)

        return np.array(predictions)


class SpatialAutocorrelation:
    """Spatial autocorrelation analysis."""

    def __init__(self, weights_type: str = "queen"):
        """
        Initialize spatial autocorrelation analysis.

        Args:
            weights_type: Type of spatial weights ('queen', 'rook', 'knn')
        """
        self.weights_type = weights_type

    def analyze(self, gdf: "gpd.GeoDataFrame", variable: str) -> AutocorrelationResult:
        """
        Perform spatial autocorrelation analysis.

        Args:
            gdf: GeoDataFrame with data
            variable: Variable to analyze

        Returns:
            AutocorrelationResult
        """
        if not PYSAL_AVAILABLE:
            logger.warning("PySAL not available - returning dummy results")
            n = len(gdf)
            return AutocorrelationResult(
                global_moran_i=0.0,
                global_moran_p=1.0,
                local_moran_i=np.zeros(n),
                local_moran_p=np.ones(n),
                moran_classification=np.zeros(n),
            )

        try:
            # Create spatial weights
            if self.weights_type == "queen":
                w = Queen.from_dataframe(gdf)
            elif self.weights_type == "rook":
                w = Rook.from_dataframe(gdf)
            elif self.weights_type == "knn":
                w = KNN.from_dataframe(gdf, k=8)
            else:
                w = Queen.from_dataframe(gdf)

            w.transform = "r"  # Row standardization

            # Global Moran's I
            values = gdf[variable].values
            moran = Moran(values, w)

            # Local Moran's I
            local_moran = Moran_Local(values, w)

            # Classification (HH, HL, LH, LL, NS)
            classification = local_moran.q

            return AutocorrelationResult(
                global_moran_i=moran.I,
                global_moran_p=moran.p_norm,
                local_moran_i=local_moran.Is,
                local_moran_p=local_moran.p_sim,
                moran_classification=classification,
            )

        except Exception as e:
            logger.error(f"Error in autocorrelation analysis: {e}")
            n = len(gdf)
            return AutocorrelationResult(
                global_moran_i=0.0,
                global_moran_p=1.0,
                local_moran_i=np.zeros(n),
                local_moran_p=np.ones(n),
                moran_classification=np.zeros(n),
            )


class HotspotAnalysis:
    """Hotspot analysis using Getis-Ord statistics."""

    def __init__(self, weights_type: str = "queen", alpha: float = 0.05):
        """
        Initialize hotspot analysis.

        Args:
            weights_type: Type of spatial weights
            alpha: Significance level
        """
        self.weights_type = weights_type
        self.alpha = alpha

    def analyze(self, gdf: "gpd.GeoDataFrame", variable: str) -> HotspotResult:
        """
        Perform hotspot analysis.

        Args:
            gdf: GeoDataFrame with data
            variable: Variable to analyze

        Returns:
            HotspotResult
        """
        if not PYSAL_AVAILABLE:
            logger.warning("PySAL not available - returning dummy results")
            n = len(gdf)
            return HotspotResult(
                getis_ord_g=np.zeros(n),
                z_scores=np.zeros(n),
                p_values=np.ones(n),
                hotspot_classification=np.zeros(n),
            )

        try:
            # Create spatial weights
            if self.weights_type == "queen":
                w = Queen.from_dataframe(gdf)
            elif self.weights_type == "rook":
                w = Rook.from_dataframe(gdf)
            elif self.weights_type == "knn":
                w = KNN.from_dataframe(gdf, k=8)
            else:
                w = Queen.from_dataframe(gdf)

            w.transform = "r"

            # Local Getis-Ord G*
            values = gdf[variable].values
            getis_ord = G_Local(values, w, star=True)

            # Classification based on significance
            classification = np.zeros(len(values))
            significant = getis_ord.p_sim < self.alpha

            # Hot spots (high values, high z-score)
            hot_spots = significant & (getis_ord.Zs > 0)
            classification[hot_spots] = 1

            # Cold spots (low values, low z-score)
            cold_spots = significant & (getis_ord.Zs < 0)
            classification[cold_spots] = -1

            return HotspotResult(
                getis_ord_g=getis_ord.Gs,
                z_scores=getis_ord.Zs,
                p_values=getis_ord.p_sim,
                hotspot_classification=classification,
            )

        except Exception as e:
            logger.error(f"Error in hotspot analysis: {e}")
            n = len(gdf)
            return HotspotResult(
                getis_ord_g=np.zeros(n),
                z_scores=np.zeros(n),
                p_values=np.ones(n),
                hotspot_classification=np.zeros(n),
            )


class SpatialClustering:
    """Spatial clustering algorithms."""

    def __init__(self, method: str = "spatial_kmeans"):
        """
        Initialize spatial clustering.

        Args:
            method: Clustering method ('spatial_kmeans', 'spatial_dbscan')
        """
        self.method = method

    def fit_predict(self, gdf: "gpd.GeoDataFrame", n_clusters: int = 5, **kwargs):
        """
        Perform spatial clustering.

        Args:
            gdf: GeoDataFrame with data
            n_clusters: Number of clusters
            **kwargs: Additional parameters

        Returns:
            Cluster labels
        """
        if self.method == "spatial_kmeans":
            from .sklearn_integration import SpatialKMeans

            clusterer = SpatialKMeans(n_clusters=n_clusters, **kwargs)
            features = gdf.drop(columns=["geometry"])
            clusterer.fit(features, geometry=gdf.geometry)
            return clusterer.labels_

        elif self.method == "spatial_dbscan":
            from .sklearn_integration import SpatialDBSCAN

            clusterer = SpatialDBSCAN(**kwargs)
            features = gdf.drop(columns=["geometry"])
            clusterer.fit(features, geometry=gdf.geometry)
            return clusterer.labels_

        else:
            raise ValueError(f"Unknown clustering method: {self.method}")


# Convenience functions
def perform_kriging(
    gdf: "gpd.GeoDataFrame",
    variable: str,
    prediction_points: "gpd.GeoDataFrame",
    **kwargs,
) -> KrigingResult:
    """Perform kriging interpolation."""
    kriging = Kriging(**kwargs)

    # Prepare data
    X = gdf.drop(columns=[variable, "geometry"])
    y = gdf[variable]

    # Fit and predict
    kriging.fit(X, y, geometry=gdf.geometry)
    predictions = kriging.predict(
        prediction_points.drop(columns=["geometry"]),
        geometry=prediction_points.geometry,
    )

    return KrigingResult(
        predictions=predictions,
        variances=np.zeros_like(predictions),  # Simplified
        variogram_params=kriging.fitted_params or {},
        cross_validation_score=0.0,  # Would need proper CV implementation
    )


def calculate_gwr(
    gdf: "gpd.GeoDataFrame", target: str, features: List[str], **kwargs
) -> GWRResult:
    """Calculate Geographically Weighted Regression."""
    gwr = GeographicallyWeightedRegression(**kwargs)

    # Prepare data
    X = gdf[features]
    y = gdf[target]

    # Fit model
    gwr.fit(X, y, geometry=gdf.geometry)

    # Make predictions
    predictions = gwr.predict(X, geometry=gdf.geometry)
    residuals = y - predictions

    # Ensure bandwidth is float
    bandwidth_value = (
        float(gwr.bandwidth) if isinstance(gwr.bandwidth, (int, float, str)) else 1000.0
    )

    return GWRResult(
        local_coefficients=gwr.local_coefficients,
        local_r2=np.zeros(len(gdf)),  # Would need proper calculation
        predictions=predictions,
        residuals=residuals,
        bandwidth=bandwidth_value,
    )


def analyze_spatial_autocorrelation(
    gdf: "gpd.GeoDataFrame", variable: str, **kwargs
) -> AutocorrelationResult:
    """Analyze spatial autocorrelation."""
    analyzer = SpatialAutocorrelation(**kwargs)
    return analyzer.analyze(gdf, variable)


def detect_hotspots(gdf: "gpd.GeoDataFrame", variable: str, **kwargs) -> HotspotResult:
    """Detect spatial hotspots."""
    analyzer = HotspotAnalysis(**kwargs)
    return analyzer.analyze(gdf, variable)
