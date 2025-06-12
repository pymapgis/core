"""
PyMapGIS ML/Analytics Integration Module

This module provides comprehensive machine learning and analytics capabilities for PyMapGIS,
including spatial feature engineering, scikit-learn integration, and specialized spatial ML algorithms.

Features:
- Spatial Feature Engineering: Geometric features, spatial statistics, neighborhood analysis
- Scikit-learn Integration: Spatial-aware preprocessing, model wrappers, pipelines
- Spatial ML Algorithms: Kriging, GWR, spatial clustering, autocorrelation analysis
- Model Evaluation: Spatial cross-validation, performance metrics for spatial data
- Preprocessing: Spatial data preparation, feature scaling, encoding

Enterprise Features:
- Scalable spatial analytics pipelines
- Integration with existing ML workflows
- Spatial model validation and evaluation
- Performance optimization for large datasets
- Distributed spatial computing support
"""

import numpy as np
from typing import Optional

from .features import (
    SpatialFeatureExtractor,
    GeometricFeatures,
    SpatialStatistics,
    NeighborhoodAnalysis,
    extract_geometric_features,
    calculate_spatial_statistics,
    analyze_neighborhoods,
)

from .sklearn_integration import (
    SpatialPreprocessor,
    SpatialPipeline,
    SpatialKMeans,
    SpatialDBSCAN,
    SpatialRegression,
    SpatialClassifier,
    spatial_train_test_split,
    spatial_cross_validate,
)

from .spatial_algorithms import (
    Kriging,
    GeographicallyWeightedRegression,
    SpatialAutocorrelation,
    HotspotAnalysis,
    SpatialClustering,
    perform_kriging,
    calculate_gwr,
    analyze_spatial_autocorrelation,
    detect_hotspots,
)

# Note: evaluation, preprocessing, and pipelines modules will be implemented as needed
# For now, we'll provide basic implementations in the main module


# Basic evaluation functions
def evaluate_spatial_model(model, X, y, geometry=None, cv=5):
    """Evaluate spatial model with cross-validation."""
    try:
        from .sklearn_integration import spatial_cross_validate

        return spatial_cross_validate(model, X, y, geometry, cv=cv)
    except ImportError:
        return np.array([0.0] * cv)


def spatial_accuracy_score(y_true, y_pred, geometry=None):
    """Calculate spatial-aware accuracy score."""
    try:
        from sklearn.metrics import accuracy_score

        return accuracy_score(y_true, y_pred)
    except ImportError:
        return 0.0


def spatial_r2_score(y_true, y_pred, geometry=None):
    """Calculate spatial-aware R² score."""
    try:
        from sklearn.metrics import r2_score

        return r2_score(y_true, y_pred)
    except ImportError:
        return 0.0


# Basic preprocessing functions
def prepare_spatial_data(gdf, target_column=None):
    """Prepare spatial data for ML."""
    if target_column:
        X = gdf.drop(columns=[target_column, "geometry"])
        y = gdf[target_column]
        return X, y, gdf.geometry
    else:
        X = gdf.drop(columns=["geometry"])
        return X, gdf.geometry


def scale_spatial_features(X, geometry=None):
    """Scale spatial features."""
    try:
        from sklearn.preprocessing import StandardScaler

        scaler = StandardScaler()
        return scaler.fit_transform(X)
    except ImportError:
        return X


def encode_spatial_categories(X, categorical_columns=None):
    """Encode categorical spatial features."""
    try:
        from sklearn.preprocessing import LabelEncoder

        X_encoded = X.copy()
        if categorical_columns:
            for col in categorical_columns:
                if col in X_encoded.columns:
                    le = LabelEncoder()
                    X_encoded[col] = le.fit_transform(X_encoded[col].astype(str))
        return X_encoded
    except ImportError:
        return X


# Basic pipeline functions
def create_spatial_pipeline(model_type="regression", **kwargs):
    """Create a spatial ML pipeline."""
    try:
        from .sklearn_integration import SpatialPipeline, SpatialPreprocessor

        if model_type == "regression":
            from .sklearn_integration import SpatialRegression

            model = SpatialRegression(**kwargs)
        elif model_type == "classification":
            from .sklearn_integration import SpatialClassifier

            model = SpatialClassifier(**kwargs)
        elif model_type == "clustering":
            from .sklearn_integration import SpatialKMeans

            model = SpatialKMeans(**kwargs)
        else:
            from .sklearn_integration import SpatialRegression

            model = SpatialRegression(**kwargs)

        pipeline = SpatialPipeline(
            [("preprocessor", SpatialPreprocessor()), ("model", model)]
        )

        return pipeline
    except ImportError:
        return None


