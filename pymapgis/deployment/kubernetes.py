"""
Kubernetes Deployment Infrastructure for PyMapGIS

Comprehensive Kubernetes orchestration with:
- Deployment manifests and configurations
- Service discovery and load balancing
- Ingress controllers and SSL termination
- Auto-scaling and resource management
- Health checks and monitoring
- ConfigMaps and Secrets management
"""

import os
import json
import yaml
import subprocess
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Check for kubectl availability
try:
    subprocess.run(["kubectl", "version", "--client"], capture_output=True, check=True)
    KUBECTL_AVAILABLE = True
except (subprocess.CalledProcessError, FileNotFoundError):
    KUBECTL_AVAILABLE = False
    logger.warning("kubectl not available")


@dataclass
class KubernetesConfig:
    """Kubernetes configuration settings."""

    namespace: str = "pymapgis"
    replicas: int = 3
    image_pull_policy: str = "Always"
    service_type: str = "ClusterIP"
    port: int = 8000
    target_port: int = 8000
    resources: Dict[str, Dict[str, str]] = None
    autoscaling: Dict[str, Any] = None

    def __post_init__(self):
        if self.resources is None:
            self.resources = {
                "requests": {"cpu": "100m", "memory": "256Mi"},
                "limits": {"cpu": "500m", "memory": "512Mi"},
            }

        if self.autoscaling is None:
            self.autoscaling = {
                "enabled": True,
                "min_replicas": 2,
                "max_replicas": 10,
                "target_cpu": 70,
            }


@dataclass
class DeploymentResult:
    """Kubernetes deployment result."""

    success: bool
    deployment_name: str
    namespace: str
    replicas: int
    status: str
    pods: List[Dict[str, Any]]
    services: List[Dict[str, Any]]
    error: Optional[str] = None


