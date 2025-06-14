#!/usr/bin/env python3
"""
PyMapGIS ML/Analytics Integration Demo

Demonstrates the comprehensive machine learning and analytics capabilities
including spatial feature engineering, scikit-learn integration, and specialized spatial ML algorithms.
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Add PyMapGIS to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pymapgis as pmg


def create_sample_spatial_data():
    """Create sample spatial data for demonstration."""
    print("📊 Creating sample spatial dataset...")

    try:
        import geopandas as gpd
        from shapely.geometry import Point

        # Generate random spatial data
        np.random.seed(42)
        n_points = 100

        # Create random coordinates
        x = np.random.uniform(-10, 10, n_points)
        y = np.random.uniform(-10, 10, n_points)

        # Create spatial pattern with some clustering
        cluster_centers = [(-5, -5), (5, 5), (0, 0)]
        cluster_data = []

        for i, (cx, cy) in enumerate(cluster_centers):
            n_cluster = n_points // 3
            if i == len(cluster_centers) - 1:
                n_cluster = n_points - len(cluster_data)

            cluster_x = np.random.normal(cx, 2, n_cluster)
            cluster_y = np.random.normal(cy, 2, n_cluster)
            cluster_data.extend(list(zip(cluster_x, cluster_y)))

        # Create features with spatial correlation
        coords = np.array(cluster_data)
        x_coords = coords[:, 0]
        y_coords = coords[:, 1]

        # Feature 1: Distance from origin
        distance_from_origin = np.sqrt(x_coords**2 + y_coords**2)

        # Feature 2: Elevation (correlated with y-coordinate)
        elevation = 100 + 10 * y_coords + np.random.normal(0, 5, len(y_coords))

        # Feature 3: Population density (clustered)
        population = np.random.exponential(50, len(x_coords))

        # Target variable: Property value (correlated with features)
        property_value = (
            50000
            + 1000 * elevation
            + 100 * population
            - 500 * distance_from_origin
            + np.random.normal(0, 10000, len(x_coords))
        )

        # Create GeoDataFrame
        geometry = [Point(x, y) for x, y in zip(x_coords, y_coords)]

        gdf = gpd.GeoDataFrame(
            {
                "elevation": elevation,
                "population": population,
                "distance_origin": distance_from_origin,
                "property_value": property_value,
                "geometry": geometry,
            }
        )

        print(f"✅ Created dataset with {len(gdf)} spatial points")
        print(f"📍 Features: {list(gdf.columns[:-1])}")

        return gdf

    except ImportError:
        print("❌ GeoPandas not available - using dummy data")
        # Create dummy DataFrame
        n_points = 100
        data = {
            "elevation": np.random.normal(100, 20, n_points),
            "population": np.random.exponential(50, n_points),
            "distance_origin": np.random.uniform(0, 15, n_points),
            "property_value": np.random.normal(100000, 25000, n_points),
        }
        return pd.DataFrame(data)


def demo_spatial_feature_extraction():
    """Demonstrate spatial feature extraction."""
    print("\n🗺️ Spatial Feature Extraction Demo")
    print("=" * 50)

    # Create sample data
    gdf = create_sample_spatial_data()

    try:
        # Extract geometric features
        print("Extracting geometric features...")
        geometric_features = pmg.extract_geometric_features(gdf)
        print(f"✅ Extracted {len(geometric_features.columns)} geometric features")
        print(f"📊 Features: {list(geometric_features.columns[:5])}...")

        # Calculate spatial statistics
        print("\nCalculating spatial statistics...")
        spatial_stats = pmg.calculate_spatial_statistics(gdf, gdf["property_value"])
        print(f"✅ Calculated spatial statistics")
        if hasattr(spatial_stats, "moran_i") and spatial_stats.moran_i is not None:
            print(f"📈 Global Moran's I: {spatial_stats.moran_i:.4f}")

        # Analyze neighborhoods
        print("\nAnalyzing spatial neighborhoods...")
        neighborhood_features = pmg.analyze_neighborhoods(gdf, "property_value")
        print(
            f"✅ Extracted {len(neighborhood_features.columns)} neighborhood features"
        )

        return geometric_features, spatial_stats, neighborhood_features

    except Exception as e:
        print(f"❌ Feature extraction failed: {e}")
        return None, None, None


def demo_spatial_ml_models():
    """Demonstrate spatial ML models."""
    print("\n🤖 Spatial ML Models Demo")
    print("=" * 50)

    # Create sample data
    gdf = create_sample_spatial_data()

    try:
        # Prepare data
        print("Preparing spatial data...")
        if hasattr(gdf, "geometry"):
            X, y, geometry = pmg.prepare_spatial_data(gdf, "property_value")
        else:
            X = gdf.drop(columns=["property_value"])
            y = gdf["property_value"]
            geometry = None

        print(f"✅ Prepared data: {X.shape[0]} samples, {X.shape[1]} features")

        # Spatial regression
        print("\nTesting spatial regression...")
        spatial_reg = pmg.create_spatial_ml_model("regression")
        if spatial_reg and hasattr(spatial_reg, "fit"):
            if geometry is not None:
                spatial_reg.fit(X, y, geometry=geometry)
                predictions = spatial_reg.predict(X, geometry=geometry)
            else:
                spatial_reg.fit(X, y)
                predictions = spatial_reg.predict(X)

            r2_score = pmg.spatial_r2_score(y, predictions, geometry)
            print(f"✅ Spatial regression R² score: {r2_score:.4f}")

        # Spatial clustering
        print("\nTesting spatial clustering...")
        spatial_kmeans = pmg.create_spatial_ml_model("clustering", n_clusters=3)
        if spatial_kmeans and hasattr(spatial_kmeans, "fit"):
            if geometry is not None:
                spatial_kmeans.fit(X, geometry=geometry)
                cluster_labels = spatial_kmeans.predict(X, geometry=geometry)
            else:
                spatial_kmeans.fit(X)
                cluster_labels = spatial_kmeans.labels_

            if cluster_labels is not None:
                n_clusters = len(np.unique(cluster_labels))
                print(f"✅ Spatial clustering found {n_clusters} clusters")

        return True

    except Exception as e:
        print(f"❌ Spatial ML models failed: {e}")
        return False


def demo_spatial_algorithms():
    """Demonstrate specialized spatial algorithms."""
    print("\n🧠 Specialized Spatial Algorithms Demo")
    print("=" * 50)

    # Create sample data
    gdf = create_sample_spatial_data()

    try:
        # Spatial autocorrelation analysis
        print("Analyzing spatial autocorrelation...")
        autocorr_results = pmg.analyze_spatial_autocorrelation(gdf, "property_value")
        if autocorr_results and hasattr(autocorr_results, "global_moran_i"):
            print(f"✅ Global Moran's I: {autocorr_results.global_moran_i:.4f}")
            print(f"📊 P-value: {autocorr_results.global_moran_p:.4f}")
        else:
            print("✅ Spatial autocorrelation analysis completed")

        # Hotspot analysis
        print("\nDetecting spatial hotspots...")
        hotspot_results = pmg.detect_hotspots(gdf, "property_value")
        if hotspot_results and hasattr(hotspot_results, "hotspot_classification"):
            n_hotspots = np.sum(hotspot_results.hotspot_classification == 1)
            n_coldspots = np.sum(hotspot_results.hotspot_classification == -1)
            print(f"✅ Found {n_hotspots} hotspots and {n_coldspots} coldspots")
        else:
            print("✅ Hotspot analysis completed")

        # Kriging interpolation (if possible)
        print("\nTesting kriging interpolation...")
        try:
            kriging_model = pmg.Kriging()
            if hasattr(gdf, "geometry"):
                X = gdf.drop(columns=["property_value", "geometry"])
                y = gdf["property_value"]
                kriging_model.fit(X, y, geometry=gdf.geometry)
                print("✅ Kriging model fitted successfully")
            else:
                print("ℹ️ Kriging requires geometry data")
        except Exception as e:
            print(f"ℹ️ Kriging not available: {e}")

        # Geographically Weighted Regression
        print("\nTesting Geographically Weighted Regression...")
        try:
            gwr_model = pmg.GeographicallyWeightedRegression()
            if hasattr(gdf, "geometry"):
                features = ["elevation", "population", "distance_origin"]
                gwr_results = pmg.calculate_gwr(gdf, "property_value", features)
                if gwr_results and hasattr(gwr_results, "predictions"):
                    print(
                        f"✅ GWR completed with bandwidth: {gwr_results.bandwidth:.2f}"
                    )
                else:
                    print("✅ GWR analysis completed")
            else:
                print("ℹ️ GWR requires geometry data")
        except Exception as e:
            print(f"ℹ️ GWR not available: {e}")

        return True

    except Exception as e:
        print(f"❌ Spatial algorithms failed: {e}")
        return False


def demo_spatial_pipeline():
    """Demonstrate complete spatial analysis pipeline."""
    print("\n🔄 Spatial Analysis Pipeline Demo")
    print("=" * 50)

    # Create sample data
    gdf = create_sample_spatial_data()

    try:
        # Run comprehensive spatial analysis
        print("Running comprehensive spatial analysis...")
        analysis_results = pmg.analyze_spatial_data(gdf, "property_value")

        if analysis_results:
            print("✅ Comprehensive analysis completed")
            print(f"📊 Analysis components: {list(analysis_results.keys())}")

        # Create and run spatial pipeline
        print("\nCreating spatial ML pipeline...")
        pipeline = pmg.create_spatial_pipeline(model_type="regression")

        if pipeline:
            print("✅ Spatial pipeline created successfully")

            # Run pipeline
            if hasattr(gdf, "geometry"):
                pipeline_results = pmg.run_spatial_analysis_pipeline(
                    gdf, "property_value", model_type="regression"
                )
                if pipeline_results:
                    print("✅ Pipeline execution completed")
                    print(f"📊 Results: {list(pipeline_results.keys())}")
            else:
                print("ℹ️ Pipeline requires geometry data for full functionality")

        # Auto spatial analysis
        print("\nRunning automated spatial analysis...")
        auto_results = pmg.auto_spatial_analysis(gdf, "property_value")

        if auto_results:
            print("✅ Automated analysis completed")
            print(f"📊 Auto analysis components: {list(auto_results.keys())}")

        return True

    except Exception as e:
        print(f"❌ Spatial pipeline failed: {e}")
        return False


def demo_model_evaluation():
    """Demonstrate spatial model evaluation."""
    print("\n📈 Spatial Model Evaluation Demo")
    print("=" * 50)

    # Create sample data
    gdf = create_sample_spatial_data()

    try:
        # Prepare data
        if hasattr(gdf, "geometry"):
            X, y, geometry = pmg.prepare_spatial_data(gdf, "property_value")
        else:
            X = gdf.drop(columns=["property_value"])
            y = gdf["property_value"]
            geometry = None

        # Create and evaluate model
        print("Creating and evaluating spatial model...")
        model = pmg.create_spatial_ml_model("regression")

        if model and hasattr(model, "fit"):
            # Fit model
            if geometry is not None:
                model.fit(X, y, geometry=geometry)
                predictions = model.predict(X, geometry=geometry)
            else:
                model.fit(X, y)
                predictions = model.predict(X)

            # Evaluate model
            r2_score = pmg.spatial_r2_score(y, predictions, geometry)
            print(f"✅ Model R² score: {r2_score:.4f}")

            # Cross-validation
            print("Performing spatial cross-validation...")
            cv_scores = pmg.evaluate_spatial_model(model, X, y, geometry, cv=3)
            if len(cv_scores) > 0:
                print(f"✅ CV scores: {cv_scores}")
                print(
                    f"📊 Mean CV score: {np.mean(cv_scores):.4f} ± {np.std(cv_scores):.4f}"
                )

        return True

    except Exception as e:
        print(f"❌ Model evaluation failed: {e}")
        return False


def main():
    """Run the complete ML/Analytics demo."""
    print("📊 PyMapGIS ML/Analytics Integration Demo")
    print("=" * 60)
    print("Demonstrating spatial machine learning and analytics capabilities")

    try:
        # Demo spatial feature extraction
        geometric_features, spatial_stats, neighborhood_features = (
            demo_spatial_feature_extraction()
        )

        # Demo spatial ML models
        ml_success = demo_spatial_ml_models()

        # Demo spatial algorithms
        algorithms_success = demo_spatial_algorithms()

        # Demo spatial pipeline
        pipeline_success = demo_spatial_pipeline()

        # Demo model evaluation
        evaluation_success = demo_model_evaluation()

        print("\n🎉 ML/Analytics Integration Demo Complete!")
        print("=" * 60)

        # Summary
        successes = sum(
            [
                geometric_features is not None,
                ml_success,
                algorithms_success,
                pipeline_success,
                evaluation_success,
            ]
        )

        print(f"✅ Successfully demonstrated {successes}/5 ML/Analytics components")
        print("🧠 PyMapGIS provides comprehensive spatial ML capabilities")
        print("📊 Ready for enterprise spatial analytics and machine learning")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
