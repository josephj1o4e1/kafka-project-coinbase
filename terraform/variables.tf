# Google Provider Variables
variable "gcp_credentials" {
  description = "My BigQuery Credentials"
  sensitive   = true
}

# GCP Resource Variables
variable "gcp_project" {
  description = "My BigQuery Project ID"
}

variable "gcp_region" {
  description = "My BigQuery Region"
  default     = "us-central1"
}

variable "gcp_zone" {
  description = "My BigQuery Zone"
  default     = "us-central1-c"
}

variable "gcp_dataset" {
  description = "My BigQuery Dataset ID"
  default     = "dezoom_coinbase_stream_terraform"
}

variable "gcp_location" {
  description = "My BigQuery Location"
  default     = "US"
}




# Confluent Provider Variables
variable "confluent_cloud_api_key" {
  description = "My Confluent Cloud API Key"
  sensitive   = true
}

variable "confluent_cloud_api_secret" {
  description = "My Confluent Cloud API Secret"
  sensitive   = true
}

# Confluent Resource Variables

variable "confluent_ksql_output_topic" {
  description = "My Confluent Cloud KSQL Output Topic Name"
  default     = "COINBASE_AVRO_FLAT"
}
