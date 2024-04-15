terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.24.0"
    }
    confluent = {
      source  = "confluentinc/confluent"
      version = "1.70.0"
    }
  }
}

provider "google" {
  credentials = file(var.gcp_credentials)
  project     = var.gcp_project
  region      = var.gcp_region
  zone        = var.gcp_zone
}

# Option #2: Manage a single Kafka cluster in the same Terraform workspace (Create a Kafka Cluster first on the Confluent Cloud Console)
# See https://github.com/confluentinc/terraform-provider-confluent/tree/master/examples/configurations/managing-single-kafka-cluster for more details
provider "confluent" {
  cloud_api_key       = var.confluent_cloud_api_key
  cloud_api_secret    = var.confluent_cloud_api_secret
  kafka_id            = var.confluent_kafka_id            # optionally use KAFKA_ID env var
  kafka_rest_endpoint = var.confluent_kafka_rest_endpoint # optionally use KAFKA_REST_ENDPOINT env var
  kafka_api_key       = var.confluent_kafka_api_key       # optionally use KAFKA_API_KEY env var
  kafka_api_secret    = var.confluent_kafka_api_secret    # optionally use KAFKA_API_SECRET env var
}


# Define GCP resources
# Create a BigQuery Dataset
resource "google_bigquery_dataset" "dezoom_coinbase_stream_terraform" {
  dataset_id                 = var.gcp_dataset
  location                   = var.gcp_location
  delete_contents_on_destroy = true
}


# Define Confluent Cloud resources
# Create a Confluent Kafka Topic
resource "confluent_kafka_topic" "coinbase_avro" {
  topic_name = "coinbase_avro"
  partitions_count = 4
}

# Create Schema in Confluent Schema Registry (value)
resource "confluent_schema" "coinbase_avro_value_schema" {
  schema_registry_cluster {
    id = var.confluent_schema_registry_id
  }
  rest_endpoint = var.confluent_schema_registry_url
  subject_name = "coinbase_avro-value"
  format = "AVRO"
  schema = file("../resources/schemas/coinbase_value.avsc")
  credentials {
    key    = var.confluent_schema_registry_api_key
    secret = var.confluent_schema_registry_api_secret
  }

  lifecycle {
    prevent_destroy = true
  }
}

# Create Schema in Confluent Schema Registry (key)
resource "confluent_schema" "coinbase_avro_key_schema" {
  schema_registry_cluster {
    id = var.confluent_schema_registry_id
  }
  rest_endpoint = var.confluent_schema_registry_url
  subject_name = "coinbase_avro-key"
  format = "AVRO"
  schema = file("../resources/schemas/coinbase_key.avsc")
  credentials {
    key    = var.confluent_schema_registry_api_key
    secret = var.confluent_schema_registry_api_secret
  }

  lifecycle {
    prevent_destroy = true
  }
}
