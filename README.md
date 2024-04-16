# kafka-project-coinbase

![project-techstack-logo](assets/images/dezoom-project-techstack.drawio.svg)

## Introduction  
This final project repo includes a Kafka streaming data pipeline for real-time Coinbase market data analysis.   

### **Problem description:**  
This repository addresses the need for real-time monitoring of Coinbase market data updates, focusing on orders and trades. By implementing a streaming data pipeline, it enables traders to stay informed about trading volume and values across various virtual currencies on Coinbase.    
We achieve this by streaming data from Coinbase's ["Exchange Websocket Direct Market Data"](https://docs.cloud.coinbase.com/exchange/docs/websocket-overview) feeding it into Confluent Kafka, and ultimately processing it in BigQuery and Looker for batch analytics and visualizations.  


This streaming data pipeline encompasses the following key aspects:  

### **Cloud:**  
The project is developed in Confluent Cloud and BigQuery. Terraform is used as my IaC tool.  
However, some resources on Confluent are better to create using Confluent Cloud Console due to better security practice.  
 
### **Data ingestion:**  
(producer_coinbase.py)  
Utilizing Kafka as the streaming tool, the repository employs the producer_coinbase.py script to ingest real-time market data from the Coinbase WebSocket feed. Functioning as a local producer, this script retrieves data from the WebSocket, processes it, and publishes messages to Confluent Cloud Topics. This script bridges the gap between the Coinbase feed and Confluent Cloud.  
(no consumer script)  
Consumer script is not really needed since I use Confluent's BigQuery Sink Connector v2 as my consumer to consume the data and send to BigQuery. Visit this [LINK](https://www.confluent.io/resources/demo/bigquery-cloud-data-warehouse-streaming-pipelines/?utm_term=&creative=&device=c&placement=&gad_source=1) to know more.  
 
### **Data warehouse:**   
(bigquery_partition.sql)  
Streamed data to BigQuery tables, and the tables are partitioned and clustered in a way that makes sense for the upstream queries. Partitioning data on the timestamp column at the hourly level can significantly improve query performance for time-based queries. Clustering by PRODUCT_ID ensures that the data within each partition is physically sorted on the product ID column, which makes sense for GROUP BY clauses.   
  
### **Transformations:**   
(ksqldb/transform_changes.sql)  
Utilized ksqlDB to perform real-time data transformations, enrichments, and aggregations on the incoming data streams from Coinbase.   
 
