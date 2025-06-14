"""
Scikit-learn Integration for Spatial ML

Provides spatial-aware wrappers and extensions for scikit-learn algorithms,
including spatial preprocessing, cross-validation, and model pipelines.
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# Optional imports for ML functionality
try:
    import geopandas as gpd
    from shapely.geometry import Point

    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False
    logger.warning("GeoPandas not available - spatial ML features limited")

try:
    from sklearn.base import (
        BaseEstimator,
        TransformerMixin,
        ClusterMixin,
        RegressorMixin,
        ClassifierMixin,
    )
    from sklearn.model_selection import train_test_split, cross_val_score, KFold
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
    from sklearn.linear_model import LinearRegression, LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.metrics import accuracy_score, r2_score, silhouette_score

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("Scikit-learn not available - ML functionality disabled")

    # Create fallback base classes when sklearn is not available
    class BaseEstimator:  # type: ignore[no-redef]
        """Fallback base estimator when sklearn not available."""

        def get_params(self, deep=True):
            return {}

        def set_params(self, **params):
            return self

    class TransformerMixin:  # type: ignore[no-redef]
        """Fallback transformer mixin when sklearn not available."""

        def fit_transform(self, X, y=None, **fit_params):
            return self.fit(X, y, **fit_params).transform(X)

    class ClusterMixin:  # type: ignore[no-redef]
        """Fallback cluster mixin when sklearn not available."""

        pass

    class RegressorMixin:  # type: ignore[no-redef]
        """Fallback regressor mixin when sklearn not available."""

        pass

    class ClassifierMixin:  # type: ignore[no-redef]
        """Fallback classifier mixin when sklearn not available."""

        pass

    class Pipeline:  # type: ignore[no-redef]
        """Fallback pipeline when sklearn not available."""

        def __init__(self, steps):
            self.steps = steps

        def fit(self, X, y=None, **fit_params):
            return self

        def predict(self, X):
            return np.zeros(len(X))

    class StandardScaler:  # type: ignore[no-redef]
        """Fallback scaler when sklearn not available."""

        def fit(self, X, y=None):
            return self

        def transform(self, X):
            return X

        def fit_transform(self, X, y=None):
            return X

    class LabelEncoder:  # type: ignore[no-redef]
        """Fallback encoder when sklearn not available."""

        def fit(self, y):
            return self

        def transform(self, y):
            return y

        def fit_transform(self, y):
            return y

    class KMeans:  # type: ignore[no-redef]
        """Fallback KMeans when sklearn not available."""

        def __init__(self, n_clusters=8, **kwargs):
            self.n_clusters = n_clusters
            self.labels_ = None

        def fit(self, X, y=None):
            self.labels_ = np.zeros(len(X))
            return self

        def predict(self, X):
            return np.zeros(len(X))

    class DBSCAN:  # type: ignore[no-redef]
        """Fallback DBSCAN when sklearn not available."""

        def __init__(self, eps=0.5, min_samples=5, **kwargs):
            self.eps = eps
            self.min_samples = min_samples
            self.labels_ = None

        def fit(self, X, y=None):
            self.labels_ = np.zeros(len(X))
            return self

    class RandomForestRegressor:  # type: ignore[no-redef]
        """Fallback RandomForestRegressor when sklearn not available."""

        def fit(self, X, y):
            return self

        def predict(self, X):
            return np.zeros(len(X))

    class RandomForestClassifier:  # type: ignore[no-redef]
        """Fallback RandomForestClassifier when sklearn not available."""

        def fit(self, X, y):
            return self

        def predict(self, X):
            return np.zeros(len(X))

        def predict_proba(self, X):
            return np.zeros((len(X), 2))

    def train_test_split(*arrays, test_size=0.2, random_state=None):
        """Fallback train_test_split when sklearn not available."""
        n_samples = len(arrays[0])
        n_test = int(n_samples * test_size)
        indices = np.arange(n_samples)
        if random_state:
            np.random.seed(random_state)
        np.random.shuffle(indices)

        train_idx = indices[n_test:]
        test_idx = indices[:n_test]

        result = []
        for array in arrays:
            if hasattr(array, "iloc"):
                result.extend([array.iloc[train_idx], array.iloc[test_idx]])
            else:
                result.extend([array[train_idx], array[test_idx]])

        return result

    def cross_val_score(estimator, X, y, cv=5, scoring=None):
        """Fallback cross_val_score when sklearn not available."""
        return np.zeros(cv)

    def accuracy_score(y_true, y_pred):
        """Fallback accuracy_score when sklearn not available."""
        return 0.0

    def r2_score(y_true, y_pred):
        """Fallback r2_score when sklearn not available."""
        return 0.0

    class KFold:  # type: ignore[no-redef]
        """Fallback KFold when sklearn not available."""

        def __init__(self, n_splits=5, shuffle=False, random_state=None):
            self.n_splits = n_splits
            self.shuffle = shuffle
            self.random_state = random_state

        def split(self, X, y=None):
            n_samples = len(X)
            indices = np.arange(n_samples)
            if self.shuffle:
                if self.random_state:
                    np.random.seed(self.random_state)
                np.random.shuffle(indices)

            fold_size = n_samples // self.n_splits
            for i in range(self.n_splits):
                start = i * fold_size
                end = start + fold_size if i < self.n_splits - 1 else n_samples
                test_idx = indices[start:end]
                train_idx = np.concatenate([indices[:start], indices[end:]])
                yield train_idx, test_idx


class SpatialPreprocessor(BaseEstimator, TransformerMixin):
    """Spatial-aware data preprocessor."""

    def __init__(
        self,
        include_spatial_features: bool = True,
        buffer_distances: List[float] = None,
    ):
        """
        Initialize spatial preprocessor.

        Args:
            include_spatial_features: Whether to include spatial features
            buffer_distances: Buffer distances for spatial feature extraction
        """
        self.include_spatial_features = include_spatial_features
        self.buffer_distances = buffer_distances or [100, 500, 1000]
        self.feature_extractor = None
        self.scaler = None

    def fit(self, X, y=None, geometry=None):
        """
        Fit the preprocessor.

        Args:
            X: Feature matrix
            y: Target variable (optional)
            geometry: Geometry column for spatial features

        Returns:
            self
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("Scikit-learn required for preprocessing")

        # Initialize scaler
        self.scaler = StandardScaler()

        # Prepare features
        features = X.copy()

        if self.include_spatial_features and geometry is not None:
            # Extract spatial features
            from .features import SpatialFeatureExtractor

            self.feature_extractor = SpatialFeatureExtractor(
                buffer_distances=self.buffer_distances
            )

            if GEOPANDAS_AVAILABLE:
                # Create temporary GeoDataFrame
                temp_gdf = gpd.GeoDataFrame(X, geometry=geometry)
                spatial_features = self.feature_extractor.extract_all_features(temp_gdf)
                features = pd.concat([features, spatial_features], axis=1)

        # Fit scaler on all features
        self.scaler.fit(features)

        return self

    def transform(self, X, geometry=None):
        """
        Transform the data.

        Args:
            X: Feature matrix
            geometry: Geometry column for spatial features

        Returns:
            Transformed feature matrix
        """
        features = X.copy()

        if (
            self.include_spatial_features
            and geometry is not None
            and self.feature_extractor
        ):
            if GEOPANDAS_AVAILABLE:
                # Create temporary GeoDataFrame
                temp_gdf = gpd.GeoDataFrame(X, geometry=geometry)
                spatial_features = self.feature_extractor.extract_all_features(temp_gdf)
                features = pd.concat([features, spatial_features], axis=1)

        # Scale features
        if self.scaler:
            scaled_features = self.scaler.transform(features)
            return pd.DataFrame(
                scaled_features, columns=features.columns, index=features.index
            )

        return features


