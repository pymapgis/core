# Container Registry Setup Guide

This guide helps you configure PyMapGIS for deployment to various container registries as part of our Phase 3 Deployment Tools implementation.

## Quick Fix for Current Issue

The current CI/CD pipeline failure is due to missing Docker Hub credentials. Here are your options:

### Option 1: Skip Container Push (Recommended for Development)
The updated CI/CD pipeline now automatically detects missing credentials and builds images locally without pushing. No action needed!

### Option 2: Configure Docker Hub (Recommended for Production)
1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Add these secrets:
   - `DOCKER_USERNAME`: Your Docker Hub username
   - `DOCKER_PASSWORD`: Your Docker Hub access token (not password!)

### Option 3: Use GitHub Container Registry (Free Alternative)
No additional secrets needed! The pipeline can automatically use GHCR with existing GitHub tokens.

## Supported Container Registries

### 1. Docker Hub (docker.io)
**Best for**: Public projects, easy setup
**Required Secrets**:
```
DOCKER_USERNAME=your-dockerhub-username
DOCKER_PASSWORD=your-dockerhub-token
```

### 2. GitHub Container Registry (ghcr.io)
**Best for**: GitHub-hosted projects, free private registries
**Required Secrets**: None (uses GITHUB_TOKEN automatically)

### 3. Amazon ECR
**Best for**: AWS-based deployments
**Required Secrets**:
```
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-west-2
AWS_ACCOUNT_ID=123456789012
```

### 4. Google Container Registry (gcr.io)
**Best for**: GCP-based deployments
**Required Secrets**:
```
GCP_SERVICE_ACCOUNT_KEY=your-service-account-json
GCP_PROJECT_ID=your-gcp-project-id
```

## Usage Examples

### Using the Multi-Registry Workflow

```yaml
# In your workflow file
- name: Deploy to Docker Hub
  uses: ./.github/workflows/docker-deploy.yml
  with:
    registry: 'dockerhub'
    environment: 'production'
  secrets:
    DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
    DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}

- name: Deploy to GitHub Container Registry
  uses: ./.github/workflows/docker-deploy.yml
  with:
    registry: 'ghcr'
    environment: 'staging'

- name: Deploy to AWS ECR
  uses: ./.github/workflows/docker-deploy.yml
  with:
    registry: 'ecr'
    environment: 'production'
  secrets:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## Security Best Practices

1. **Use Access Tokens**: Never use passwords directly
2. **Least Privilege**: Grant minimal required permissions
3. **Rotate Regularly**: Update tokens/keys periodically
4. **Environment Separation**: Use different credentials for staging/production

## Troubleshooting

### "Username and password required" Error
- Check that secrets are properly configured in GitHub repository settings
- Verify secret names match exactly (case-sensitive)
- Ensure tokens have push permissions to the registry

### ECR Authentication Issues
- Verify AWS credentials have ECR permissions
- Check that the ECR repository exists
- Ensure the AWS region is correct

### Build Failures
- Check Dockerfile syntax
- Verify all required files are included in build context
- Review build logs for specific error messages

## Phase 3 Deployment Tools Roadmap

This container registry setup is part of our comprehensive Phase 3 Deployment Tools implementation:

- ✅ **Multi-Registry Support**: Docker Hub, ECR, GCR, GHCR
- ✅ **Automated Security Scanning**: Trivy integration
- ✅ **Flexible Authentication**: Multiple auth methods
- 🔄 **Coming Next**: Kubernetes deployment templates
- 🔄 **Coming Next**: Cloud infrastructure templates
- 🔄 **Coming Next**: Automated rollback mechanisms

## Getting Help

If you encounter issues:
1. Check the [GitHub Actions logs](../../actions) for detailed error messages
2. Review this documentation for configuration requirements
3. Open an issue with the specific error message and configuration details
