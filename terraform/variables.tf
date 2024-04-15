# Google Provider Variables
variable "gcp_credentials" {
  description = "My BigQuery Credentials"
  sensitive   = true
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

variable "confluent_kafka_id" {
  description = "My Confluent Kafka Cluster ID"
  sensitive   = true
}

variable "confluent_kafka_rest_endpoint" {
  description = "My Confluent Kafka Cluster REST Endpoint"
  sensitive   = true
}

variable "confluent_kafka_api_key" {
  description = "My Confluent Kafka Cluster API Key"
  sensitive   = true
}

variable "confluent_kafka_api_secret" {
  description = "My Confluent Kafka Cluster Secret"
  sensitive   = true
}

variable "confluent_schema_registry_id" {
  description = "My Confluent Schema Registry Endpoint"
  sensitive   = true
}

variable "confluent_schema_registry_url" {
  description = "My Confluent Schema Registry Endpoint"
  sensitive   = true
}

variable "confluent_schema_registry_api_key" {
  description = "My Confluent Schema Registry API Key"
  sensitive   = true
}

variable "confluent_schema_registry_api_secret" {
  description = "My Confluent Schema Registry API Secret"
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


# Confluent Resource Variables


