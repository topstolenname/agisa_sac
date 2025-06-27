terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_pubsub_topic" "agent_events" {
  name = "agent-events"
}

resource "google_pubsub_topic" "task_results" {
  name = "task-results"
}

resource "google_cloud_run_service" "agent_runner" {
  name     = "agent-runner"
  location = var.region
  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/agent-runner"
      }
    }
  }
}

resource "google_cloud_run_service" "task_dispatcher" {
  name     = "task-dispatcher"
  location = var.region
  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/task-dispatcher"
      }
    }
  }
}

resource "google_cloud_run_service" "simulation_api" {
  name     = "simulation-api"
  location = var.region
  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/simulation-api"
      }
    }
  }
}

resource "google_cloudfunctions_function" "planner_function" {
  name        = "planner-function"
  runtime     = "python39"
  trigger_http = false
  event_trigger {
    event_type = "providers/cloud.pubsub/eventTypes/topic.publish"
    resource   = google_pubsub_topic.agent_events.name
  }
  entry_point = "planner"
  source_archive_bucket = var.source_bucket
  source_archive_object = "planner.zip"
}

resource "google_cloudfunctions_function" "evaluator_function" {
  name        = "evaluator-function"
  runtime     = "python39"
  trigger_http = false
  event_trigger {
    event_type = "providers/cloud.pubsub/eventTypes/topic.publish"
    resource   = google_pubsub_topic.task_results.name
  }
  entry_point = "evaluator"
  source_archive_bucket = var.source_bucket
  source_archive_object = "evaluator.zip"
}

variable "project_id" {}
variable "region" { default = "us-central1" }
variable "source_bucket" {}