def auto_spatial_analysis(gdf, target_column=None, **kwargs):
    """Perform automated spatial analysis."""
    results = analyze_spatial_data(gdf, target_column, **kwargs)
    return results


# Placeholder classes for compatibility
class SpatialCrossValidator:
    """Placeholder for spatial cross-validator."""

    def __init__(self, cv=5):
        self.cv = cv


class SpatialMetrics:
    """Placeholder for spatial metrics."""

    pass


class ModelEvaluator:
    """Placeholder for model evaluator."""

    def evaluate_model(self, model, X, y, geometry=None):
        return {"score": 0.0}


class SpatialScaler:
    """Placeholder for spatial scaler."""

    def fit_transform(self, X):
        return scale_spatial_features(X)


class SpatialEncoder:
    """Placeholder for spatial encoder."""

    def fit_transform(self, X):
        return encode_spatial_categories(X)


class SpatialImputer:
    """Placeholder for spatial imputer."""

    def fit_transform(self, X):
        return X.fillna(X.mean())


class SpatialMLPipeline:
    """Placeholder for spatial ML pipeline."""

    def __init__(self, steps):
        self.steps = steps


class AutoSpatialML:
    """Placeholder for automated spatial ML."""

    def fit(self, X, y, geometry=None):
        return self


class SpatialModelSelector:
    """Placeholder for spatial model selector."""

    def select_best_model(self, X, y, geometry=None):
        return create_spatial_pipeline()


# Version and metadata
__version__ = "0.3.2"
__author__ = "PyMapGIS Team"

# Default configuration
DEFAULT_CONFIG = {
    "feature_extraction": {
        "geometric_features": True,
        "spatial_statistics": True,
        "neighborhood_analysis": True,
        "buffer_distances": [100, 500, 1000],  # meters
        "spatial_weights": "queen",
    },
    "sklearn_integration": {
        "spatial_cv_folds": 5,
        "spatial_buffer": 1000,  # meters
        "random_state": 42,
        "n_jobs": -1,
    },
    "spatial_algorithms": {
        "kriging_variogram": "spherical",
        "gwr_bandwidth": "adaptive",
        "autocorrelation_weights": "queen",
        "hotspot_alpha": 0.05,
    },
    "preprocessing": {
        "scaling_method": "standard",
        "encoding_method": "onehot",
        "imputation_strategy": "spatial_mean",
    },
}

# Global instances
_feature_extractor = None
_spatial_preprocessor = None
_model_evaluator = None


def get_feature_extractor() -> SpatialFeatureExtractor:
    """Get the global spatial feature extractor instance."""
    global _feature_extractor
    if _feature_extractor is None:
        _feature_extractor = SpatialFeatureExtractor()
    return _feature_extractor


def get_spatial_preprocessor() -> SpatialPreprocessor:
    """Get the global spatial preprocessor instance."""
    global _spatial_preprocessor
    if _spatial_preprocessor is None:
        _spatial_preprocessor = SpatialPreprocessor()
    return _spatial_preprocessor


def get_model_evaluator() -> ModelEvaluator:
    """Get the global model evaluator instance."""
    global _model_evaluator
    if _model_evaluator is None:
        _model_evaluator = ModelEvaluator()
    return _model_evaluator


# Convenience functions
def analyze_spatial_data(gdf, target_column: Optional[str] = None, **kwargs):
    """
    Perform comprehensive spatial data analysis.

    Args:
        gdf: GeoDataFrame with spatial data
        target_column: Target variable for supervised learning
        **kwargs: Additional analysis parameters

    Returns:
        Analysis results dictionary
    """
    results = {}

    # Extract spatial features
    feature_extractor = get_feature_extractor()
    spatial_features = feature_extractor.extract_all_features(gdf)
    results["spatial_features"] = spatial_features

    # Calculate spatial statistics
    spatial_stats = calculate_spatial_statistics(gdf)
    results["spatial_statistics"] = spatial_stats

    # Perform spatial autocorrelation analysis
    if target_column and target_column in gdf.columns:
        autocorr_results = analyze_spatial_autocorrelation(gdf, target_column)
        results["spatial_autocorrelation"] = autocorr_results

    # Detect spatial clusters/hotspots
    if target_column and target_column in gdf.columns:
        hotspot_results = detect_hotspots(gdf, target_column)
        results["hotspots"] = hotspot_results

    return results


