"""
Test suite for PyMapGIS ML/Analytics Integration features.

Tests spatial feature engineering, scikit-learn integration,
spatial algorithms, and ML pipelines.
"""

import pytest
import numpy as np
import pandas as pd
import tempfile
import shutil
from pathlib import Path

# Import PyMapGIS ML components
try:
    from pymapgis.ml import (
        SpatialFeatureExtractor,
        SpatialPreprocessor,
        SpatialKMeans,
        SpatialRegression,
        SpatialClassifier,
        Kriging,
        GeographicallyWeightedRegression,
        SpatialAutocorrelation,
        HotspotAnalysis,
        extract_geometric_features,
        calculate_spatial_statistics,
        analyze_neighborhoods,
        spatial_train_test_split,
        spatial_cross_validate,
        perform_kriging,
        calculate_gwr,
        analyze_spatial_autocorrelation,
        detect_hotspots,
        evaluate_spatial_model,
        spatial_accuracy_score,
        spatial_r2_score,
        prepare_spatial_data,
        scale_spatial_features,
        encode_spatial_categories,
        create_spatial_pipeline,
        auto_spatial_analysis,
        analyze_spatial_data,
        create_spatial_ml_model,
        run_spatial_analysis_pipeline,
    )

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# Optional imports for testing
try:
    import geopandas as gpd
    from shapely.geometry import Point, Polygon

    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False

try:
    from sklearn.datasets import make_classification, make_regression

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


@pytest.fixture
def sample_spatial_data():
    """Create sample spatial data for testing."""
    if not GEOPANDAS_AVAILABLE:
        pytest.skip("GeoPandas not available")

    # Generate sample points
    np.random.seed(42)
    n_points = 50

    x = np.random.uniform(0, 10, n_points)
    y = np.random.uniform(0, 10, n_points)

    # Create features
    feature1 = np.random.normal(100, 20, n_points)
    feature2 = np.random.exponential(5, n_points)
    target = feature1 * 0.5 + feature2 * 2 + np.random.normal(0, 10, n_points)

    # Create GeoDataFrame
    geometry = [Point(xi, yi) for xi, yi in zip(x, y)]

    gdf = gpd.GeoDataFrame(
        {
            "feature1": feature1,
            "feature2": feature2,
            "target": target,
            "geometry": geometry,
        }
    )

    return gdf


@pytest.fixture
def sample_tabular_data():
    """Create sample tabular data for testing."""
    np.random.seed(42)
    n_samples = 100

    data = {
        "feature1": np.random.normal(0, 1, n_samples),
        "feature2": np.random.normal(0, 1, n_samples),
        "feature3": np.random.uniform(0, 10, n_samples),
        "target": np.random.normal(50, 15, n_samples),
    }

    return pd.DataFrame(data)


@pytest.mark.skipif(not ML_AVAILABLE, reason="ML module not available")
class TestSpatialFeatureExtraction:
    """Test spatial feature extraction functionality."""

    def test_spatial_feature_extractor_creation(self):
        """Test spatial feature extractor creation."""
        extractor = SpatialFeatureExtractor()
        assert extractor is not None
        assert extractor.buffer_distances == [100, 500, 1000]
        assert extractor.spatial_weights == "queen"

    def test_geometric_features_extraction(self, sample_spatial_data):
        """Test geometric feature extraction."""
        if not GEOPANDAS_AVAILABLE:
            pytest.skip("GeoPandas not available")

        try:
            geometric_features = extract_geometric_features(sample_spatial_data)
            assert isinstance(geometric_features, pd.DataFrame)
            assert len(geometric_features) == len(sample_spatial_data)

            # Check for expected geometric features
            expected_features = ["area", "perimeter", "centroid_x", "centroid_y"]
            for feature in expected_features:
                assert feature in geometric_features.columns

        except ImportError:
            pytest.skip("Required dependencies not available")

    def test_spatial_statistics_calculation(self, sample_spatial_data):
        """Test spatial statistics calculation."""
        if not GEOPANDAS_AVAILABLE:
            pytest.skip("GeoPandas not available")

        try:
            spatial_stats = calculate_spatial_statistics(
                sample_spatial_data, sample_spatial_data["target"]
            )
            assert spatial_stats is not None

            # Check if statistics were calculated (may be None if PySAL not available)
            assert hasattr(spatial_stats, "moran_i")
            assert hasattr(spatial_stats, "neighbor_count")

        except ImportError:
            pytest.skip("Required dependencies not available")

    def test_neighborhood_analysis(self, sample_spatial_data):
        """Test neighborhood analysis."""
        if not GEOPANDAS_AVAILABLE:
            pytest.skip("GeoPandas not available")

        try:
            neighborhood_features = analyze_neighborhoods(sample_spatial_data, "target")
            assert isinstance(neighborhood_features, pd.DataFrame)
            assert len(neighborhood_features) == len(sample_spatial_data)

        except ImportError:
            pytest.skip("Required dependencies not available")


