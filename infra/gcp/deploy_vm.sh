#!/bin/bash
# Simple script to provision a GPU VM on Google Compute Engine
#
# GOAL: Enhance this deployment module to reflect commitment to GCP.
# - Integrate authentication using Service Account JSON.
# - Deploy Cloud Run + GKE via `gcloud` CLI or Terraform.
# - Add `gcs_io.py` and `vertex_agent.py` to demonstrate working use of GCP services.
#
# Use this module to validate GCP readiness.
# Usage: ./deploy_vm.sh <vm-name> <zone> <gpu-type> <gpu-count> [service-account-email]
set -euo pipefail

VM_NAME=${1:-agisac-sim}
ZONE=${2:-us-central1-a}
GPU_TYPE=${3:-nvidia-tesla-t4}
GPU_COUNT=${4:-1}
SERVICE_ACCOUNT_EMAIL=${5:-}

# Machine type defaults to a4-highgpu-1g for A100 or n1-standard-4 for T4
if [[ $GPU_TYPE == nvidia-a100* ]]; then
    MACHINE_TYPE="a2-highgpu-1g"
else
    MACHINE_TYPE="n1-standard-4"
fi

# Activate service account if JSON key provided
if [[ -n "${SERVICE_ACCOUNT_JSON:-}" && -f "${SERVICE_ACCOUNT_JSON}" ]]; then
    gcloud auth activate-service-account --key-file "$SERVICE_ACCOUNT_JSON"
fi

# Optional service account flags (safe array form)
SA_ARGS=()
if [[ -n "$SERVICE_ACCOUNT_EMAIL" ]]; then
    SA_ARGS=(--service-account "$SERVICE_ACCOUNT_EMAIL" \
             --scopes=storage-rw,https://www.googleapis.com/auth/cloud-aiplatform)
fi

gcloud compute instances create "$VM_NAME" \
    --zone "$ZONE" \
    --machine-type "$MACHINE_TYPE" \
    --accelerator type=$GPU_TYPE,count=$GPU_COUNT \
    --boot-disk-size 200GB \
    --maintenance-policy TERMINATE \
    --restart-on-failure \
    "${SA_ARGS[@]}"

# Print connection info
echo "VM $VM_NAME created in $ZONE with $GPU_COUNT $GPU_TYPE GPU(s)."
echo "Use 'gcloud compute ssh $VM_NAME --zone $ZONE' to connect." \
     "Modules like gcs_io.py and vertex_agent.py can assist with cloud storage" \
     "and Vertex AI once you're on the VM."