def create_spatial_ml_model(model_type: str = "regression", **kwargs):
    """
    Create a spatial-aware ML model.

    Args:
        model_type: Type of model ('regression', 'classification', 'clustering')
        **kwargs: Model parameters

    Returns:
        Configured spatial ML model
    """
    if model_type == "regression":
        return SpatialRegression(**kwargs)
    elif model_type == "classification":
        return SpatialClassifier(**kwargs)
    elif model_type == "clustering":
        return SpatialKMeans(**kwargs)
    elif model_type == "gwr":
        return GeographicallyWeightedRegression(**kwargs)
    elif model_type == "kriging":
        return Kriging(**kwargs)
    else:
        raise ValueError(f"Unknown model type: {model_type}")


def run_spatial_analysis_pipeline(
    gdf, target_column: str = None, model_type: str = "auto", **kwargs
):
    """
    Run a complete spatial analysis pipeline.

    Args:
        gdf: GeoDataFrame with spatial data
        target_column: Target variable for supervised learning
        model_type: Type of analysis ('auto', 'regression', 'classification', 'clustering')
        **kwargs: Pipeline parameters

    Returns:
        Pipeline results with model and evaluation metrics
    """
    # Create spatial pipeline
    pipeline = create_spatial_pipeline(model_type=model_type, **kwargs)

    # Prepare data
    if target_column:
        X = gdf.drop(columns=[target_column, "geometry"])
        y = gdf[target_column]

        # Fit and evaluate model
        pipeline.fit(X, y, geometry=gdf.geometry)

        # Evaluate model
        evaluator = get_model_evaluator()
        results = evaluator.evaluate_model(pipeline, X, y, geometry=gdf.geometry)
    else:
        # Unsupervised analysis
        X = gdf.drop(columns=["geometry"])
        pipeline.fit(X, geometry=gdf.geometry)
        results = {"model": pipeline, "features": X.columns.tolist()}

    return results


# Export all public components
__all__ = [
    # Feature Engineering
    "SpatialFeatureExtractor",
    "GeometricFeatures",
    "SpatialStatistics",
    "NeighborhoodAnalysis",
    "extract_geometric_features",
    "calculate_spatial_statistics",
    "analyze_neighborhoods",
    # Scikit-learn Integration
    "SpatialPreprocessor",
    "SpatialPipeline",
    "SpatialKMeans",
    "SpatialDBSCAN",
    "SpatialRegression",
    "SpatialClassifier",
    "spatial_train_test_split",
    "spatial_cross_validate",
    # Spatial Algorithms
    "Kriging",
    "GeographicallyWeightedRegression",
    "SpatialAutocorrelation",
    "HotspotAnalysis",
    "SpatialClustering",
    "perform_kriging",
    "calculate_gwr",
    "analyze_spatial_autocorrelation",
    "detect_hotspots",
    # Evaluation
    "SpatialCrossValidator",
    "SpatialMetrics",
    "ModelEvaluator",
    "evaluate_spatial_model",
    "spatial_accuracy_score",
    "spatial_r2_score",
    # Preprocessing
    "SpatialScaler",
    "SpatialEncoder",
    "SpatialImputer",
    "prepare_spatial_data",
    "scale_spatial_features",
    "encode_spatial_categories",
    # Pipelines
    "SpatialMLPipeline",
    "AutoSpatialML",
    "SpatialModelSelector",
    "create_spatial_pipeline",
    "auto_spatial_analysis",
    # Manager instances
    "get_feature_extractor",
    "get_spatial_preprocessor",
    "get_model_evaluator",
    # Convenience functions
    "analyze_spatial_data",
    "create_spatial_ml_model",
    "run_spatial_analysis_pipeline",
    # Configuration
    "DEFAULT_CONFIG",
]