@pytest.mark.skipif(not ML_AVAILABLE, reason="ML module not available")
class TestSpatialMLModels:
    """Test spatial ML models functionality."""

    def test_spatial_preprocessor(self, sample_spatial_data):
        """Test spatial preprocessor."""
        if not GEOPANDAS_AVAILABLE:
            pytest.skip("GeoPandas not available")

        try:
            preprocessor = SpatialPreprocessor()

            X = sample_spatial_data.drop(columns=["target", "geometry"])
            y = sample_spatial_data["target"]
            geometry = sample_spatial_data.geometry

            preprocessor.fit(X, y, geometry=geometry)
            X_transformed = preprocessor.transform(X, geometry=geometry)

            assert isinstance(X_transformed, pd.DataFrame)
            assert len(X_transformed) == len(X)

        except ImportError:
            pytest.skip("Required dependencies not available")

    def test_spatial_kmeans(self, sample_spatial_data):
        """Test spatial K-means clustering."""
        if not GEOPANDAS_AVAILABLE:
            pytest.skip("GeoPandas not available")

        try:
            kmeans = SpatialKMeans(n_clusters=3)

            X = sample_spatial_data.drop(columns=["target", "geometry"])
            geometry = sample_spatial_data.geometry

            kmeans.fit(X, geometry=geometry)
            labels = kmeans.predict(X, geometry=geometry)

            assert labels is not None
            assert len(labels) == len(X)
            assert len(np.unique(labels)) <= 3

        except ImportError:
            pytest.skip("Required dependencies not available")

    def test_spatial_regression(self, sample_spatial_data):
        """Test spatial regression."""
        if not GEOPANDAS_AVAILABLE:
            pytest.skip("GeoPandas not available")

        try:
            regression = SpatialRegression()

            X = sample_spatial_data.drop(columns=["target", "geometry"])
            y = sample_spatial_data["target"]
            geometry = sample_spatial_data.geometry

            regression.fit(X, y, geometry=geometry)
            predictions = regression.predict(X, geometry=geometry)

            assert predictions is not None
            assert len(predictions) == len(y)

        except ImportError:
            pytest.skip("Required dependencies not available")

    def test_spatial_classifier(self, sample_spatial_data):
        """Test spatial classifier."""
        if not GEOPANDAS_AVAILABLE:
            pytest.skip("GeoPandas not available")

        try:
            classifier = SpatialClassifier()

            X = sample_spatial_data.drop(columns=["target", "geometry"])
            # Create binary target
            y = (
                sample_spatial_data["target"] > sample_spatial_data["target"].median()
            ).astype(int)
            geometry = sample_spatial_data.geometry

            classifier.fit(X, y, geometry=geometry)
            predictions = classifier.predict(X, geometry=geometry)

            assert predictions is not None
            assert len(predictions) == len(y)
            assert set(predictions).issubset({0, 1})

        except ImportError:
            pytest.skip("Required dependencies not available")


@pytest.mark.skipif(not ML_AVAILABLE, reason="ML module not available")
class TestSpatialAlgorithms:
    """Test specialized spatial algorithms."""

    def test_kriging(self, sample_spatial_data):
        """Test kriging interpolation."""
        if not GEOPANDAS_AVAILABLE:
            pytest.skip("GeoPandas not available")

        try:
            kriging = Kriging()

            X = sample_spatial_data.drop(columns=["target", "geometry"])
            y = sample_spatial_data["target"]
            geometry = sample_spatial_data.geometry

            kriging.fit(X, y, geometry=geometry)
            predictions = kriging.predict(X, geometry=geometry)

            assert predictions is not None
            assert len(predictions) == len(y)

        except ImportError:
            pytest.skip("Required dependencies not available")

    def test_gwr(self, sample_spatial_data):
        """Test Geographically Weighted Regression."""
        if not GEOPANDAS_AVAILABLE:
            pytest.skip("GeoPandas not available")

        try:
            gwr = GeographicallyWeightedRegression()

            X = sample_spatial_data.drop(columns=["target", "geometry"])
            y = sample_spatial_data["target"]
            geometry = sample_spatial_data.geometry

            gwr.fit(X, y, geometry=geometry)
            predictions = gwr.predict(X, geometry=geometry)

            assert predictions is not None
            assert len(predictions) == len(y)

        except ImportError:
            pytest.skip("Required dependencies not available")

    def test_spatial_autocorrelation(self, sample_spatial_data):
        """Test spatial autocorrelation analysis."""
        if not GEOPANDAS_AVAILABLE:
            pytest.skip("GeoPandas not available")

        try:
            autocorr_results = analyze_spatial_autocorrelation(
                sample_spatial_data, "target"
            )
            assert autocorr_results is not None
            assert hasattr(autocorr_results, "global_moran_i")
            assert hasattr(autocorr_results, "local_moran_i")

        except ImportError:
            pytest.skip("Required dependencies not available")

    def test_hotspot_analysis(self, sample_spatial_data):
        """Test hotspot analysis."""
        if not GEOPANDAS_AVAILABLE:
            pytest.skip("GeoPandas not available")

        try:
            hotspot_results = detect_hotspots(sample_spatial_data, "target")
            assert hotspot_results is not None
            assert hasattr(hotspot_results, "hotspot_classification")
            assert hasattr(hotspot_results, "z_scores")

        except ImportError:
            pytest.skip("Required dependencies not available")


