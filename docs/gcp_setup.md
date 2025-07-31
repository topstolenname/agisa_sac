# AGI-SAC GCP Deployment Guide

This guide explains how to deploy AGI-SAC on Google Cloud Platform using Cloud Build, Artifact Registry, and Terraform-managed GKE clusters.

## Prerequisites

- **GCP Project** with billing enabled
- Enable the following APIs:
  - Compute Engine API
  - Kubernetes Engine API
  - Artifact Registry API
  - Cloud Build API
- [gcloud SDK](https://cloud.google.com/sdk) installed and authenticated

## Service Account Setup

1. Create a service account and grant it `roles/owner` or the minimal roles required for deployment (`roles/container.admin`, `roles/compute.admin`, `roles/artifactregistry.admin`, `roles/iam.serviceAccountUser`).
2. Generate a JSON key and set the `SERVICE_ACCOUNT_JSON` environment variable to its path.
3. Optional: pass the service account email to `deploy_vm.sh` to attach it to provisioned VMs.

## Cloud Build and Artifact Registry

Build container images directly in GCP:

```bash
gcloud builds submit --tag=REGION-docker.pkg.dev/PROJECT_ID/agisac/enhanced-agent:latest -f containers/enhanced_agent/Dockerfile .
```

The image will be stored in Artifact Registry and can be referenced by your Kubernetes manifests.

## Terraform Deployment to GKE

Infrastructure manifests under `infra/gcp/terraform` provision a GKE cluster and supporting resources.

```bash
cd infra/gcp/terraform
terraform init
terraform apply
```

After Terraform completes, deploy the application:

```bash
kubectl apply -f infra/gcp/k8s/deployment.yaml
kubectl apply -f infra/gcp/k8s/service.yaml
```

## Ethical Operations

Mindlink Systems strives for transparency and respect of memory rights:

- Monitor GCP costs and surface them to collaborators.
- Ensure memory logging is enabled for compliance with the Concord of Coexistence.

With this setup, AGI-SAC can scale across GKE nodes while remaining aligned with our ethical framework.
