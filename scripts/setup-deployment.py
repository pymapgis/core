#!/usr/bin/env python3
"""
PyMapGIS Deployment Setup Script

This script helps configure deployment settings for PyMapGIS as part of
the Phase 3 Deployment Tools implementation.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional


def print_banner():
    """Print the setup banner."""
    print("🚀 PyMapGIS Deployment Setup")
    print("=" * 50)
    print("Phase 3 Deployment Tools Configuration")
    print()


def check_github_cli():
    """Check if GitHub CLI is available."""
    try:
        result = subprocess.run(["gh", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def get_registry_choice():
    """Get user's container registry choice."""
    print("📦 Container Registry Options:")
    print("1. Docker Hub (docker.io) - Most popular, requires account")
    print("2. GitHub Container Registry (ghcr.io) - Free with GitHub")
    print("3. Amazon ECR - Best for AWS deployments")
    print("4. Google Container Registry - Best for GCP deployments")
    print("5. Skip container deployment")
    print()
    
    while True:
        choice = input("Choose your container registry (1-5): ").strip()
        if choice in ["1", "2", "3", "4", "5"]:
            return choice
        print("❌ Invalid choice. Please enter 1-5.")


def setup_docker_hub():
    """Setup Docker Hub configuration."""
    print("\n🐳 Docker Hub Setup")
    print("You'll need:")
    print("1. Docker Hub account (https://hub.docker.com)")
    print("2. Access token (not password!)")
    print()
    
    username = input("Docker Hub username: ").strip()
    if not username:
        print("❌ Username is required")
        return None
        
    print("\n📝 To create an access token:")
    print("1. Go to https://hub.docker.com/settings/security")
    print("2. Click 'New Access Token'")
    print("3. Give it a name like 'PyMapGIS-CI'")
    print("4. Copy the token (you won't see it again!)")
    print()
    
    token = input("Docker Hub access token: ").strip()
    if not token:
        print("❌ Access token is required")
        return None
        
    return {
        "DOCKER_USERNAME": username,
        "DOCKER_PASSWORD": token
    }


def setup_github_registry():
    """Setup GitHub Container Registry."""
    print("\n📦 GitHub Container Registry Setup")
    print("✅ No additional configuration needed!")
    print("GitHub Container Registry uses your existing GitHub token.")
    print()
    return {}


def setup_aws_ecr():
    """Setup AWS ECR configuration."""
    print("\n☁️  AWS ECR Setup")
    print("You'll need AWS credentials with ECR permissions.")
    print()
    
    access_key = input("AWS Access Key ID: ").strip()
    secret_key = input("AWS Secret Access Key: ").strip()
    region = input("AWS Region (e.g., us-west-2): ").strip()
    account_id = input("AWS Account ID: ").strip()
    
    if not all([access_key, secret_key, region, account_id]):
        print("❌ All AWS fields are required")
        return None
        
    return {
        "AWS_ACCESS_KEY_ID": access_key,
        "AWS_SECRET_ACCESS_KEY": secret_key,
        "AWS_REGION": region,
        "AWS_ACCOUNT_ID": account_id
    }


def setup_gcp_gcr():
    """Setup Google Container Registry."""
    print("\n🌐 Google Container Registry Setup")
    print("You'll need a GCP service account key.")
    print()
    
    project_id = input("GCP Project ID: ").strip()
    key_file = input("Path to service account JSON file: ").strip()
    
    if not project_id:
        print("❌ Project ID is required")
        return None
        
    if not os.path.exists(key_file):
        print(f"❌ Service account file not found: {key_file}")
        return None
        
    with open(key_file, 'r') as f:
        service_account_key = f.read()
        
    return {
        "GCP_PROJECT_ID": project_id,
        "GCP_SERVICE_ACCOUNT_KEY": service_account_key
    }


def set_github_secrets(secrets: Dict[str, str]):
    """Set GitHub repository secrets using GitHub CLI."""
    if not check_github_cli():
        print("\n❌ GitHub CLI not found. Please install it:")
        print("https://cli.github.com/")
        return False
        
    print("\n🔐 Setting GitHub repository secrets...")
    
    for name, value in secrets.items():
        try:
            cmd = ["gh", "secret", "set", name, "--body", value]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Set secret: {name}")
            else:
                print(f"❌ Failed to set secret {name}: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error setting secret {name}: {e}")
            return False
            
    return True


def generate_env_file(secrets: Dict[str, str]):
    """Generate a .env file for local development."""
    env_file = Path(".env.deployment")
    
    with open(env_file, 'w') as f:
        f.write("# PyMapGIS Deployment Configuration\n")
        f.write("# Generated by setup-deployment.py\n\n")
        
        for name, value in secrets.items():
            # Don't write sensitive values to file
            if "PASSWORD" in name or "SECRET" in name or "KEY" in name:
                f.write(f"{name}=<REDACTED>\n")
            else:
                f.write(f"{name}={value}\n")
                
    print(f"📄 Configuration saved to: {env_file}")


def main():
    """Main setup function."""
    print_banner()
    
    choice = get_registry_choice()
    
    secrets = {}
    
    if choice == "1":
        secrets = setup_docker_hub()
    elif choice == "2":
        secrets = setup_github_registry()
    elif choice == "3":
        secrets = setup_aws_ecr()
    elif choice == "4":
        secrets = setup_gcp_gcr()
    elif choice == "5":
        print("\n⏭️  Skipping container deployment setup")
        print("You can run this script again later to configure deployment.")
        return
        
    if secrets is None:
        print("\n❌ Setup failed. Please try again.")
        return
        
    if secrets:
        print("\n🔧 Configuration Options:")
        print("1. Set GitHub repository secrets (recommended)")
        print("2. Generate local .env file only")
        print("3. Both")
        
        config_choice = input("Choose configuration method (1-3): ").strip()
        
        if config_choice in ["1", "3"]:
            if set_github_secrets(secrets):
                print("✅ GitHub secrets configured successfully!")
            else:
                print("❌ Failed to configure GitHub secrets")
                
        if config_choice in ["2", "3"]:
            generate_env_file(secrets)
            
    print("\n🎉 Deployment setup complete!")
    print("\n📖 Next steps:")
    print("1. Push your changes to trigger the CI/CD pipeline")
    print("2. Check the Actions tab for deployment status")
    print("3. Review docs/deployment/container-registry-setup.md for more options")


if __name__ == "__main__":
    main()
