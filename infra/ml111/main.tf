terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.0"
    }
  }
  backend "gcs" {
    bucket = "PROJECT_ID-tf-state"
    prefix = "agisa"
  }
}

locals {
  agent_image = coalesce(var.agent_image, "us-central1-docker.pkg.dev/${var.project_id}/agisa-repo/agent:latest")
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_artifact_registry_repository" "agisa_repo" {
  location      = var.region
  repository_id = "agisa-repo"
  description   = "AGISA container repository"
  format        = "DOCKER"
}

resource "google_cloud_run_service" "agisa_transmitter" {
  name     = "agisa-transmitter"
  location = var.region
  template {
    spec {
      containers {
        image = local.agent_image
        ports {
          container_port = 8765
        }
      }
    }
  }
}

resource "google_cloud_run_service" "agisa_receiver" {
  name     = "agisa-receiver"
  location = var.region
  template {
    spec {
      containers {
        image = local.agent_image
        ports {
          container_port = 8765
        }
      }
    }
  }
}

resource "google_pubsub_topic" "messages" {
  name = "agisa-messages"
}

resource "google_pubsub_topic" "logs" {
  name = "agisa-logs"
}

resource "google_firestore_database" "default" {
  name       = "(default)"
  location_id = var.region
  type       = "NATIVE"
}

resource "google_storage_bucket" "logs_bucket" {
  name     = var.logs_bucket
  location = var.region
  uniform_bucket_level_access = true
}

