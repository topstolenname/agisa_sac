#!/bin/bash
# Simple script to provision a GPU VM on Google Compute Engine
# Usage: ./deploy_vm.sh <vm-name> <zone> <gpu-type> <gpu-count>
set -euo pipefail

VM_NAME=${1:-agisac-sim}
ZONE=${2:-us-central1-a}
GPU_TYPE=${3:-nvidia-tesla-t4}
GPU_COUNT=${4:-1}

# Machine type defaults to a4-highgpu-1g for A100 or n1-standard-4 for T4
if [[ $GPU_TYPE == nvidia-a100* ]]; then
    MACHINE_TYPE="a2-highgpu-1g"
else
    MACHINE_TYPE="n1-standard-4"
fi

gcloud compute instances create "$VM_NAME" \
    --zone "$ZONE" \
    --machine-type "$MACHINE_TYPE" \
    --accelerator type=$GPU_TYPE,count=$GPU_COUNT \
    --boot-disk-size 200GB \
    --maintenance-policy TERMINATE \
    --restart-on-failure

# Print connection info
echo "VM $VM_NAME created in $ZONE with $GPU_COUNT $GPU_TYPE GPU(s)."
