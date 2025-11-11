terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ═══════════════════════════════════════════════════════════
# Pub/Sub Topics for AGISA-SAC Distributed Coordination
# ═══════════════════════════════════════════════════════════

resource "google_pubsub_topic" "workspace_intentions" {
  name = "global-workspace.intentions.v1"

  message_retention_duration = "86400s" # 24 hours
}

resource "google_pubsub_topic" "handoff_offers" {
  name = "agents.handoff.offers.v1"

  message_retention_duration = "3600s" # 1 hour
}

resource "google_pubsub_topic" "handoff_claims" {
  name = "agents.handoff.claims.v1"

  message_retention_duration = "3600s"
}

resource "google_pubsub_topic" "tool_invocations" {
  name = "agents.tool.invocations.v1"

  message_retention_duration = "86400s"
}

# Legacy topics (preserved for backward compatibility)
resource "google_pubsub_topic" "agent_events" {
  name = "agent-events"
}

resource "google_pubsub_topic" "task_results" {
  name = "task-results"
}

# ═══════════════════════════════════════════════════════════
# Pub/Sub Subscriptions
# ═══════════════════════════════════════════════════════════

resource "google_pubsub_subscription" "handoff_offers_sub" {
  name  = "handoff-offers-consumer"
  topic = google_pubsub_topic.handoff_offers.name

  ack_deadline_seconds = 60

  message_retention_duration = "3600s"
  retain_acked_messages      = false

  expiration_policy {
    ttl = "" # Never expire
  }
}

# ═══════════════════════════════════════════════════════════
# Service Accounts
# ═══════════════════════════════════════════════════════════

resource "google_service_account" "agents" {
  account_id   = "agisa-agents"
  display_name = "AGISA Agent Service Account"
  description  = "Service account for agent execution with limited permissions"
}

resource "google_service_account" "orchestrator" {
  account_id   = "agisa-orchestrator"
  display_name = "AGISA Orchestration Service Account"
  description  = "Service account for topology orchestration and coordination"
}

# ═══════════════════════════════════════════════════════════
# IAM: Agents Pub/Sub Publishing
# ═══════════════════════════════════════════════════════════

resource "google_pubsub_topic_iam_member" "agents_pub_workspace" {
  topic  = google_pubsub_topic.workspace_intentions.name
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:${google_service_account.agents.email}"
}

resource "google_pubsub_topic_iam_member" "agents_pub_offers" {
  topic  = google_pubsub_topic.handoff_offers.name
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:${google_service_account.agents.email}"
}

resource "google_pubsub_topic_iam_member" "agents_pub_claims" {
  topic  = google_pubsub_topic.handoff_claims.name
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:${google_service_account.agents.email}"
}

resource "google_pubsub_topic_iam_member" "agents_pub_tools" {
  topic  = google_pubsub_topic.tool_invocations.name
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:${google_service_account.agents.email}"
}

# ═══════════════════════════════════════════════════════════
# IAM: Orchestrator Pub/Sub Subscribing
# ═══════════════════════════════════════════════════════════

resource "google_pubsub_subscription_iam_member" "orchestrator_sub_offers" {
  subscription = google_pubsub_subscription.handoff_offers_sub.name
  role         = "roles/pubsub.subscriber"
  member       = "serviceAccount:${google_service_account.orchestrator.email}"
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

# ═══════════════════════════════════════════════════════════
# GCS Buckets for Context and Topology Storage
# ═══════════════════════════════════════════════════════════

resource "google_storage_bucket" "contexts" {
  name          = "${var.project_id}-agisa-sac-contexts"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 7 # days
    }
    action {
      type = "Delete"
    }
  }
}

resource "google_storage_bucket" "topology" {
  name          = "${var.project_id}-agisa-sac-topology"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}

resource "google_storage_bucket" "metrics" {
  name          = "${var.project_id}-agisa-sac-metrics"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true
}

# ═══════════════════════════════════════════════════════════
# GCS IAM Permissions
# ═══════════════════════════════════════════════════════════

resource "google_storage_bucket_iam_member" "agents_contexts_write" {
  bucket = google_storage_bucket.contexts.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${google_service_account.agents.email}"
}

resource "google_storage_bucket_iam_member" "orchestrator_contexts_read" {
  bucket = google_storage_bucket.contexts.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.orchestrator.email}"
}

resource "google_storage_bucket_iam_member" "orchestrator_topology_write" {
  bucket = google_storage_bucket.topology.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.orchestrator.email}"
}

# ═══════════════════════════════════════════════════════════
# Firestore (Note: Must be enabled manually via console)
# After enabling, create composite indexes as needed
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# Variables
# ═══════════════════════════════════════════════════════════

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "source_bucket" {
  description = "GCS bucket for function source code"
  type        = string
}

# ═══════════════════════════════════════════════════════════
# Outputs
# ═══════════════════════════════════════════════════════════

output "workspace_topic" {
  description = "Global workspace intentions topic"
  value       = google_pubsub_topic.workspace_intentions.name
}

output "handoff_offers_topic" {
  description = "Handoff offers topic"
  value       = google_pubsub_topic.handoff_offers.name
}

output "agents_sa_email" {
  description = "Agents service account email"
  value       = google_service_account.agents.email
}

output "orchestrator_sa_email" {
  description = "Orchestrator service account email"
  value       = google_service_account.orchestrator.email
}

output "contexts_bucket" {
  description = "Context storage bucket"
  value       = google_storage_bucket.contexts.name
}

output "topology_bucket" {
  description = "Topology data bucket"
  value       = google_storage_bucket.topology.name
}
