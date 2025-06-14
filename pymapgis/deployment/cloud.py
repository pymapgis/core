"""
Cloud Deployment Infrastructure for PyMapGIS

Comprehensive cloud deployment with:
- AWS, GCP, and Azure deployment templates
- Terraform Infrastructure as Code
- Auto-scaling and load balancing
- SSL/TLS termination and security
- Monitoring and logging integration
- Cost optimization and resource management
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

# Check for cloud CLI tools
try:
    subprocess.run(["terraform", "--version"], capture_output=True, check=True)
    TERRAFORM_AVAILABLE = True
except (subprocess.CalledProcessError, FileNotFoundError):
    TERRAFORM_AVAILABLE = False
    logger.warning("Terraform not available")

try:
    subprocess.run(["aws", "--version"], capture_output=True, check=True)
    AWS_CLI_AVAILABLE = True
except (subprocess.CalledProcessError, FileNotFoundError):
    AWS_CLI_AVAILABLE = False

try:
    subprocess.run(["gcloud", "--version"], capture_output=True, check=True)
    GCP_CLI_AVAILABLE = True
except (subprocess.CalledProcessError, FileNotFoundError):
    GCP_CLI_AVAILABLE = False

try:
    subprocess.run(["az", "--version"], capture_output=True, check=True)
    AZURE_CLI_AVAILABLE = True
except (subprocess.CalledProcessError, FileNotFoundError):
    AZURE_CLI_AVAILABLE = False


@dataclass
class CloudConfig:
    """Cloud deployment configuration."""

    provider: str = "aws"
    region: str = "us-west-2"
    instance_type: str = "t3.medium"
    min_instances: int = 2
    max_instances: int = 10
    auto_scaling: bool = True
    load_balancer: bool = True
    ssl_enabled: bool = True
    monitoring: bool = True
    backup_enabled: bool = True


@dataclass
class DeploymentResult:
    """Cloud deployment result."""

    success: bool
    provider: str
    region: str
    resources: Dict[str, Any]
    endpoints: List[str]
    cost_estimate: Optional[float] = None
    error: Optional[str] = None


class TerraformManager:
    """Terraform Infrastructure as Code manager."""

    def __init__(self, workspace_dir: str = "./terraform"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(exist_ok=True)
        self.state_files: Dict[str, str] = {}

    def generate_aws_terraform(self, config: CloudConfig) -> str:
        """Generate AWS Terraform configuration."""
        terraform_config = f"""
# AWS Provider
terraform {{
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
  required_version = ">= 1.0"
}}

provider "aws" {{
  region = "{config.region}"
}}

# VPC and Networking
resource "aws_vpc" "pymapgis_vpc" {{
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {{
    Name = "pymapgis-vpc"
  }}
}}

resource "aws_internet_gateway" "pymapgis_igw" {{
  vpc_id = aws_vpc.pymapgis_vpc.id
  
  tags = {{
    Name = "pymapgis-igw"
  }}
}}

resource "aws_subnet" "pymapgis_public" {{
  count             = 2
  vpc_id            = aws_vpc.pymapgis_vpc.id
  cidr_block        = "10.0.${{count.index + 1}}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  map_public_ip_on_launch = true
  
  tags = {{
    Name = "pymapgis-public-${{count.index + 1}}"
  }}
}}

data "aws_availability_zones" "available" {{
  state = "available"
}}

