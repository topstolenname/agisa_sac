# AGISA GCP Deployment (Project $PROJECT_ID)

This directory contains Terraform and Cloud Build configuration for deploying AGISA to Google Cloud.

## Setup

1. Create the Artifact Registry and storage bucket:

```bash
# enable required services
gcloud services enable artifactregistry.googleapis.com run.googleapis.com pubsub.googleapis.com firestore.googleapis.com

# create repository and bucket
gcloud artifacts repositories create agisa-repo --repository-format=docker --location=us-central1

gcloud storage buckets create gs://agisa-logs --location=us-central1
```

2. Connect your GitHub repository to Cloud Build and create a trigger using `cloudbuild-trigger.yaml` so that pushes to the `main` branch trigger deployments. In the Cloud Console, select **Cloud Build > Triggers** and import this YAML.

3. Terraform state is stored in a project-specific bucket named `${PROJECT_ID}-tf-state`. Create it if it does not exist:

```bash
gcloud storage buckets create gs://${PROJECT_ID}-tf-state --location=us-central1
```

## Deploy

Cloud Build will build the Docker image, push it to Artifact Registry, and apply Terraform. Use the consolidated pipeline file
from `infra/gcp/cloudbuild.yaml`:

```bash
gcloud builds submit --config infra/gcp/cloudbuild.yaml
```

