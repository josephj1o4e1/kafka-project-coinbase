terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "5.24.0"
    }
    # confluent = {
    #   source  = "confluentinc/confluent"
    #   version = "1.68.0"
    # }
  }
}

provider "google" {
  project = "level-night-412601"
  region  = "us-central1"
  zone    = "us-central1-c"
}

# provider "confluent" {
#   cloud_api_key    = var.confluent_cloud_api_key    # optionally use CONFLUENT_CLOUD_API_KEY env var
#   cloud_api_secret = var.confluent_cloud_api_secret # optionally use CONFLUENT_CLOUD_API_SECRET env var
# }


# Define GCP resources


# Define Confluent Cloud resources

