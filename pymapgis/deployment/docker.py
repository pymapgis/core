"""
Docker Deployment Infrastructure for PyMapGIS

Comprehensive Docker containerization with:
- Multi-stage Dockerfiles for optimized builds
- Docker Compose for local development
- Container orchestration and management
- Production-ready configurations
- Health checks and monitoring
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

# Check for Docker availability
try:
    subprocess.run(["docker", "--version"], capture_output=True, check=True)
    DOCKER_AVAILABLE = True
except (subprocess.CalledProcessError, FileNotFoundError):
    DOCKER_AVAILABLE = False
    logger.warning("Docker not available")


@dataclass
class DockerConfig:
    """Docker configuration settings."""

    base_image: str = "python:3.11-slim"
    working_dir: str = "/app"
    port: int = 8000
    environment: str = "production"
    multi_stage: bool = True
    optimize: bool = True
    health_check: bool = True
    user: str = "pymapgis"


@dataclass
class BuildResult:
    """Docker build result."""

    success: bool
    image_name: str
    image_id: str
    build_time: float
    size_mb: float
    logs: List[str]
    error: Optional[str] = None


class DockerImageBuilder:
    """Docker image builder with multi-stage support."""

    def __init__(self, config: Optional[DockerConfig] = None):
        self.config = config or DockerConfig()
        self.build_history: List[BuildResult] = []

    def generate_dockerfile(
        self, app_path: str, requirements_file: str = "requirements.txt"
    ) -> str:
        """Generate optimized Dockerfile."""
        dockerfile_content = f"""# Multi-stage Dockerfile for PyMapGIS