class SpatialPipeline(Pipeline):
    """Spatial-aware ML pipeline."""

    def __init__(self, steps, spatial_features: bool = True):
        """
        Initialize spatial pipeline.

        Args:
            steps: Pipeline steps
            spatial_features: Whether to include spatial features
        """
        super().__init__(steps)
        self.spatial_features = spatial_features
        self.geometry = None

    def fit(self, X, y=None, geometry=None, **fit_params):
        """
        Fit the pipeline with spatial awareness.

        Args:
            X: Feature matrix
            y: Target variable
            geometry: Geometry column
            **fit_params: Additional fit parameters

        Returns:
            self
        """
        self.geometry = geometry

        # Add geometry to fit_params for spatial steps
        if geometry is not None:
            fit_params["geometry"] = geometry

        return super().fit(X, y, **fit_params)

    def predict(self, X, geometry=None):
        """
        Make predictions with spatial awareness.

        Args:
            X: Feature matrix
            geometry: Geometry column

        Returns:
            Predictions
        """
        # Use stored geometry if not provided
        if geometry is None:
            geometry = self.geometry

        # Transform with geometry information
        X_transformed = X
        for name, transformer in self.steps[:-1]:
            if hasattr(transformer, "transform"):
                if "geometry" in transformer.transform.__code__.co_varnames:
                    X_transformed = transformer.transform(
                        X_transformed, geometry=geometry
                    )
                else:
                    X_transformed = transformer.transform(X_transformed)

        # Final prediction
        final_estimator = self.steps[-1][1]
        return final_estimator.predict(X_transformed)


