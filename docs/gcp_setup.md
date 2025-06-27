# GCP Setup

This document outlines basic steps to run AGI-SAC in Google Cloud.

1. **Provision a GPU VM**
   ```bash
   infra/gcp/deploy_vm.sh my-sim us-central1-a nvidia-tesla-t4 1
   ```
2. **Build Docker image**
   ```bash
   docker build -t gcr.io/PROJECT_ID/agisac:latest -f containers/enhanced_agent/Dockerfile .
   ```
3. **Deploy to GKE**
   ```bash
   kubectl apply -f infra/gcp/k8s/deployment.yaml
   kubectl apply -f infra/gcp/k8s/service.yaml
   ```

Functions for scroll export and time pulses are located in the `functions` directory.
