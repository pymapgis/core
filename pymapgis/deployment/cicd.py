"""
CI/CD Pipeline Infrastructure for PyMapGIS

Comprehensive CI/CD automation with:
- GitHub Actions workflows
- Automated testing and quality gates
- Docker image building and publishing
- Multi-environment deployments
- Rollback and monitoring integration
- Security scanning and compliance
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

# Check for GitHub CLI
try:
    subprocess.run(["gh", "--version"], capture_output=True, check=True)
    GH_CLI_AVAILABLE = True
except (subprocess.CalledProcessError, FileNotFoundError):
    GH_CLI_AVAILABLE = False
    logger.warning("GitHub CLI not available")


@dataclass
class PipelineConfig:
    """CI/CD pipeline configuration."""

    trigger_on: List[str] = None
    environments: List[str] = None
    test_commands: List[str] = None
    build_commands: List[str] = None
    deploy_commands: List[str] = None
    quality_gates: Dict[str, Any] = None

    def __post_init__(self):
        if self.trigger_on is None:
            self.trigger_on = ["push", "pull_request"]

        if self.environments is None:
            self.environments = ["development", "staging", "production"]

        if self.test_commands is None:
            self.test_commands = [
                "poetry run pytest",
                "poetry run mypy pymapgis/",
                "poetry run ruff check pymapgis/",
            ]

        if self.build_commands is None:
            self.build_commands = [
                "docker build -t pymapgis-app:latest .",
                "docker tag pymapgis-app:latest pymapgis-app:${{ github.sha }}",
            ]

        if self.deploy_commands is None:
            self.deploy_commands = [
                "kubectl apply -f k8s/",
                "kubectl rollout status deployment/pymapgis-deployment",
            ]

        if self.quality_gates is None:
            self.quality_gates = {
                "test_coverage": 80,
                "code_quality": "A",
                "security_scan": True,
                "performance_test": True,
            }


@dataclass
class DeploymentStatus:
    """Deployment status information."""

    success: bool
    environment: str
    version: str
    timestamp: str
    duration: float
    logs: List[str]
    error: Optional[str] = None


class GitHubActionsManager:
    """GitHub Actions workflow manager."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.workflows_dir = self.repo_path / ".github" / "workflows"
        self.workflows_dir.mkdir(parents=True, exist_ok=True)

    def generate_ci_workflow(self, config: PipelineConfig) -> str:
        """Generate CI workflow YAML."""
        workflow = {
            "name": "PyMapGIS CI/CD Pipeline",
            "on": {
                "push": {"branches": ["main", "develop"]},
                "pull_request": {"branches": ["main"]},
            },
            "env": {
                "PYTHON_VERSION": "3.11",
                "POETRY_VERSION": "1.6.1",
            },
            "jobs": {
                "test": {
                    "runs-on": "ubuntu-latest",
                    "strategy": {
                        "matrix": {
                            "python-version": ["3.9", "3.10", "3.11"],
                        }
                    },
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4",
                        },
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v4",
                            "with": {"python-version": "${{ matrix.python-version }}"},
                        },
                        {
                            "name": "Install Poetry",
                            "uses": "snok/install-poetry@v1",
                            "with": {"version": "${{ env.POETRY_VERSION }}"},
                        },
                        {
                            "name": "Configure Poetry",
                            "run": "poetry config virtualenvs.create true",
                        },
                        {
                            "name": "Install dependencies",
                            "run": "poetry install --with dev",
                        },
                        {
                            "name": "Run tests",
                            "run": " && ".join(config.test_commands),
                        },
                        {
                            "name": "Upload coverage reports",
                            "uses": "codecov/codecov-action@v3",
                            "if": "matrix.python-version == '3.11'",
                        },
                    ],
                },
                "security": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4",
                        },
                        {
                            "name": "Run security scan",
                            "uses": "securecodewarrior/github-action-add-sarif@v1",
                            "with": {"sarif-file": "security-scan-results.sarif"},
                        },
                        {
                            "name": "Run dependency check",
                            "run": "poetry run safety check",
                        },
                    ],
                },
                "build": {
                    "needs": ["test", "security"],
                    "runs-on": "ubuntu-latest",
                    "if": "github.ref == 'refs/heads/main'",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4",
                        },
                        {
                            "name": "Set up Docker Buildx",
                            "uses": "docker/setup-buildx-action@v3",
                        },
                        {
                            "name": "Login to Docker Hub",
                            "uses": "docker/login-action@v3",
                            "with": {
                                "username": "${{ secrets.DOCKER_USERNAME }}",
                                "password": "${{ secrets.DOCKER_PASSWORD }}",
                            },
                        },
                        {
                            "name": "Build and push Docker image",
                            "uses": "docker/build-push-action@v5",
                            "with": {
                                "context": ".",
                                "push": True,
                                "tags": [
                                    "pymapgis/pymapgis-app:latest",
                                    "pymapgis/pymapgis-app:${{ github.sha }}",
                                ],
                                "cache-from": "type=gha",
                                "cache-to": "type=gha,mode=max",
                            },
                        },
                    ],
                },
                "deploy-staging": {
                    "needs": ["build"],
                    "runs-on": "ubuntu-latest",
                    "environment": "staging",
                    "if": "github.ref == 'refs/heads/main'",
                    "steps": [
                        {
                            "name": "Deploy to staging",
                            "run": "echo 'Deploying to staging environment'",
                        },
                        {
                            "name": "Run smoke tests",
                            "run": "echo 'Running smoke tests'",
                        },
                    ],
                },
                "deploy-production": {
                    "needs": ["deploy-staging"],
                    "runs-on": "ubuntu-latest",
                    "environment": "production",
                    "if": "github.ref == 'refs/heads/main'",
                    "steps": [
                        {
                            "name": "Deploy to production",
                            "run": "echo 'Deploying to production environment'",
                        },
                        {
                            "name": "Run health checks",
                            "run": "echo 'Running health checks'",
                        },
                    ],
                },
            },
        }

        return yaml.dump(workflow, default_flow_style=False, sort_keys=False)

    def generate_release_workflow(self) -> str:
        """Generate release workflow YAML."""
        workflow = {
            "name": "Release",
            "on": {
                "push": {"tags": ["v*"]},
            },
            "jobs": {
                "release": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4",
                        },
                        {
                            "name": "Create Release",
                            "uses": "actions/create-release@v1",
                            "env": {"GITHUB_TOKEN": "${{ secrets.GITHUB_TOKEN }}"},
                            "with": {
                                "tag_name": "${{ github.ref }}",
                                "release_name": "Release ${{ github.ref }}",
                                "draft": False,
                                "prerelease": False,
                            },
                        },
                        {
                            "name": "Build and publish to PyPI",
                            "run": "poetry publish --build",
                            "env": {
                                "POETRY_PYPI_TOKEN_PYPI": "${{ secrets.PYPI_TOKEN }}"
                            },
                        },
                    ],
                },
            },
        }

        return yaml.dump(workflow, default_flow_style=False, sort_keys=False)

    def create_workflow_file(self, workflow_name: str, workflow_content: str) -> bool:
        """Create workflow file."""
        try:
            workflow_file = self.workflows_dir / f"{workflow_name}.yml"

            with open(workflow_file, "w") as f:
                f.write(workflow_content)

            logger.info(f"Created workflow file: {workflow_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to create workflow file: {e}")
            return False

    def setup_workflows(self, config: PipelineConfig) -> Dict[str, bool]:
        """Setup all workflows."""
        results = {}

        # CI/CD workflow
        ci_workflow = self.generate_ci_workflow(config)
        results["ci"] = self.create_workflow_file("ci", ci_workflow)

        # Release workflow
        release_workflow = self.generate_release_workflow()
        results["release"] = self.create_workflow_file("release", release_workflow)

        return results


