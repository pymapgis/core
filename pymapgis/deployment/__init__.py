"""
PyMapGIS Deployment Tools & DevOps Infrastructure

Comprehensive deployment and DevOps capabilities for PyMapGIS including:
- Docker containerization with multi-stage builds
- Kubernetes orchestration and scaling
- Cloud deployment templates (AWS, GCP, Azure)
- CI/CD pipeline integration
- Infrastructure as Code (Terraform)
- Monitoring and observability
- Health checks and service discovery
"""

from typing import Dict, List, Any, Optional, Union
import os
import json
import yaml
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Version and metadata
__version__ = "0.3.2"

# Import deployment components
try:
    from .docker import (
        DockerManager,
        DockerImageBuilder,
        DockerComposeManager,
        ContainerOrchestrator,
        build_docker_image,
        create_docker_compose,
        deploy_container,
        get_container_status,
    )
except ImportError:
    logger.warning("Docker components not available")
    DockerManager = None  # type: ignore
    DockerImageBuilder = None  # type: ignore
    DockerComposeManager = None  # type: ignore
    ContainerOrchestrator = None  # type: ignore

try:
    from .kubernetes import (
        KubernetesManager,
        KubernetesDeployment,
        ServiceManager,
        IngressManager,
        deploy_to_kubernetes,
        scale_deployment,
        get_pod_status,
        create_service,
    )
except ImportError:
    logger.warning("Kubernetes components not available")
    KubernetesManager = None  # type: ignore
    KubernetesDeployment = None  # type: ignore
    ServiceManager = None  # type: ignore
    IngressManager = None  # type: ignore

try:
    from .cloud import (
        CloudDeploymentManager,
        AWSDeployment,
        GCPDeployment,
        AzureDeployment,
        TerraformManager,
        deploy_to_aws,
        deploy_to_gcp,
        deploy_to_azure,
        create_infrastructure,
    )
except ImportError:
    logger.warning("Cloud deployment components not available")
    CloudDeploymentManager = None  # type: ignore
    AWSDeployment = None  # type: ignore
    GCPDeployment = None  # type: ignore
    AzureDeployment = None  # type: ignore
    TerraformManager = None  # type: ignore

try:
    from .cicd import (
        CICDManager,
        GitHubActionsManager,
        PipelineManager,
        DeploymentPipeline,
        create_github_workflow,
        trigger_deployment,
        get_deployment_status,
        setup_cicd_pipeline,
    )
except ImportError:
    logger.warning("CI/CD components not available")
    CICDManager = None  # type: ignore
    GitHubActionsManager = None  # type: ignore
    PipelineManager = None  # type: ignore
    DeploymentPipeline = None  # type: ignore

try:
    from .monitoring import (
        MonitoringManager,
        HealthCheckManager,
        MetricsCollector,
        LoggingManager,
        setup_monitoring,
        create_health_checks,
        collect_metrics,
        configure_logging,
    )
except ImportError:
    logger.warning("Monitoring components not available")
    MonitoringManager = None  # type: ignore
    HealthCheckManager = None  # type: ignore
    MetricsCollector = None  # type: ignore
    LoggingManager = None  # type: ignore

# Deployment configuration
DEFAULT_DEPLOYMENT_CONFIG = {
    "docker": {
        "base_image": "python:3.11-slim",
        "working_dir": "/app",
        "port": 8000,
        "environment": "production",
        "multi_stage": True,
        "optimize": True,
    },
    "kubernetes": {
        "namespace": "pymapgis",
        "replicas": 3,
        "resources": {
            "requests": {"cpu": "100m", "memory": "256Mi"},
            "limits": {"cpu": "500m", "memory": "512Mi"},
        },
        "autoscaling": {
            "enabled": True,
            "min_replicas": 2,
            "max_replicas": 10,
            "target_cpu": 70,
        },
    },
    "cloud": {
        "region": "us-west-2",
        "instance_type": "t3.medium",
        "auto_scaling": True,
        "load_balancer": True,
        "ssl_enabled": True,
    },
    "monitoring": {
        "health_checks": True,
        "metrics_collection": True,
        "logging_level": "INFO",
        "retention_days": 30,
    },
}

# Global deployment manager instances
_docker_manager = None
_kubernetes_manager = None
_cloud_manager = None
_cicd_manager = None
_monitoring_manager = None


def get_docker_manager() -> Optional["DockerManager"]:
    """Get global Docker manager instance."""
    global _docker_manager
    if _docker_manager is None and DockerManager is not None:
        _docker_manager = DockerManager()
    return _docker_manager


def get_kubernetes_manager() -> Optional["KubernetesManager"]:
    """Get global Kubernetes manager instance."""
    global _kubernetes_manager
    if _kubernetes_manager is None and KubernetesManager is not None:
        _kubernetes_manager = KubernetesManager()
    return _kubernetes_manager


def get_cloud_manager() -> Optional["CloudDeploymentManager"]:
    """Get global cloud deployment manager instance."""
    global _cloud_manager
    if _cloud_manager is None and CloudDeploymentManager is not None:
        _cloud_manager = CloudDeploymentManager()
    return _cloud_manager