class SpatialKMeans(BaseEstimator, ClusterMixin):
    """Spatial-aware K-Means clustering."""

    def __init__(self, n_clusters: int = 8, spatial_weight: float = 0.5, **kwargs):
        """
        Initialize spatial K-Means.

        Args:
            n_clusters: Number of clusters
            spatial_weight: Weight for spatial features (0-1)
            **kwargs: Additional KMeans parameters
        """
        self.n_clusters = n_clusters
        self.spatial_weight = spatial_weight
        self.kwargs = kwargs
        self.kmeans = None
        self.spatial_features = None

    def fit(self, X, geometry=None):
        """
        Fit spatial K-Means.

        Args:
            X: Feature matrix
            geometry: Geometry column

        Returns:
            self
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("Scikit-learn required for clustering")

        # Prepare features
        features = X.copy()

        if geometry is not None and GEOPANDAS_AVAILABLE:
            # Extract spatial coordinates
            coords = np.array([[geom.centroid.x, geom.centroid.y] for geom in geometry])
            spatial_df = pd.DataFrame(
                coords, columns=["spatial_x", "spatial_y"], index=X.index
            )

            # Normalize spatial features
            spatial_scaler = StandardScaler()
            spatial_normalized = spatial_scaler.fit_transform(spatial_df)
            spatial_df_norm = pd.DataFrame(
                spatial_normalized, columns=["spatial_x", "spatial_y"], index=X.index
            )

            # Combine features with spatial weight
            if len(features.columns) > 0:
                feature_scaler = StandardScaler()
                features_normalized = feature_scaler.fit_transform(features)
                features_df_norm = pd.DataFrame(
                    features_normalized, columns=features.columns, index=X.index
                )

                # Weight and combine
                weighted_features = features_df_norm * (1 - self.spatial_weight)
                weighted_spatial = spatial_df_norm * self.spatial_weight

                combined_features = pd.concat(
                    [weighted_features, weighted_spatial], axis=1
                )
            else:
                combined_features = spatial_df_norm

            self.spatial_features = spatial_df
        else:
            combined_features = features

        # Fit K-Means
        self.kmeans = KMeans(n_clusters=self.n_clusters, **self.kwargs)
        self.kmeans.fit(combined_features)

        return self

    def predict(self, X, geometry=None):
        """
        Predict cluster labels.

        Args:
            X: Feature matrix
            geometry: Geometry column

        Returns:
            Cluster labels
        """
        if self.kmeans is None:
            raise ValueError("Model not fitted yet")

        # Prepare features (similar to fit)
        features = X.copy()

        if geometry is not None and GEOPANDAS_AVAILABLE:
            coords = np.array([[geom.centroid.x, geom.centroid.y] for geom in geometry])
            spatial_df = pd.DataFrame(
                coords, columns=["spatial_x", "spatial_y"], index=X.index
            )

            # Use same normalization as training
            if self.spatial_features is not None:
                spatial_scaler = StandardScaler()
                spatial_scaler.fit(self.spatial_features)
                spatial_normalized = spatial_scaler.transform(spatial_df)
                spatial_df_norm = pd.DataFrame(
                    spatial_normalized,
                    columns=["spatial_x", "spatial_y"],
                    index=X.index,
                )

                if len(features.columns) > 0:
                    feature_scaler = StandardScaler()
                    features_normalized = feature_scaler.fit_transform(features)
                    features_df_norm = pd.DataFrame(
                        features_normalized, columns=features.columns, index=X.index
                    )

                    weighted_features = features_df_norm * (1 - self.spatial_weight)
                    weighted_spatial = spatial_df_norm * self.spatial_weight

                    combined_features = pd.concat(
                        [weighted_features, weighted_spatial], axis=1
                    )
                else:
                    combined_features = spatial_df_norm
            else:
                combined_features = spatial_df
        else:
            combined_features = features

        return self.kmeans.predict(combined_features)

    @property
    def labels_(self):
        """Get cluster labels."""
        return self.kmeans.labels_ if self.kmeans else None


class SpatialDBSCAN(BaseEstimator, ClusterMixin):
    """Spatial-aware DBSCAN clustering."""

    def __init__(
        self,
        eps: float = 0.5,
        min_samples: int = 5,
        spatial_weight: float = 0.5,
        **kwargs
    ):
        """
        Initialize spatial DBSCAN.

        Args:
            eps: Maximum distance between samples
            min_samples: Minimum samples in neighborhood
            spatial_weight: Weight for spatial features
            **kwargs: Additional DBSCAN parameters
        """
        self.eps = eps
        self.min_samples = min_samples
        self.spatial_weight = spatial_weight
        self.kwargs = kwargs
        self.dbscan = None

    def fit(self, X, geometry=None):
        """
        Fit spatial DBSCAN.

        Args:
            X: Feature matrix
            geometry: Geometry column

        Returns:
            self
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("Scikit-learn required for clustering")

        # Prepare features (similar to SpatialKMeans)
        features = X.copy()

        if geometry is not None and GEOPANDAS_AVAILABLE:
            coords = np.array([[geom.centroid.x, geom.centroid.y] for geom in geometry])
            spatial_df = pd.DataFrame(
                coords, columns=["spatial_x", "spatial_y"], index=X.index
            )

            # Combine with weights
            if len(features.columns) > 0:
                combined_features = pd.concat(
                    [
                        features * (1 - self.spatial_weight),
                        spatial_df * self.spatial_weight,
                    ],
                    axis=1,
                )
            else:
                combined_features = spatial_df
        else:
            combined_features = features

        # Fit DBSCAN
        self.dbscan = DBSCAN(eps=self.eps, min_samples=self.min_samples, **self.kwargs)
        self.dbscan.fit(combined_features)

        return self

    @property
    def labels_(self):
        """Get cluster labels."""
        return self.dbscan.labels_ if self.dbscan else None


