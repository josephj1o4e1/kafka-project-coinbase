output "confluent_schema_registry_api_key_id" {
  description = "Schema Registry Cluster API Key ID that is owned by 'dezoom_env_manager' service account"
  value       = confluent_api_key.dezoom_env_manager_schema_registry_api_key.id
  sensitive   = true
}

output "confluent_schema_registry_api_key_secret" {
  description = "Schema Registry Cluster API Key Secret that is owned by 'dezoom_env_manager' service account"
  value       = confluent_api_key.dezoom_env_manager_schema_registry_api_key.secret
  sensitive   = true
}

output "confluent_schema_registry_url" {
  description = "Schema Registry Cluster rest endpoint URL"
  value       = confluent_schema_registry_cluster.essentials.rest_endpoint
  sensitive   = true
}

output "confluent_kafka_bootstrap" {
  description = "Confluent Kafka Cluster's Bootstrap Endpoint"
  value       = confluent_kafka_cluster.dezoom_kafka_cluster0.bootstrap_endpoint
  sensitive   = true
}

output "confluent_kafka_api_key_id" {
  description = "Kafka API Key ID"
  value       = confluent_api_key.dezoom_cluster_manager_kafka_api_key.id
  sensitive   = true
}

output "confluent_kafka_api_key_secret" {
  description = "Kafka API Key Secret"
  value       = confluent_api_key.dezoom_cluster_manager_kafka_api_key.secret
  sensitive   = true
}

output "confluent_kafka_topic_name" {
  description = "Kafka topic name"
  value       = confluent_kafka_topic.coinbase_avro.topic_name
}