class KubernetesDeployment:
    """Kubernetes deployment manager."""

    def __init__(self, config: Optional[KubernetesConfig] = None):
        self.config = config or KubernetesConfig()
        self.deployments: Dict[str, Dict[str, Any]] = {}

    def generate_deployment_manifest(
        self,
        app_name: str,
        image_name: str,
        labels: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Generate Kubernetes deployment manifest."""
        default_labels = {"app": app_name, "version": "v1"}
        labels = {**default_labels, **(labels or {})}

        manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"{app_name}-deployment",
                "namespace": self.config.namespace,
                "labels": labels,
            },
            "spec": {
                "replicas": self.config.replicas,
                "selector": {"matchLabels": {"app": app_name}},
                "template": {
                    "metadata": {"labels": labels},
                    "spec": {
                        "containers": [
                            {
                                "name": app_name,
                                "image": image_name,
                                "imagePullPolicy": self.config.image_pull_policy,
                                "ports": [{"containerPort": self.config.target_port}],
                                "resources": self.config.resources,
                                "env": [
                                    {"name": "PYMAPGIS_ENV", "value": "production"},
                                    {
                                        "name": "PORT",
                                        "value": str(self.config.target_port),
                                    },
                                ],
                                "livenessProbe": {
                                    "httpGet": {
                                        "path": "/health",
                                        "port": self.config.target_port,
                                    },
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 10,
                                },
                                "readinessProbe": {
                                    "httpGet": {
                                        "path": "/ready",
                                        "port": self.config.target_port,
                                    },
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 5,
                                },
                            }
                        ],
                        "restartPolicy": "Always",
                    },
                },
            },
        }

        return manifest

    def generate_service_manifest(
        self,
        app_name: str,
        labels: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Generate Kubernetes service manifest."""
        default_labels = {"app": app_name}
        labels = {**default_labels, **(labels or {})}

        manifest = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{app_name}-service",
                "namespace": self.config.namespace,
                "labels": labels,
            },
            "spec": {
                "selector": {"app": app_name},
                "ports": [
                    {
                        "protocol": "TCP",
                        "port": self.config.port,
                        "targetPort": self.config.target_port,
                    }
                ],
                "type": self.config.service_type,
            },
        }

        return manifest

    def generate_hpa_manifest(
        self,
        app_name: str,
        labels: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Generate Horizontal Pod Autoscaler manifest."""
        if not self.config.autoscaling["enabled"]:
            return {}

        default_labels = {"app": app_name}
        labels = {**default_labels, **(labels or {})}

        manifest = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": f"{app_name}-hpa",
                "namespace": self.config.namespace,
                "labels": labels,
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": f"{app_name}-deployment",
                },
                "minReplicas": self.config.autoscaling["min_replicas"],
                "maxReplicas": self.config.autoscaling["max_replicas"],
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": self.config.autoscaling[
                                    "target_cpu"
                                ],
                            },
                        },
                    }
                ],
            },
        }

        return manifest

    def deploy(
        self,
        app_name: str,
        image_name: str,
        labels: Optional[Dict[str, str]] = None,
    ) -> DeploymentResult:
        """Deploy application to Kubernetes."""
        if not KUBECTL_AVAILABLE:
            return DeploymentResult(
                success=False,
                deployment_name=f"{app_name}-deployment",
                namespace=self.config.namespace,
                replicas=0,
                status="failed",
                pods=[],
                services=[],
                error="kubectl not available",
            )

        try:
            # Create namespace if it doesn't exist
            self._ensure_namespace()

            # Generate manifests
            deployment_manifest = self.generate_deployment_manifest(
                app_name, image_name, labels
            )
            service_manifest = self.generate_service_manifest(app_name, labels)
            hpa_manifest = self.generate_hpa_manifest(app_name, labels)

            # Apply deployment
            self._apply_manifest(deployment_manifest)
            self._apply_manifest(service_manifest)

            if hpa_manifest:
                self._apply_manifest(hpa_manifest)

            # Wait for deployment to be ready
            deployment_name = f"{app_name}-deployment"
            self._wait_for_deployment(deployment_name)

            # Get deployment status
            pods = self._get_pods(app_name)
            services = self._get_services(app_name)

            result = DeploymentResult(
                success=True,
                deployment_name=deployment_name,
                namespace=self.config.namespace,
                replicas=len(pods),
                status="running",
                pods=pods,
                services=services,
            )

            self.deployments[app_name] = {
                "deployment": deployment_manifest,
                "service": service_manifest,
                "hpa": hpa_manifest,
                "result": result,
            }

            logger.info(f"Successfully deployed {app_name} to Kubernetes")
            return result

        except Exception as e:
            error_msg = f"Kubernetes deployment failed: {e}"
            logger.error(error_msg)

            return DeploymentResult(
                success=False,
                deployment_name=f"{app_name}-deployment",
                namespace=self.config.namespace,
                replicas=0,
                status="failed",
                pods=[],
                services=[],
                error=error_msg,
            )

    def _ensure_namespace(self):
        """Ensure namespace exists."""
        try:
            subprocess.run(
                ["kubectl", "get", "namespace", self.config.namespace],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError:
            # Create namespace
            subprocess.run(
                ["kubectl", "create", "namespace", self.config.namespace],
                check=True,
                capture_output=True,
            )

    def _apply_manifest(self, manifest: Dict[str, Any]):
        """Apply Kubernetes manifest."""
        manifest_yaml = yaml.dump(manifest)

        process = subprocess.Popen(
            ["kubectl", "apply", "-f", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        stdout, stderr = process.communicate(input=manifest_yaml)

        if process.returncode != 0:
            raise Exception(f"kubectl apply failed: {stderr}")

    def _wait_for_deployment(self, deployment_name: str, timeout: int = 300):
        """Wait for deployment to be ready."""
        subprocess.run(
            [
                "kubectl",
                "wait",
                "--for=condition=available",
                f"deployment/{deployment_name}",
                f"--namespace={self.config.namespace}",
                f"--timeout={timeout}s",
            ],
            check=True,
            capture_output=True,
        )

    def _get_pods(self, app_name: str) -> List[Dict[str, Any]]:
        """Get pods for application."""
        try:
            result = subprocess.run(
                [
                    "kubectl",
                    "get",
                    "pods",
                    f"--namespace={self.config.namespace}",
                    f"--selector=app={app_name}",
                    "-o",
                    "json",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            pods_data = json.loads(result.stdout)
            return pods_data.get("items", [])

        except subprocess.CalledProcessError:
            return []

    def _get_services(self, app_name: str) -> List[Dict[str, Any]]:
        """Get services for application."""
        try:
            result = subprocess.run(
                [
                    "kubectl",
                    "get",
                    "services",
                    f"--namespace={self.config.namespace}",
                    f"--selector=app={app_name}",
                    "-o",
                    "json",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            services_data = json.loads(result.stdout)
            return services_data.get("items", [])

        except subprocess.CalledProcessError:
            return []


class ServiceManager:
    """Kubernetes service management."""

    def __init__(self, namespace: str = "pymapgis"):
        self.namespace = namespace

    def create_load_balancer_service(
        self,
        app_name: str,
        port: int = 80,
        target_port: int = 8000,
    ) -> Dict[str, Any]:
        """Create LoadBalancer service."""
        manifest = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{app_name}-lb",
                "namespace": self.namespace,
            },
            "spec": {
                "selector": {"app": app_name},
                "ports": [{"port": port, "targetPort": target_port}],
                "type": "LoadBalancer",
            },
        }

        return self._apply_service(manifest)

    def _apply_service(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Apply service manifest."""
        if not KUBECTL_AVAILABLE:
            return {"success": False, "error": "kubectl not available"}

        try:
            manifest_yaml = yaml.dump(manifest)

            process = subprocess.Popen(
                ["kubectl", "apply", "-f", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            stdout, stderr = process.communicate(input=manifest_yaml)

            if process.returncode != 0:
                return {"success": False, "error": stderr}

            return {"success": True, "output": stdout}

        except Exception as e:
            return {"success": False, "error": str(e)}


class IngressManager:
    """Kubernetes ingress management."""

    def __init__(self, namespace: str = "pymapgis"):
        self.namespace = namespace

    def create_ingress(
        self,
        app_name: str,
        host: str,
        service_name: str,
        service_port: int = 80,
        tls_enabled: bool = True,
    ) -> Dict[str, Any]:
        """Create ingress for application."""
        manifest = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": f"{app_name}-ingress",
                "namespace": self.namespace,
                "annotations": {
                    "nginx.ingress.kubernetes.io/rewrite-target": "/",
                },
            },
            "spec": {
                "rules": [
                    {
                        "host": host,
                        "http": {
                            "paths": [
                                {
                                    "path": "/",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": service_name,
                                            "port": {"number": service_port},
                                        }
                                    },
                                }
                            ]
                        },
                    }
                ]
            },
        }

        if tls_enabled:
            manifest["spec"]["tls"] = [  # type: ignore
                {"hosts": [host], "secretName": f"{app_name}-tls"}
            ]

        return self._apply_ingress(manifest)

    def _apply_ingress(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Apply ingress manifest."""
        if not KUBECTL_AVAILABLE:
            return {"success": False, "error": "kubectl not available"}

        try:
            manifest_yaml = yaml.dump(manifest)

            process = subprocess.Popen(
                ["kubectl", "apply", "-f", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            stdout, stderr = process.communicate(input=manifest_yaml)

            if process.returncode != 0:
                return {"success": False, "error": stderr}

            return {"success": True, "output": stdout}

        except Exception as e:
            return {"success": False, "error": str(e)}


class KubernetesManager:
    """Main Kubernetes deployment manager."""

    def __init__(self, config: Optional[KubernetesConfig] = None):
        self.config = config or KubernetesConfig()
        self.deployment = KubernetesDeployment(self.config)
        self.service_manager = ServiceManager(self.config.namespace)
        self.ingress_manager = IngressManager(self.config.namespace)

    def quick_deploy(
        self,
        image_name: str,
        app_name: str = "pymapgis",
        namespace: str = "default",
        replicas: int = 3,
    ) -> Dict[str, Any]:
        """Quick Kubernetes deployment."""
        try:
            # Update config
            self.config.namespace = namespace
            self.config.replicas = replicas

            # Deploy application
            result = self.deployment.deploy(app_name, image_name)

            if not result.success:
                return {"success": False, "error": result.error}

            # Create load balancer service
            lb_result = self.service_manager.create_load_balancer_service(app_name)

            return {
                "success": True,
                "deployment": {
                    "name": result.deployment_name,
                    "namespace": result.namespace,
                    "replicas": result.replicas,
                    "status": result.status,
                },
                "load_balancer": lb_result,
                "pods": len(result.pods),
                "services": len(result.services),
            }

        except Exception as e:
            logger.error(f"Quick Kubernetes deployment failed: {e}")
            return {"success": False, "error": str(e)}


# Convenience functions
def deploy_to_kubernetes(image_name: str, app_name: str, **kwargs) -> DeploymentResult:
    """Deploy to Kubernetes."""
    deployment = KubernetesDeployment()
    return deployment.deploy(app_name, image_name, **kwargs)


def scale_deployment(
    deployment_name: str, replicas: int, namespace: str = "pymapgis"
) -> Dict[str, Any]:
    """Scale Kubernetes deployment."""
    if not KUBECTL_AVAILABLE:
        return {"success": False, "error": "kubectl not available"}

    try:
        subprocess.run(
            [
                "kubectl",
                "scale",
                f"deployment/{deployment_name}",
                f"--replicas={replicas}",
                f"--namespace={namespace}",
            ],
            check=True,
            capture_output=True,
        )

        return {"success": True, "replicas": replicas}

    except subprocess.CalledProcessError as e:
        return {"success": False, "error": str(e)}


def get_pod_status(app_name: str, namespace: str = "pymapgis") -> List[Dict[str, Any]]:
    """Get pod status."""
    deployment = KubernetesDeployment()
    deployment.config.namespace = namespace
    return deployment._get_pods(app_name)


def create_service(
    app_name: str, service_type: str = "ClusterIP", **kwargs
) -> Dict[str, Any]:
    """Create Kubernetes service."""
    service_manager = ServiceManager()

    if service_type == "LoadBalancer":
        return service_manager.create_load_balancer_service(app_name, **kwargs)
    else:
        # Default ClusterIP service creation would go here
        return {
            "success": False,
            "error": f"Service type {service_type} not implemented",
        }