def get_cicd_manager() -> Optional["CICDManager"]:
    """Get global CI/CD manager instance."""
    global _cicd_manager
    if _cicd_manager is None and CICDManager is not None:
        _cicd_manager = CICDManager()
    return _cicd_manager


def get_monitoring_manager() -> Optional["MonitoringManager"]:
    """Get global monitoring manager instance."""
    global _monitoring_manager
    if _monitoring_manager is None and MonitoringManager is not None:
        _monitoring_manager = MonitoringManager()
    return _monitoring_manager


# Convenience functions for quick deployment
def quick_docker_deploy(
    app_path: str,
    image_name: str = "pymapgis-app",
    port: int = 8000,
    environment: str = "production",
) -> Dict[str, Any]:
    """
    Quick Docker deployment with sensible defaults.

    Args:
        app_path: Path to application directory
        image_name: Docker image name
        port: Application port
        environment: Deployment environment

    Returns:
        Deployment result
    """
    docker_manager = get_docker_manager()
    if docker_manager is None:
        return {"error": "Docker manager not available"}

    return docker_manager.quick_deploy(
        app_path=app_path,
        image_name=image_name,
        port=port,
        environment=environment,
    )


def quick_kubernetes_deploy(
    image_name: str,
    app_name: str = "pymapgis",
    namespace: str = "default",
    replicas: int = 3,
) -> Dict[str, Any]:
    """
    Quick Kubernetes deployment with sensible defaults.

    Args:
        image_name: Docker image name
        app_name: Application name
        namespace: Kubernetes namespace
        replicas: Number of replicas

    Returns:
        Deployment result
    """
    k8s_manager = get_kubernetes_manager()
    if k8s_manager is None:
        return {"error": "Kubernetes manager not available"}

    return k8s_manager.quick_deploy(
        image_name=image_name,
        app_name=app_name,
        namespace=namespace,
        replicas=replicas,
    )


def quick_cloud_deploy(
    provider: str,
    region: str = "us-west-2",
    instance_type: str = "t3.medium",
    auto_scaling: bool = True,
) -> Dict[str, Any]:
    """
    Quick cloud deployment with sensible defaults.

    Args:
        provider: Cloud provider (aws, gcp, azure)
        region: Deployment region
        instance_type: Instance type
        auto_scaling: Enable auto scaling

    Returns:
        Deployment result
    """
    cloud_manager = get_cloud_manager()
    if cloud_manager is None:
        return {"error": "Cloud manager not available"}

    return cloud_manager.quick_deploy(
        provider=provider,
        region=region,
        instance_type=instance_type,
        auto_scaling=auto_scaling,
    )


def setup_complete_deployment(
    app_path: str,
    deployment_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Setup complete deployment infrastructure.

    Args:
        app_path: Path to application directory
        deployment_config: Optional deployment configuration

    Returns:
        Complete deployment setup result
    """
    config = deployment_config or DEFAULT_DEPLOYMENT_CONFIG
    results: Dict[str, Any] = {}

    try:
        # Docker setup
        docker_port = config["docker"]["port"]
        docker_env = config["docker"]["environment"]
        docker_result = quick_docker_deploy(
            app_path=app_path,
            port=int(docker_port) if docker_port is not None else 8000,  # type: ignore
            environment=str(docker_env) if docker_env is not None else "production",
        )
        results["docker"] = docker_result

        # Kubernetes setup if Docker successful
        if "error" not in docker_result:
            k8s_replicas = config["kubernetes"]["replicas"]
            k8s_result = quick_kubernetes_deploy(
                image_name=docker_result.get("image_name", "pymapgis-app"),
                replicas=int(k8s_replicas) if k8s_replicas is not None else 3,  # type: ignore
            )
            results["kubernetes"] = k8s_result

        # Monitoring setup
        monitoring_manager = get_monitoring_manager()
        if monitoring_manager is not None:
            monitoring_result = monitoring_manager.setup_monitoring(
                config["monitoring"]
            )
            results["monitoring"] = monitoring_result

        results["status"] = "success"
        results["timestamp"] = datetime.now().isoformat()

    except Exception as e:
        logger.error(f"Complete deployment setup failed: {e}")
        results["status"] = "failed"
        results["error"] = str(e)

    return results


# Export all components
__all__ = [
    # Core managers
    "DockerManager",
    "KubernetesManager",
    "CloudDeploymentManager",
    "CICDManager",
    "MonitoringManager",
    # Specific components
    "DockerImageBuilder",
    "DockerComposeManager",
    "KubernetesDeployment",
    "ServiceManager",
    "AWSDeployment",
    "GCPDeployment",
    "AzureDeployment",
    "TerraformManager",
    "GitHubActionsManager",
    "HealthCheckManager",
    "MetricsCollector",
    # Manager getters
    "get_docker_manager",
    "get_kubernetes_manager",
    "get_cloud_manager",
    "get_cicd_manager",
    "get_monitoring_manager",
    # Convenience functions
    "quick_docker_deploy",
    "quick_kubernetes_deploy",
    "quick_cloud_deploy",
    "setup_complete_deployment",
    # Configuration
    "DEFAULT_DEPLOYMENT_CONFIG",
    # Version
    "__version__",
]