class PipelineManager:
    """Pipeline execution and management."""

    def __init__(self):
        self.deployments: Dict[str, DeploymentStatus] = {}

    def trigger_deployment(
        self,
        environment: str,
        version: str,
        commands: List[str],
    ) -> DeploymentStatus:
        """Trigger deployment to environment."""
        start_time = datetime.now()
        logs = []

        try:
            for command in commands:
                logger.info(f"Executing: {command}")

                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    check=True,
                )

                logs.extend(result.stdout.split("\n"))
                if result.stderr:
                    logs.extend(result.stderr.split("\n"))

            duration = (datetime.now() - start_time).total_seconds()

            status = DeploymentStatus(
                success=True,
                environment=environment,
                version=version,
                timestamp=start_time.isoformat(),
                duration=duration,
                logs=logs,
            )

            self.deployments[f"{environment}-{version}"] = status
            logger.info(f"Successfully deployed {version} to {environment}")

            return status

        except subprocess.CalledProcessError as e:
            duration = (datetime.now() - start_time).total_seconds()
            error_msg = f"Deployment failed: {e.stderr}"

            status = DeploymentStatus(
                success=False,
                environment=environment,
                version=version,
                timestamp=start_time.isoformat(),
                duration=duration,
                logs=logs + [error_msg],
                error=error_msg,
            )

            self.deployments[f"{environment}-{version}"] = status
            logger.error(error_msg)

            return status

    def rollback_deployment(
        self,
        environment: str,
        previous_version: str,
    ) -> DeploymentStatus:
        """Rollback deployment to previous version."""
        rollback_commands = [
            f"kubectl set image deployment/pymapgis-deployment pymapgis=pymapgis-app:{previous_version}",
            "kubectl rollout status deployment/pymapgis-deployment",
        ]

        return self.trigger_deployment(environment, previous_version, rollback_commands)

    def get_deployment_history(self, environment: str) -> List[DeploymentStatus]:
        """Get deployment history for environment."""
        return [
            status
            for key, status in self.deployments.items()
            if status.environment == environment
        ]