# Stage 1: Build dependencies
FROM {self.config.base_image} as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    libgdal-dev \\
    libproj-dev \\
    libgeos-dev \\
    libspatialindex-dev \\
    && rm -rf /var/lib/apt/lists/*

# Create user
RUN groupadd -r {self.config.user} && useradd -r -g {self.config.user} {self.config.user}

# Set work directory
WORKDIR {self.config.working_dir}

# Copy requirements and install Python dependencies
COPY {requirements_file} .
RUN pip install --user --no-warn-script-location -r {requirements_file}

# Stage 2: Production image
FROM {self.config.base_image} as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/home/{self.config.user}/.local/bin:$PATH

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \\
    libgdal28 \\
    libproj19 \\
    libgeos-c1v5 \\
    libspatialindex6 \\
    && rm -rf /var/lib/apt/lists/*

# Create user
RUN groupadd -r {self.config.user} && useradd -r -g {self.config.user} {self.config.user}

# Copy Python packages from builder stage
COPY --from=builder /home/{self.config.user}/.local /home/{self.config.user}/.local

# Set work directory and copy application
WORKDIR {self.config.working_dir}
COPY --chown={self.config.user}:{self.config.user} . .

# Switch to non-root user
USER {self.config.user}

# Expose port
EXPOSE {self.config.port}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{self.config.port}/health || exit 1

# Default command
CMD ["python", "-m", "pymapgis.serve", "--host", "0.0.0.0", "--port", "{self.config.port}"]
"""
        return dockerfile_content

    def build_image(
        self,
        app_path: str,
        image_name: str,
        tag: str = "latest",
        build_args: Optional[Dict[str, str]] = None,
    ) -> BuildResult:
        """Build Docker image."""
        if not DOCKER_AVAILABLE:
            return BuildResult(
                success=False,
                image_name=image_name,
                image_id="",
                build_time=0.0,
                size_mb=0.0,
                logs=[],
                error="Docker not available",
            )

        start_time = datetime.now()
        logs: List[str] = []

        try:
            # Generate Dockerfile
            dockerfile_content = self.generate_dockerfile(app_path)
            dockerfile_path = Path(app_path) / "Dockerfile"

            with open(dockerfile_path, "w") as f:
                f.write(dockerfile_content)

            # Build command
            cmd = ["docker", "build", "-t", f"{image_name}:{tag}", "."]

            # Add build args
            if build_args:
                for key, value in build_args.items():
                    cmd.extend(["--build-arg", f"{key}={value}"])

            # Execute build
            result = subprocess.run(
                cmd,
                cwd=app_path,
                capture_output=True,
                text=True,
                check=True,
            )

            logs.extend(result.stdout.split("\n"))

            # Get image info
            inspect_result = subprocess.run(
                ["docker", "inspect", f"{image_name}:{tag}"],
                capture_output=True,
                text=True,
                check=True,
            )

            image_info = json.loads(inspect_result.stdout)[0]
            image_id = image_info["Id"]
            size_bytes = image_info["Size"]
            size_mb = size_bytes / (1024 * 1024)

            build_time = (datetime.now() - start_time).total_seconds()

            build_result = BuildResult(
                success=True,
                image_name=f"{image_name}:{tag}",
                image_id=image_id,
                build_time=build_time,
                size_mb=size_mb,
                logs=logs,
            )

            self.build_history.append(build_result)
            logger.info(f"Successfully built image {image_name}:{tag}")

            return build_result

        except subprocess.CalledProcessError as e:
            error_msg = f"Docker build failed: {e.stderr}"
            logger.error(error_msg)

            return BuildResult(
                success=False,
                image_name=f"{image_name}:{tag}",
                image_id="",
                build_time=(datetime.now() - start_time).total_seconds(),
                size_mb=0.0,
                logs=logs + [error_msg],
                error=error_msg,
            )

    def push_image(
        self, image_name: str, registry: str = "docker.io"
    ) -> Dict[str, Any]:
        """Push image to registry."""
        if not DOCKER_AVAILABLE:
            return {"success": False, "error": "Docker not available"}

        try:
            # Tag for registry
            registry_image = f"{registry}/{image_name}"
            subprocess.run(
                ["docker", "tag", image_name, registry_image],
                check=True,
                capture_output=True,
            )

            # Push to registry
            result = subprocess.run(
                ["docker", "push", registry_image],
                check=True,
                capture_output=True,
                text=True,
            )

            logger.info(f"Successfully pushed {registry_image}")
            return {
                "success": True,
                "registry_image": registry_image,
                "logs": result.stdout.split("\n"),
            }

        except subprocess.CalledProcessError as e:
            error_msg = f"Docker push failed: {e.stderr}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}


class DockerComposeManager:
    """Docker Compose manager for multi-service deployments."""

    def __init__(self):
        self.compose_files: Dict[str, Dict[str, Any]] = {}

    def generate_compose_file(
        self,
        services: Dict[str, Dict[str, Any]],
        networks: Optional[Dict[str, Any]] = None,
        volumes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate Docker Compose configuration."""
        compose_config = {
            "version": "3.8",
            "services": {},
            "networks": networks or {"pymapgis-network": {"driver": "bridge"}},
            "volumes": volumes or {"pymapgis-data": {}},
        }

        # Default PyMapGIS service
        default_service = {
            "build": ".",
            "ports": ["8000:8000"],
            "environment": {
                "PYTHONPATH": "/app",
                "PYMAPGIS_ENV": "production",
            },
            "volumes": ["pymapgis-data:/app/data"],
            "networks": ["pymapgis-network"],
            "restart": "unless-stopped",
            "healthcheck": {
                "test": ["CMD", "curl", "-f", "http://localhost:8000/health"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3,
                "start_period": "40s",
            },
        }

        # Add services
        for service_name, service_config in services.items():
            compose_config["services"][service_name] = {  # type: ignore
                **default_service,
                **service_config,
            }

        return compose_config

    def create_compose_file(
        self,
        file_path: str,
        services: Dict[str, Dict[str, Any]],
        **kwargs,
    ) -> bool:
        """Create Docker Compose file."""
        try:
            compose_config = self.generate_compose_file(services, **kwargs)

            with open(file_path, "w") as f:
                yaml.dump(compose_config, f, default_flow_style=False)

            self.compose_files[file_path] = compose_config
            logger.info(f"Created Docker Compose file: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to create compose file: {e}")
            return False

    def deploy_compose(
        self, compose_file: str, project_name: str = "pymapgis"
    ) -> Dict[str, Any]:
        """Deploy using Docker Compose."""
        if not DOCKER_AVAILABLE:
            return {"success": False, "error": "Docker not available"}

        try:
            # Deploy with compose
            result = subprocess.run(
                ["docker-compose", "-f", compose_file, "-p", project_name, "up", "-d"],
                check=True,
                capture_output=True,
                text=True,
            )

            logger.info(f"Successfully deployed compose project: {project_name}")
            return {
                "success": True,
                "project_name": project_name,
                "logs": result.stdout.split("\n"),
            }

        except subprocess.CalledProcessError as e:
            error_msg = f"Docker Compose deployment failed: {e.stderr}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}


class ContainerOrchestrator:
    """Container orchestration and management."""

    def __init__(self):
        self.running_containers: Dict[str, Dict[str, Any]] = {}

    def run_container(
        self,
        image_name: str,
        container_name: str,
        port_mapping: Optional[Dict[int, int]] = None,
        environment: Optional[Dict[str, str]] = None,
        volumes: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Run a container."""
        if not DOCKER_AVAILABLE:
            return {"success": False, "error": "Docker not available"}

        try:
            cmd = ["docker", "run", "-d", "--name", container_name]

            # Add port mappings
            if port_mapping:
                for host_port, container_port in port_mapping.items():
                    cmd.extend(["-p", f"{host_port}:{container_port}"])

            # Add environment variables
            if environment:
                for key, value in environment.items():
                    cmd.extend(["-e", f"{key}={value}"])

            # Add volume mounts
            if volumes:
                for host_path, container_path in volumes.items():
                    cmd.extend(["-v", f"{host_path}:{container_path}"])

            cmd.append(image_name)

            # Run container
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            container_id = result.stdout.strip()

            container_info = {
                "container_id": container_id,
                "container_name": container_name,
                "image_name": image_name,
                "status": "running",
                "created_at": datetime.now().isoformat(),
            }

            self.running_containers[container_name] = container_info
            logger.info(f"Successfully started container: {container_name}")

            return {"success": True, **container_info}

        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to run container: {e.stderr}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def get_container_status(self, container_name: str) -> Dict[str, Any]:
        """Get container status."""
        if not DOCKER_AVAILABLE:
            return {"error": "Docker not available"}

        try:
            result = subprocess.run(
                ["docker", "inspect", container_name],
                check=True,
                capture_output=True,
                text=True,
            )

            container_info = json.loads(result.stdout)[0]

            return {
                "name": container_info["Name"],
                "status": container_info["State"]["Status"],
                "running": container_info["State"]["Running"],
                "created": container_info["Created"],
                "image": container_info["Config"]["Image"],
                "ports": container_info["NetworkSettings"]["Ports"],
            }

        except subprocess.CalledProcessError:
            return {"error": f"Container {container_name} not found"}


class DockerManager:
    """Main Docker deployment manager."""

    def __init__(self, config: Optional[DockerConfig] = None):
        self.config = config or DockerConfig()
        self.image_builder = DockerImageBuilder(self.config)
        self.compose_manager = DockerComposeManager()
        self.orchestrator = ContainerOrchestrator()

    def quick_deploy(
        self,
        app_path: str,
        image_name: str = "pymapgis-app",
        port: int = 8000,
        environment: str = "production",
    ) -> Dict[str, Any]:
        """Quick deployment with sensible defaults."""
        try:
            # Build image
            build_result = self.image_builder.build_image(app_path, image_name)

            if not build_result.success:
                return {"success": False, "error": build_result.error}

            # Run container
            container_result = self.orchestrator.run_container(
                image_name=build_result.image_name,
                container_name=f"{image_name}-container",
                port_mapping={port: port},
                environment={"PYMAPGIS_ENV": environment},
            )

            return {
                "success": True,
                "image_name": build_result.image_name,
                "container": container_result,
                "build_time": build_result.build_time,
                "image_size_mb": build_result.size_mb,
            }

        except Exception as e:
            logger.error(f"Quick deployment failed: {e}")
            return {"success": False, "error": str(e)}


# Convenience functions
def build_docker_image(app_path: str, image_name: str, **kwargs) -> BuildResult:
    """Build Docker image."""
    builder = DockerImageBuilder()
    return builder.build_image(app_path, image_name, **kwargs)


def create_docker_compose(
    file_path: str, services: Dict[str, Dict[str, Any]], **kwargs
) -> bool:
    """Create Docker Compose file."""
    manager = DockerComposeManager()
    return manager.create_compose_file(file_path, services, **kwargs)


def deploy_container(image_name: str, container_name: str, **kwargs) -> Dict[str, Any]:
    """Deploy container."""
    orchestrator = ContainerOrchestrator()
    return orchestrator.run_container(image_name, container_name, **kwargs)


def get_container_status(container_name: str) -> Dict[str, Any]:
    """Get container status."""
    orchestrator = ContainerOrchestrator()
    return orchestrator.get_container_status(container_name)