@pytest.mark.skipif(not ML_AVAILABLE, reason="ML module not available")
class TestSpatialPipelines:
    """Test spatial ML pipelines."""

    def test_create_spatial_pipeline(self):
        """Test spatial pipeline creation."""
        try:
            pipeline = create_spatial_pipeline(model_type="regression")
            assert pipeline is not None

        except ImportError:
            pytest.skip("Required dependencies not available")

    def test_spatial_data_preparation(self, sample_spatial_data):
        """Test spatial data preparation."""
        if not GEOPANDAS_AVAILABLE:
            pytest.skip("GeoPandas not available")

        try:
            X, y, geometry = prepare_spatial_data(sample_spatial_data, "target")

            assert isinstance(X, pd.DataFrame)
            assert isinstance(y, pd.Series)
            assert len(X) == len(y)
            assert "target" not in X.columns
            assert "geometry" not in X.columns

        except ImportError:
            pytest.skip("Required dependencies not available")

    def test_spatial_feature_scaling(self, sample_tabular_data):
        """Test spatial feature scaling."""
        try:
            X_scaled = scale_spatial_features(
                sample_tabular_data.drop(columns=["target"])
            )
            assert X_scaled is not None
            assert X_scaled.shape == (len(sample_tabular_data), 3)

        except ImportError:
            pytest.skip("Required dependencies not available")

    def test_analyze_spatial_data(self, sample_spatial_data):
        """Test comprehensive spatial data analysis."""
        if not GEOPANDAS_AVAILABLE:
            pytest.skip("GeoPandas not available")

        try:
            results = analyze_spatial_data(sample_spatial_data, "target")
            assert isinstance(results, dict)

        except ImportError:
            pytest.skip("Required dependencies not available")


@pytest.mark.skipif(not ML_AVAILABLE, reason="ML module not available")
class TestModelEvaluation:
    """Test spatial model evaluation."""

    def test_spatial_accuracy_score(self):
        """Test spatial accuracy score."""
        y_true = np.array([0, 1, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 0, 1])

        try:
            score = spatial_accuracy_score(y_true, y_pred)
            assert isinstance(score, float)
            assert 0 <= score <= 1

        except ImportError:
            pytest.skip("Required dependencies not available")

    def test_spatial_r2_score(self):
        """Test spatial R² score."""
        y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y_pred = np.array([1.1, 2.1, 2.9, 3.8, 5.2])

        try:
            score = spatial_r2_score(y_true, y_pred)
            assert isinstance(score, float)

        except ImportError:
            pytest.skip("Required dependencies not available")

    def test_evaluate_spatial_model(self, sample_spatial_data):
        """Test spatial model evaluation."""
        if not GEOPANDAS_AVAILABLE:
            pytest.skip("GeoPandas not available")

        try:
            model = create_spatial_ml_model("regression")
            if model is None:
                pytest.skip("Could not create spatial model")

            X = sample_spatial_data.drop(columns=["target", "geometry"])
            y = sample_spatial_data["target"]
            geometry = sample_spatial_data.geometry

            scores = evaluate_spatial_model(model, X, y, geometry, cv=3)
            assert isinstance(scores, np.ndarray)
            assert len(scores) == 3

        except ImportError:
            pytest.skip("Required dependencies not available")


@pytest.mark.skipif(not ML_AVAILABLE, reason="ML module not available")
class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_create_spatial_ml_model(self):
        """Test spatial ML model creation."""
        try:
            # Test different model types
            reg_model = create_spatial_ml_model("regression")
            assert reg_model is not None

            clf_model = create_spatial_ml_model("classification")
            assert clf_model is not None

            cluster_model = create_spatial_ml_model("clustering")
            assert cluster_model is not None

        except ImportError:
            pytest.skip("Required dependencies not available")

    def test_auto_spatial_analysis(self, sample_spatial_data):
        """Test automated spatial analysis."""
        if not GEOPANDAS_AVAILABLE:
            pytest.skip("GeoPandas not available")

        try:
            results = auto_spatial_analysis(sample_spatial_data, "target")
            assert isinstance(results, dict)

        except ImportError:
            pytest.skip("Required dependencies not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