class SpatialRegression(BaseEstimator, RegressorMixin):
    """Spatial-aware regression model."""

    def __init__(self, base_estimator=None, include_spatial_lag: bool = True):
        """
        Initialize spatial regression.

        Args:
            base_estimator: Base regression model
            include_spatial_lag: Whether to include spatial lag features
        """
        self.base_estimator = base_estimator or (
            RandomForestRegressor() if SKLEARN_AVAILABLE else None
        )
        self.include_spatial_lag = include_spatial_lag
        self.spatial_weights = None

    def fit(self, X, y, geometry=None):
        """
        Fit spatial regression model.

        Args:
            X: Feature matrix
            y: Target variable
            geometry: Geometry column

        Returns:
            self
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("Scikit-learn required for regression")

        features = X.copy()

        if self.include_spatial_lag and geometry is not None:
            # Calculate spatial lag of target variable
            try:
                from libpysal.weights import Queen

                if GEOPANDAS_AVAILABLE:
                    temp_gdf = gpd.GeoDataFrame(X, geometry=geometry)
                    w = Queen.from_dataframe(temp_gdf)
                    w.transform = "r"
                    spatial_lag = w.sparse.dot(y)
                    features["spatial_lag_y"] = spatial_lag
                    self.spatial_weights = w
            except ImportError:
                logger.warning("PySAL not available - spatial lag not calculated")

        self.base_estimator.fit(features, y)
        return self

    def predict(self, X, geometry=None):
        """
        Make predictions.

        Args:
            X: Feature matrix
            geometry: Geometry column

        Returns:
            Predictions
        """
        features = X.copy()

        if self.include_spatial_lag and self.spatial_weights is not None:
            # For prediction, we need to estimate spatial lag
            # This is simplified - in practice, you'd use iterative methods
            features["spatial_lag_y"] = 0  # Placeholder

        return self.base_estimator.predict(features)


class SpatialClassifier(BaseEstimator, ClassifierMixin):
    """Spatial-aware classification model."""

    def __init__(self, base_estimator=None, include_spatial_features: bool = True):
        """
        Initialize spatial classifier.

        Args:
            base_estimator: Base classification model
            include_spatial_features: Whether to include spatial features
        """
        self.base_estimator = base_estimator or (
            RandomForestClassifier() if SKLEARN_AVAILABLE else None
        )
        self.include_spatial_features = include_spatial_features
        self.feature_extractor = None

    def fit(self, X, y, geometry=None):
        """
        Fit spatial classification model.

        Args:
            X: Feature matrix
            y: Target variable
            geometry: Geometry column

        Returns:
            self
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("Scikit-learn required for classification")

        features = X.copy()

        if self.include_spatial_features and geometry is not None:
            # Extract spatial features
            from .features import SpatialFeatureExtractor

            self.feature_extractor = SpatialFeatureExtractor()

            if GEOPANDAS_AVAILABLE:
                temp_gdf = gpd.GeoDataFrame(X, geometry=geometry)
                spatial_features = self.feature_extractor.extract_all_features(temp_gdf)
                features = pd.concat([features, spatial_features], axis=1)

        self.base_estimator.fit(features, y)
        return self

    def predict(self, X, geometry=None):
        """
        Make predictions.

        Args:
            X: Feature matrix
            geometry: Geometry column

        Returns:
            Predictions
        """
        features = X.copy()

        if (
            self.include_spatial_features
            and self.feature_extractor
            and geometry is not None
        ):
            if GEOPANDAS_AVAILABLE:
                temp_gdf = gpd.GeoDataFrame(X, geometry=geometry)
                spatial_features = self.feature_extractor.extract_all_features(temp_gdf)
                features = pd.concat([features, spatial_features], axis=1)

        return self.base_estimator.predict(features)

    def predict_proba(self, X, geometry=None):
        """
        Predict class probabilities.

        Args:
            X: Feature matrix
            geometry: Geometry column

        Returns:
            Class probabilities
        """
        features = X.copy()

        if (
            self.include_spatial_features
            and self.feature_extractor
            and geometry is not None
        ):
            if GEOPANDAS_AVAILABLE:
                temp_gdf = gpd.GeoDataFrame(X, geometry=geometry)
                spatial_features = self.feature_extractor.extract_all_features(temp_gdf)
                features = pd.concat([features, spatial_features], axis=1)

        return self.base_estimator.predict_proba(features)