### **Dashboard:**   
[My Interactive Looker Dashboard](https://lookerstudio.google.com/reporting/3711d375-9496-4ce0-be5b-46e5345048c6) that visualizes simple analytical results after 10 hours of continuous streaming.   
<img width="635" height="354" alt="image" src="https://github.com/josephj1o4e1/kafka-project-coinbase/assets/13396370/f4bc361d-9837-4c86-b810-7285fb1c44fe">
<img width="354" height="354" alt="image" src="https://github.com/josephj1o4e1/kafka-project-coinbase/assets/13396370/454c4a59-851a-4560-bcaa-8420dbefaa88">
<img width="782" alt="image" src="https://github.com/josephj1o4e1/kafka-project-coinbase/assets/13396370/64021220-3a6a-414e-84bf-a21ccc2bb522">


 
## **Reproduce the Pipeline**  
Please follow the below steps to reproduce the pipeline.  
1. [Setup](#1-setup)
2. [Usage](#2-usage)

## 1. Setup   
### **Environment/Prequisites:**  
OS: WSL (Linux AMD64)  
Package Manager: Conda  
Git  
BigQuery Free Account  
Confluent Cloud Free Account  

### **Step-by-step Setup**
1. Git Clone this repo and navigate to project directory.  
	`git clone https://github.com/josephj1o4e1/kafka-project-coinbase.git`

2. Create the conda environment.  
	`conda env create -f environment.yml`  
	`conda activate dezoom-project-reproduce`

3. Create a BigQuery project.  

4. Get BigQuery api keys/credentials   
	- create keys/ folder under terraform folder
	- put (credential) .json file under keys/ folder

5. Create a Confluent Kafka Environment and Cluster.  

6. **.env** file: Copy template.env to .env, and start filling in the variables. 
	- COINBASE_KEY_SCHEMA_PATH='resources/schemas/coinbase_key.avsc'  
	- COINBASE_VALUE_SCHEMA_PATH='resources/schemas/coinbase_value.avsc'  

	Confluent Cloud Console:  
	- BOOTSTRAP_SERVERS:  
		Navigate to Environments/Environment/Cluster/Cluster Settings and you'll see it.  
	- CLUSTER_API_KEY, CLUSTER_API_SECRET: 
		Navigate to Environments/Environment/Cluster/API Keys and add API key.  
	- KAFKA_TOPICS="coinbase_avro"  
	- SCHEMA_REGISTRY_URL(endpoint), SCHEMA_REGISTRY_API_KEY, SCHEMA_REGISTRY_API_SECRET:  
		Navigate to Environments/<YOUR ENV>/Stream Governance API.  
		Follow this [LINK](https://docs.confluent.io/cloud/current/get-started/schema-registry.html#create-an-api-key-for-ccloud-sr) to learn more about creating schema registration key.   
	
	Coinbase Sandbox API:  
	- SANDBOX_API_KEY, SANDBOX_PASSPHRASE, SANDBOX_SECRET_KEY:  
		Sign up and Log into the [sandbox web interface](https://public.sandbox.exchange.coinbase.com/), and go to the "API" tab to create an API key.  

7. **secret.tfvars** file: Copy template_secret.tfvars to secret.tfvars, and start filling in the variables.  
	GCP:  
	- gcp_credentials:  
		path of your (credential) .json file    
	- gcp_project: 
		name of your gcp project (project id).  
	
	Confluent Cloud:  
	- confluent_cloud_api_key, confluent_cloud_api_secret:  
		Create a cloud api key on confluent cloud console (under the main tab on the upperright).   
	- confluent_kafka_id, confluent_kafka_rest_endpoint:  
		Go to cluster settings to get kafka cluster id and rest endpoint.  
	- confluent_kafka_api_key, confluent_kafka_api_secret:  
		Same as CLUSTER_API_KEY, CLUSTER_API_SECRET in .env  

8. Run terraform (bigquery dataset, confluent topic, confluent schema registry).   
	- install terraform if you haven't yet (mine is linux amd64)  
		https://developer.hashicorp.com/terraform/install (use terraform --help command to confirm installation)  
	- `cd terraform/`   
	- `terraform init` (get providers)  
	- `terraform plan -var-file="secret.tfvars"` (this make sure credentials work and prepared resources are correct)   
	- `terraform apply -var-file="secret.tfvars"` 

9. Setup ksqlDB stream processing/transformation.  
	Although our avro works on Confluent Kafka, the avro schema changes when sent to BigQuery since Nested arrays are not supported by BigQuery yet.  
	- Create a ksqldb cluster. All default is fine.  
	- Go to Streams tab -> Import topics as stream -> choose coinbase_avro.  
	- Go to Editor tab -> run the two queries in the transform_changes.sql under the resources/ folder, one at a time.  
	- Now you should already have two streams created: coinbase_avro_explode, coinbase_avro_flat. You should also have Two topics created that have the suffix coinbase_avro_explode and coinbase_avro_flat.  

10. Add Confluent Google BigQuery Sink v2 Connector. 
	- Choose topic to stream from: choose the topic that has "coinbase_avro_flat" as suffix.  
	- Use an existing API key: Enter CLUSTER_API_KEY, CLUSTER_API_SECRET (to allow the connector to only have permissions to that Kafka cluster).  
	- Connect with Google Cloud: Set OAuth 2.0 permission to connect to BigQuery.  
	- Specify BigQuery project id and dataset id(dezoom_coinbase_stream_terraform) of your desired BigQuery table to stream to.  
	- Config and set kafka record key/value format both AVRO.  
	- In advanced config > Auto create tables, select Non-partitioned.  


## 2. Usage   
Please finish all the setup steps above first.  
1. Simply run `python producer_coinbase.py`.  Streaming begins.  
It should look something like this:  
<img width="791" alt="terminal_view_streaming" src="https://github.com/josephj1o4e1/kafka-project-coinbase/assets/13396370/cdb76be8-fdd8-464c-8d63-750457eb43dd">

2. BigQuery table Partitioning and Clustering. 
	Have a look at bigquery_partition.sql and run the sql query in your BigQuery project to partition and cluster the table.  
	Partitioned by time-hour, and clustered by product_id.  
	```
	Performance after Partitioning and Clustering: 
	-- process 22.13MB
	SELECT * FROM <TABLE_NAME> 
	where PRODUCT_ID='BTC-EUR' and time between '2024-04-13T07:00:00' and '2024-04-13T9:00:00'
	limit 1000
	;
	-- process 2.35MB
	SELECT * FROM <TABLE_NAME_PARTITIONED_CLUSTERED> 
	where PRODUCT_ID='BTC-EUR' and time between '2024-04-13T07:00:00' and '2024-04-13T9:00:00'
	limit 1000
	;
	```

3. Looker Studio. 
	Visualize the data on Looker studio. 
	[Here's the link](https://lookerstudio.google.com/reporting/3711d375-9496-4ce0-be5b-46e5345048c6) of my simple analysis and visualization. 



