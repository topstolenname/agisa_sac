variable "project_id" {
  description = "GCP project ID for deployment"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "agent_image" {
  description = "Container image for AGISA services"
  type        = string
  default     = null
}

variable "logs_bucket" {
  description = "GCS bucket for logs"
  type        = string
  default     = "agisa-logs"
}

