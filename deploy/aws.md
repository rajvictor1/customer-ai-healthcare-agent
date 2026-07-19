# Deploy to AWS

## ECS Fargate (recommended)

1. Build and push the Docker image to Amazon ECR:
   ```bash
   aws ecr get-login-password | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$(aws configure get region).amazonaws.com
   docker build -t customer-ai-healthcare-agent .
   docker tag customer-ai-healthcare-agent:latest $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$(aws configure get region).amazonaws.com/customer-ai-healthcare-agent:latest
   docker push $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$(aws configure get region).amazonaws.com/customer-ai-healthcare-agent:latest
   ```

2. Create an ECS Fargate service with:
   - Task role with least privilege
   - Secrets stored in AWS Secrets Manager, referenced by the task definition
   - Application Load Balancer for HTTPS
   - RDS PostgreSQL for persistence (do not use SQLite in production)
   - ElastiCache Redis if session state is needed beyond RDS

3. Set environment variables via the task definition, pulling secrets from Secrets Manager.

## Compliance note

For healthcare deployments, ensure a signed HIPAA Business Associate Agreement (BAA) with AWS and any PHI-handling services before enabling real EHR integrations.