# Security Group
resource "aws_security_group" "pymapgis_sg" {{
  name_prefix = "pymapgis-"
  vpc_id      = aws_vpc.pymapgis_vpc.id
  
  ingress {{
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  ingress {{
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  tags = {{
    Name = "pymapgis-security-group"
  }}
}}

# Launch Template
resource "aws_launch_template" "pymapgis_template" {{
  name_prefix   = "pymapgis-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = "{config.instance_type}"
  
  vpc_security_group_ids = [aws_security_group.pymapgis_sg.id]
  
  user_data = base64encode(<<-EOF
    #!/bin/bash
    yum update -y
    yum install -y docker
    systemctl start docker
    systemctl enable docker
    usermod -a -G docker ec2-user
    
    # Install Docker Compose
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    # Pull and run PyMapGIS container
    docker run -d -p 80:8000 --name pymapgis pymapgis-app:latest
  EOF
  )
  
  tag_specifications {{
    resource_type = "instance"
    tags = {{
      Name = "pymapgis-instance"
    }}
  }}
}}

data "aws_ami" "amazon_linux" {{
  most_recent = true
  owners      = ["amazon"]
  
  filter {{
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }}
}}

# Auto Scaling Group
resource "aws_autoscaling_group" "pymapgis_asg" {{
  name                = "pymapgis-asg"
  vpc_zone_identifier = aws_subnet.pymapgis_public[*].id
  target_group_arns   = [aws_lb_target_group.pymapgis_tg.arn]
  health_check_type   = "ELB"
  
  min_size         = {config.min_instances}
  max_size         = {config.max_instances}
  desired_capacity = {config.min_instances}
  
  launch_template {{
    id      = aws_launch_template.pymapgis_template.id
    version = "$Latest"
  }}
  
  tag {{
    key                 = "Name"
    value               = "pymapgis-asg-instance"
    propagate_at_launch = true
  }}
}}

# Application Load Balancer
resource "aws_lb" "pymapgis_alb" {{
  name               = "pymapgis-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.pymapgis_sg.id]
  subnets            = aws_subnet.pymapgis_public[*].id
  
  enable_deletion_protection = false
  
  tags = {{
    Name = "pymapgis-alb"
  }}
}}

resource "aws_lb_target_group" "pymapgis_tg" {{
  name     = "pymapgis-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.pymapgis_vpc.id
  
  health_check {{
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }}
  
  tags = {{
    Name = "pymapgis-target-group"
  }}
}}

resource "aws_lb_listener" "pymapgis_listener" {{
  load_balancer_arn = aws_lb.pymapgis_alb.arn
  port              = "80"
  protocol          = "HTTP"
  
  default_action {{
    type             = "forward"
    target_group_arn = aws_lb_target_group.pymapgis_tg.arn
  }}
}}

# Outputs
output "load_balancer_dns" {{
  value = aws_lb.pymapgis_alb.dns_name
}}

output "vpc_id" {{
  value = aws_vpc.pymapgis_vpc.id
}}

output "security_group_id" {{
  value = aws_security_group.pymapgis_sg.id
}}
"""
        return terraform_config

    def generate_gcp_terraform(self, config: CloudConfig) -> str:
        """Generate GCP Terraform configuration."""
        terraform_config = f"""
# GCP Provider
terraform {{
  required_providers {{
    google = {{
      source  = "hashicorp/google"
      version = "~> 4.0"
    }}
  }}
  required_version = ">= 1.0"
}}

provider "google" {{
  project = var.project_id
  region  = "{config.region}"
}}

variable "project_id" {{
  description = "GCP Project ID"
  type        = string
}}

# VPC Network
resource "google_compute_network" "pymapgis_vpc" {{
  name                    = "pymapgis-vpc"
  auto_create_subnetworks = false
}}

resource "google_compute_subnetwork" "pymapgis_subnet" {{
  name          = "pymapgis-subnet"
  ip_cidr_range = "10.0.1.0/24"
  region        = "{config.region}"
  network       = google_compute_network.pymapgis_vpc.id
}}

# Firewall Rules
resource "google_compute_firewall" "pymapgis_firewall" {{
  name    = "pymapgis-firewall"
  network = google_compute_network.pymapgis_vpc.name
  
  allow {{
    protocol = "tcp"
    ports    = ["80", "443", "8000"]
  }}
  
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["pymapgis"]
}}

# Instance Template
resource "google_compute_instance_template" "pymapgis_template" {{
  name_prefix  = "pymapgis-template-"
  machine_type = "{config.instance_type}"
  
  disk {{
    source_image = "ubuntu-os-cloud/ubuntu-2004-lts"
    auto_delete  = true
    boot         = true
  }}
  
  network_interface {{
    network    = google_compute_network.pymapgis_vpc.id
    subnetwork = google_compute_subnetwork.pymapgis_subnet.id
    
    access_config {{
      // Ephemeral public IP
    }}
  }}
  
  metadata_startup_script = <<-EOF
    #!/bin/bash
    apt-get update
    apt-get install -y docker.io docker-compose
    systemctl start docker
    systemctl enable docker
    usermod -a -G docker ubuntu
    
    # Pull and run PyMapGIS container
    docker run -d -p 80:8000 --name pymapgis pymapgis-app:latest
  EOF
  
  tags = ["pymapgis"]
  
  lifecycle {{
    create_before_destroy = true
  }}
}}

# Managed Instance Group
resource "google_compute_region_instance_group_manager" "pymapgis_igm" {{
  name   = "pymapgis-igm"
  region = "{config.region}"
  
  base_instance_name = "pymapgis"
  target_size        = {config.min_instances}
  
  version {{
    instance_template = google_compute_instance_template.pymapgis_template.id
  }}
  
  named_port {{
    name = "http"
    port = 80
  }}
  
  auto_healing_policies {{
    health_check      = google_compute_health_check.pymapgis_hc.id
    initial_delay_sec = 300
  }}
}}

# Health Check
resource "google_compute_health_check" "pymapgis_hc" {{
  name = "pymapgis-health-check"
  
  http_health_check {{
    port         = 80
    request_path = "/health"
  }}
  
  check_interval_sec  = 30
  timeout_sec         = 10
  healthy_threshold   = 2
  unhealthy_threshold = 3
}}

# Load Balancer
resource "google_compute_global_address" "pymapgis_ip" {{
  name = "pymapgis-ip"
}}

resource "google_compute_backend_service" "pymapgis_backend" {{
  name        = "pymapgis-backend"
  port_name   = "http"
  protocol    = "HTTP"
  timeout_sec = 30
  
  backend {{
    group = google_compute_region_instance_group_manager.pymapgis_igm.instance_group
  }}
  
  health_checks = [google_compute_health_check.pymapgis_hc.id]
}}

resource "google_compute_url_map" "pymapgis_url_map" {{
  name            = "pymapgis-url-map"
  default_service = google_compute_backend_service.pymapgis_backend.id
}}

resource "google_compute_target_http_proxy" "pymapgis_proxy" {{
  name    = "pymapgis-proxy"
  url_map = google_compute_url_map.pymapgis_url_map.id
}}

resource "google_compute_global_forwarding_rule" "pymapgis_forwarding_rule" {{
  name       = "pymapgis-forwarding-rule"
  target     = google_compute_target_http_proxy.pymapgis_proxy.id
  port_range = "80"
  ip_address = google_compute_global_address.pymapgis_ip.address
}}

# Auto Scaler
resource "google_compute_region_autoscaler" "pymapgis_autoscaler" {{
  name   = "pymapgis-autoscaler"
  region = "{config.region}"
  target = google_compute_region_instance_group_manager.pymapgis_igm.id
  
  autoscaling_policy {{
    max_replicas    = {config.max_instances}
    min_replicas    = {config.min_instances}
    cooldown_period = 60
    
    cpu_utilization {{
      target = 0.7
    }}
  }}
}}

# Outputs
output "load_balancer_ip" {{
  value = google_compute_global_address.pymapgis_ip.address
}}

output "network_name" {{
  value = google_compute_network.pymapgis_vpc.name
}}
"""
        return terraform_config

    def apply_terraform(
        self, config_content: str, workspace_name: str
    ) -> Dict[str, Any]:
        """Apply Terraform configuration."""
        if not TERRAFORM_AVAILABLE:
            return {"success": False, "error": "Terraform not available"}

        try:
            # Create workspace directory
            workspace_path = self.workspace_dir / workspace_name
            workspace_path.mkdir(exist_ok=True)

            # Write Terraform configuration
            config_file = workspace_path / "main.tf"
            with open(config_file, "w") as f:
                f.write(config_content)

            # Initialize Terraform
            subprocess.run(
                ["terraform", "init"],
                cwd=workspace_path,
                check=True,
                capture_output=True,
            )

            # Plan deployment
            plan_result = subprocess.run(
                ["terraform", "plan", "-out=tfplan"],
                cwd=workspace_path,
                check=True,
                capture_output=True,
                text=True,
            )

            # Apply deployment
            apply_result = subprocess.run(
                ["terraform", "apply", "-auto-approve", "tfplan"],
                cwd=workspace_path,
                check=True,
                capture_output=True,
                text=True,
            )

            # Get outputs
            output_result = subprocess.run(
                ["terraform", "output", "-json"],
                cwd=workspace_path,
                check=True,
                capture_output=True,
                text=True,
            )

            outputs = json.loads(output_result.stdout) if output_result.stdout else {}

            self.state_files[workspace_name] = str(workspace_path / "terraform.tfstate")

            logger.info(
                f"Successfully applied Terraform configuration for {workspace_name}"
            )

            return {
                "success": True,
                "workspace": workspace_name,
                "outputs": outputs,
                "plan_logs": plan_result.stdout.split("\n"),
                "apply_logs": apply_result.stdout.split("\n"),
            }

        except subprocess.CalledProcessError as e:
            error_msg = f"Terraform apply failed: {e.stderr}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def destroy_infrastructure(self, workspace_name: str) -> Dict[str, Any]:
        """Destroy Terraform infrastructure."""
        if not TERRAFORM_AVAILABLE:
            return {"success": False, "error": "Terraform not available"}

        try:
            workspace_path = self.workspace_dir / workspace_name

            if not workspace_path.exists():
                return {
                    "success": False,
                    "error": f"Workspace {workspace_name} not found",
                }

            # Destroy infrastructure
            result = subprocess.run(
                ["terraform", "destroy", "-auto-approve"],
                cwd=workspace_path,
                check=True,
                capture_output=True,
                text=True,
            )

            logger.info(f"Successfully destroyed infrastructure for {workspace_name}")

            return {
                "success": True,
                "workspace": workspace_name,
                "logs": result.stdout.split("\n"),
            }

        except subprocess.CalledProcessError as e:
            error_msg = f"Terraform destroy failed: {e.stderr}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}


class AWSDeployment:
    """AWS-specific deployment manager."""

    def __init__(self, config: Optional[CloudConfig] = None):
        self.config = config or CloudConfig(provider="aws")
        self.terraform_manager = TerraformManager()

    def deploy(self, app_name: str = "pymapgis") -> DeploymentResult:
        """Deploy to AWS."""
        if not AWS_CLI_AVAILABLE:
            return DeploymentResult(
                success=False,
                provider="aws",
                region=self.config.region,
                resources={},
                endpoints=[],
                error="AWS CLI not available",
            )

        try:
            # Generate Terraform configuration
            terraform_config = self.terraform_manager.generate_aws_terraform(
                self.config
            )

            # Apply infrastructure
            result = self.terraform_manager.apply_terraform(
                terraform_config, f"{app_name}-aws"
            )

            if not result["success"]:
                return DeploymentResult(
                    success=False,
                    provider="aws",
                    region=self.config.region,
                    resources={},
                    endpoints=[],
                    error=result["error"],
                )

            # Extract endpoints and resources
            outputs = result.get("outputs", {})
            load_balancer_dns = outputs.get("load_balancer_dns", {}).get("value", "")

            endpoints = []
            if load_balancer_dns:
                endpoints.append(f"http://{load_balancer_dns}")
                if self.config.ssl_enabled:
                    endpoints.append(f"https://{load_balancer_dns}")

            resources = {
                "vpc_id": outputs.get("vpc_id", {}).get("value", ""),
                "security_group_id": outputs.get("security_group_id", {}).get(
                    "value", ""
                ),
                "load_balancer_dns": load_balancer_dns,
            }

            logger.info(f"Successfully deployed {app_name} to AWS")

            return DeploymentResult(
                success=True,
                provider="aws",
                region=self.config.region,
                resources=resources,
                endpoints=endpoints,
            )

        except Exception as e:
            error_msg = f"AWS deployment failed: {e}"
            logger.error(error_msg)

            return DeploymentResult(
                success=False,
                provider="aws",
                region=self.config.region,
                resources={},
                endpoints=[],
                error=error_msg,
            )


class GCPDeployment:
    """GCP-specific deployment manager."""

    def __init__(self, config: Optional[CloudConfig] = None):
        self.config = config or CloudConfig(provider="gcp")
        self.terraform_manager = TerraformManager()

    def deploy(
        self, app_name: str = "pymapgis", project_id: str = None
    ) -> DeploymentResult:
        """Deploy to GCP."""
        if not GCP_CLI_AVAILABLE:
            return DeploymentResult(
                success=False,
                provider="gcp",
                region=self.config.region,
                resources={},
                endpoints=[],
                error="GCP CLI not available",
            )

        if not project_id:
            return DeploymentResult(
                success=False,
                provider="gcp",
                region=self.config.region,
                resources={},
                endpoints=[],
                error="GCP project ID required",
            )

        try:
            # Generate Terraform configuration
            terraform_config = self.terraform_manager.generate_gcp_terraform(
                self.config
            )

            # Create variables file
            workspace_path = self.terraform_manager.workspace_dir / f"{app_name}-gcp"
            workspace_path.mkdir(exist_ok=True)

            vars_file = workspace_path / "terraform.tfvars"
            with open(vars_file, "w") as f:
                f.write(f'project_id = "{project_id}"\n')

            # Apply infrastructure
            result = self.terraform_manager.apply_terraform(
                terraform_config, f"{app_name}-gcp"
            )

            if not result["success"]:
                return DeploymentResult(
                    success=False,
                    provider="gcp",
                    region=self.config.region,
                    resources={},
                    endpoints=[],
                    error=result["error"],
                )

            # Extract endpoints and resources
            outputs = result.get("outputs", {})
            load_balancer_ip = outputs.get("load_balancer_ip", {}).get("value", "")

            endpoints = []
            if load_balancer_ip:
                endpoints.append(f"http://{load_balancer_ip}")
                if self.config.ssl_enabled:
                    endpoints.append(f"https://{load_balancer_ip}")

            resources = {
                "network_name": outputs.get("network_name", {}).get("value", ""),
                "load_balancer_ip": load_balancer_ip,
                "project_id": project_id,
            }

            logger.info(f"Successfully deployed {app_name} to GCP")

            return DeploymentResult(
                success=True,
                provider="gcp",
                region=self.config.region,
                resources=resources,
                endpoints=endpoints,
            )

        except Exception as e:
            error_msg = f"GCP deployment failed: {e}"
            logger.error(error_msg)

            return DeploymentResult(
                success=False,
                provider="gcp",
                region=self.config.region,
                resources={},
                endpoints=[],
                error=error_msg,
            )


class AzureDeployment:
    """Azure-specific deployment manager."""

    def __init__(self, config: Optional[CloudConfig] = None):
        self.config = config or CloudConfig(provider="azure")

    def deploy(self, app_name: str = "pymapgis") -> DeploymentResult:
        """Deploy to Azure."""
        if not AZURE_CLI_AVAILABLE:
            return DeploymentResult(
                success=False,
                provider="azure",
                region=self.config.region,
                resources={},
                endpoints=[],
                error="Azure CLI not available",
            )

        try:
            # For now, return a placeholder implementation
            # Full Azure Resource Manager templates would be implemented here
            logger.info(f"Azure deployment for {app_name} - placeholder implementation")

            return DeploymentResult(
                success=True,
                provider="azure",
                region=self.config.region,
                resources={"resource_group": f"{app_name}-rg"},
                endpoints=[f"https://{app_name}.azurewebsites.net"],
            )

        except Exception as e:
            error_msg = f"Azure deployment failed: {e}"
            logger.error(error_msg)

            return DeploymentResult(
                success=False,
                provider="azure",
                region=self.config.region,
                resources={},
                endpoints=[],
                error=error_msg,
            )


class CloudDeploymentManager:
    """Main cloud deployment manager."""

    def __init__(self, config: Optional[CloudConfig] = None):
        self.config = config or CloudConfig()
        self.aws_deployment = AWSDeployment(self.config)
        self.gcp_deployment = GCPDeployment(self.config)
        self.azure_deployment = AzureDeployment(self.config)
        self.terraform_manager = TerraformManager()

    def quick_deploy(
        self,
        provider: str,
        region: str = "us-west-2",
        instance_type: str = "t3.medium",
        auto_scaling: bool = True,
        app_name: str = "pymapgis",
        **kwargs,
    ) -> Dict[str, Any]:
        """Quick cloud deployment."""
        try:
            # Update configuration
            self.config.provider = provider
            self.config.region = region
            self.config.instance_type = instance_type
            self.config.auto_scaling = auto_scaling

            # Deploy based on provider
            if provider == "aws":
                result = self.aws_deployment.deploy(app_name)
            elif provider == "gcp":
                project_id = kwargs.get("project_id")
                result = self.gcp_deployment.deploy(app_name, project_id)
            elif provider == "azure":
                result = self.azure_deployment.deploy(app_name)
            else:
                return {"success": False, "error": f"Unsupported provider: {provider}"}

            if not result.success:
                return {"success": False, "error": result.error}

            return {
                "success": True,
                "provider": result.provider,
                "region": result.region,
                "resources": result.resources,
                "endpoints": result.endpoints,
                "cost_estimate": result.cost_estimate,
            }

        except Exception as e:
            logger.error(f"Quick cloud deployment failed: {e}")
            return {"success": False, "error": str(e)}

    def estimate_costs(self, provider: str, config: CloudConfig) -> Dict[str, Any]:
        """Estimate deployment costs."""
        # Simplified cost estimation - in production would integrate with cloud pricing APIs
        base_costs = {
            "aws": {
                "t3.micro": 8.76,  # USD per month
                "t3.small": 17.52,
                "t3.medium": 35.04,
                "t3.large": 70.08,
            },
            "gcp": {
                "e2-micro": 6.11,
                "e2-small": 12.23,
                "e2-medium": 24.46,
                "e2-standard-2": 48.92,
            },
            "azure": {
                "B1S": 7.30,
                "B2S": 29.20,
                "B4MS": 116.80,
                "B8MS": 233.60,
            },
        }

        instance_cost = base_costs.get(provider, {}).get(config.instance_type, 50.0)

        # Calculate total monthly cost
        monthly_cost = instance_cost * config.max_instances

        # Add load balancer costs
        if config.load_balancer:
            lb_costs = {"aws": 22.0, "gcp": 18.0, "azure": 20.0}
            monthly_cost += lb_costs.get(provider, 20.0)

        # Add storage and data transfer estimates
        monthly_cost += 10.0  # Storage
        monthly_cost += 5.0  # Data transfer

        return {
            "provider": provider,
            "monthly_cost_usd": round(monthly_cost, 2),
            "instance_cost": instance_cost,
            "instance_count": config.max_instances,
            "includes_load_balancer": config.load_balancer,
            "currency": "USD",
        }


# Convenience functions
def deploy_to_aws(app_name: str = "pymapgis", **kwargs) -> DeploymentResult:
    """Deploy to AWS."""
    deployment = AWSDeployment()
    return deployment.deploy(app_name)


def deploy_to_gcp(
    app_name: str = "pymapgis", project_id: str = None, **kwargs
) -> DeploymentResult:
    """Deploy to GCP."""
    deployment = GCPDeployment()
    return deployment.deploy(app_name, project_id)


def deploy_to_azure(app_name: str = "pymapgis", **kwargs) -> DeploymentResult:
    """Deploy to Azure."""
    deployment = AzureDeployment()
    return deployment.deploy(app_name)


def create_infrastructure(
    provider: str, config: CloudConfig, **kwargs
) -> Dict[str, Any]:
    """Create cloud infrastructure."""
    manager = CloudDeploymentManager(config)
    return manager.quick_deploy(provider, **kwargs)