# Convenience functions
def spatial_train_test_split(
    X,
    y,
    geometry,
    test_size: float = 0.2,
    spatial_buffer: float = 1000,
    random_state: int = None,
):
    """
    Spatial-aware train-test split.

    Args:
        X: Feature matrix
        y: Target variable
        geometry: Geometry column
        test_size: Proportion of test set
        spatial_buffer: Buffer distance for spatial separation
        random_state: Random state for reproducibility

    Returns:
        X_train, X_test, y_train, y_test, geom_train, geom_test
    """
    if not SKLEARN_AVAILABLE:
        raise ImportError("Scikit-learn required for train-test split")

    # Simple random split for now - could be enhanced with spatial blocking
    indices = np.arange(len(X))
    train_idx, test_idx = train_test_split(
        indices, test_size=test_size, random_state=random_state
    )

    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]
    y_train = y.iloc[train_idx]
    y_test = y.iloc[test_idx]
    geom_train = geometry.iloc[train_idx]
    geom_test = geometry.iloc[test_idx]

    return X_train, X_test, y_train, y_test, geom_train, geom_test


def spatial_cross_validate(
    estimator, X, y, geometry, cv: int = 5, scoring: str = "accuracy"
):
    """
    Spatial-aware cross-validation.

    Args:
        estimator: ML estimator
        X: Feature matrix
        y: Target variable
        geometry: Geometry column
        cv: Number of CV folds
        scoring: Scoring metric

    Returns:
        Cross-validation scores
    """
    if not SKLEARN_AVAILABLE:
        raise ImportError("Scikit-learn required for cross-validation")

    # Simple K-fold for now - could be enhanced with spatial blocking
    kfold = KFold(n_splits=cv, shuffle=True, random_state=42)
    scores = []

    for train_idx, test_idx in kfold.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        geom_train, geom_test = geometry.iloc[train_idx], geometry.iloc[test_idx]

        # Fit and predict
        if (
            hasattr(estimator, "fit")
            and "geometry" in estimator.fit.__code__.co_varnames
        ):
            estimator.fit(X_train, y_train, geometry=geom_train)
        else:
            estimator.fit(X_train, y_train)

        if (
            hasattr(estimator, "predict")
            and "geometry" in estimator.predict.__code__.co_varnames
        ):
            y_pred = estimator.predict(X_test, geometry=geom_test)
        else:
            y_pred = estimator.predict(X_test)

        # Calculate score
        if scoring == "accuracy":
            score = accuracy_score(y_test, y_pred)
        elif scoring == "r2":
            score = r2_score(y_test, y_pred)
        else:
            score = 0  # Default

        scores.append(score)

    return np.array(scores)