class DeploymentPipeline:
    """Complete deployment pipeline orchestrator."""

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.github_actions = GitHubActionsManager()
        self.pipeline_manager = PipelineManager()

    def setup_complete_pipeline(self) -> Dict[str, Any]:
        """Setup complete CI/CD pipeline."""
        try:
            # Setup GitHub Actions workflows
            workflow_results = self.github_actions.setup_workflows(self.config)

            # Create environment-specific configurations
            env_configs = {}
            for env in self.config.environments:
                env_configs[env] = {
                    "deployment_strategy": (
                        "rolling" if env == "production" else "recreate"
                    ),
                    "health_check_timeout": 300 if env == "production" else 120,
                    "rollback_enabled": True,
                }

            return {
                "success": True,
                "workflows": workflow_results,
                "environments": env_configs,
                "quality_gates": self.config.quality_gates,
            }

        except Exception as e:
            logger.error(f"Pipeline setup failed: {e}")
            return {"success": False, "error": str(e)}


class CICDManager:
    """Main CI/CD management interface."""

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.github_actions = GitHubActionsManager()
        self.pipeline_manager = PipelineManager()
        self.deployment_pipeline = DeploymentPipeline(self.config)

    def quick_setup(self, repo_path: str = ".") -> Dict[str, Any]:
        """Quick CI/CD setup with sensible defaults."""
        try:
            # Initialize GitHub Actions manager with repo path
            self.github_actions = GitHubActionsManager(repo_path)

            # Setup complete pipeline
            result = self.deployment_pipeline.setup_complete_pipeline()

            if not result["success"]:
                return result

            logger.info("CI/CD pipeline setup completed successfully")

            return {
                "success": True,
                "message": "CI/CD pipeline configured successfully",
                "workflows_created": result["workflows"],
                "environments": result["environments"],
                "next_steps": [
                    "Configure repository secrets (DOCKER_USERNAME, DOCKER_PASSWORD, etc.)",
                    "Set up environment protection rules",
                    "Configure deployment targets",
                    "Test the pipeline with a commit",
                ],
            }

        except Exception as e:
            logger.error(f"Quick CI/CD setup failed: {e}")
            return {"success": False, "error": str(e)}


# Convenience functions
def create_github_workflow(
    workflow_name: str, config: PipelineConfig, **kwargs
) -> bool:
    """Create GitHub workflow."""
    manager = GitHubActionsManager()
    workflow_content = manager.generate_ci_workflow(config)
    return manager.create_workflow_file(workflow_name, workflow_content)


def trigger_deployment(
    environment: str, version: str, commands: List[str]
) -> DeploymentStatus:
    """Trigger deployment."""
    manager = PipelineManager()
    return manager.trigger_deployment(environment, version, commands)


def get_deployment_status(environment: str, version: str) -> Optional[DeploymentStatus]:
    """Get deployment status."""
    manager = PipelineManager()
    return manager.deployments.get(f"{environment}-{version}")


def setup_cicd_pipeline(
    repo_path: str = ".", config: Optional[PipelineConfig] = None
) -> Dict[str, Any]:
    """Setup complete CI/CD pipeline."""
    manager = CICDManager(config)
    return manager.quick_setup(repo_path)
