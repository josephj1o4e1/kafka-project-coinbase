# kafka-project-coinbase

![project-techstack-logo](assets/images/dezoom-project-techstack.drawio.svg)

## Introduction  
This final project repo includes real-time Coinbase market streaming pipeline.   
The above graph is a brief summary of my streaming pipeline. My Kafka producer, written in Python, ingests data from Coinbase and publishes it to a Confluent Kafka Topic. Prior to consumption, I use ksqlDB for essential stream processing and transformation. For consuming the data, I utilize a managed Confluent connector as my Kafka consumer, which retrieves messages from ksqlDB and transfers them to a BigQuery Table.     

### **Problem description:**  
This repository fulfills the requirement for real-time monitoring of Coinbase market data updates, specifically focusing on orders and trades. Through the implementation of a streaming data pipeline, it empowers traders with up-to-date information on trading volume and values across various virtual currencies on Coinbase.  
This is achieved by streaming data from Coinbase's ["Exchange Websocket Direct Market Data"](https://docs.cloud.coinbase.com/exchange/docs/websocket-overview), feeding it into Confluent Kafka for processing, storing the processed data on BigQuery, and ultimately leveraging Looker Studio to construct visualizations for insights into trading trends.  

This streaming data pipeline encompasses the following key aspects:  

### **Cloud:**  
The project is developed using Confluent Cloud and BigQuery. Terraform serves as the Infrastructure as Code (IaC) tool for resource creation. However, it's worth noting that certain resources on Confluent are best created using the Confluent Cloud Console for enhanced security practices. Rest assured, I'll provide guidance wherever possible throughout the process.  
 
### **Data ingestion:**  
Producer:    
Utilizing Kafka as the streaming tool, this repository employs the `producer_coinbase.py` script to ingest real-time market data from the Coinbase WebSocket feed. Acting as a local producer, this script retrieves data from the WebSocket, processes it, and publishes messages to Confluent Cloud Topics. In essence, it serves as a vital link between the Coinbase feed and Confluent Cloud, facilitating seamless data flow.  
Consumer:   
The consumer script is not essential in this setup because I utilize Confluent's BigQuery Sink Connector v2 to consume the data and send it directly to BigQuery. Visit this [LINK](https://www.confluent.io/resources/demo/bigquery-cloud-data-warehouse-streaming-pipelines/?utm_term=&creative=&device=c&placement=&gad_source=1).  
 
### **Data warehouse:**    
Data has been streamed to BigQuery tables, where they are partitioned and clustered to optimize upstream queries. Refer to `bigquery_partition.sql` for details.   
Partitioning data based on the `TIME` column at the hourly level can notably enhance query performance for time-based queries. Additionally, clustering by `PRODUCT_ID` ensures that data within each partition is logically sorted based on the product ID column, aligning well with GROUP BY clauses.     
  
### **Transformations:**     
Utilized ksqlDB to perform real-time data transformations, enrichments, and aggregations on the incoming data streams from Coinbase. Refer to `ksqldb/transform_changes.sql` for details.  
One of the reasons for the transformation is that our data includes an attribute called "changes" that is a nested array. While nested arrays are supported by AVRO on Confluent Kafka, it is not yet supported by AVRO on BigQuery. Therefore, we perform necessary transformations to ensure that the data meets the type requirements for AVRO on BigQuery. 
 
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
	`cd kafka-project-coinbase`  

3. Create the conda environment.  
	`conda env create -f environment.yml`  
	`conda activate dezoom-project-reproduce`

4. Create a BigQuery project.  

5. Get BigQuery api keys/credentials   
	- Create keys/ folder under terraform folder
 	- In GCP Cloud Console, create service account:  
		- IAM&admin -> service accounts -> create new service account -> choose only BigQuery Admin Permission
		- Click the 3dots -> manage keys -> create a new key(JSON) -> save to terraform/keys/ folder

6. Create a Confluent Kafka Environment and Cluster.
	- https://docs.confluent.io/cloud/current/get-started/index.html 

7. **.env** file: Copy template.env to .env, and start filling in the variables. 
	- `COINBASE_KEY_SCHEMA_PATH`='resources/schemas/coinbase_key.avsc'  
	- `COINBASE_VALUE_SCHEMA_PATH`='resources/schemas/coinbase_value.avsc'  

	Confluent Cloud Console:  
	- `BOOTSTRAP_SERVERS`:  
		Navigate to Environments/Environment/Cluster/Cluster Settings and you'll see it.  
	- `CLUSTER_API_KEY`, `CLUSTER_API_SECRET`: 
		Navigate to Environments/Environment/Cluster/API Keys and add API key.  
	- `KAFKA_TOPICS`="coinbase_avro"  
	- `SCHEMA_REGISTRY_URL`(endpoint), `SCHEMA_REGISTRY_API_KEY`, `SCHEMA_REGISTRY_API_SECRET`:  
		Navigate to Environments/<YOUR ENV>/Stream Governance API.  
		Follow this [LINK](https://docs.confluent.io/cloud/current/get-started/schema-registry.html#create-an-api-key-for-ccloud-sr) to learn more about creating schema registration key.   
	
	Coinbase Sandbox API:  
	- `SANDBOX_API_KEY`, `SANDBOX_PASSPHRASE`, `SANDBOX_SECRET_KEY`:  
		Sign up and Log into the [sandbox web interface](https://public.sandbox.exchange.coinbase.com/), and go to the "API" tab to create an API key.  

8. **secret.tfvars** file: Copy template_secret.tfvars to secret.tfvars, and start filling in the variables.  
	GCP:  
	- `gcp_credentials`:  
		path of your (credential) .json file    
	- `gcp_project`:  
		name of your gcp project (project id).  
	
	Confluent Cloud:  
	- `confluent_cloud_api_key`, `confluent_cloud_api_secret`:  
		Create a cloud api key on confluent cloud console (under the main tab on the upperright).   
	- `confluent_kafka_id`, `confluent_kafka_rest_endpoint`:  
		Go to cluster settings to get kafka cluster id and rest endpoint.  
	- `confluent_kafka_api_key`, `confluent_kafka_api_secret`:  
		Same as `CLUSTER_API_KEY`, `CLUSTER_API_SECRET` in .env  

9. Run terraform (bigquery dataset, confluent topic, confluent schema registry).   
	- Install Terraform if you haven't already (I use Linux AMD64)  
		https://developer.hashicorp.com/terraform/install (use terraform --help command to confirm installation)  
	- `cd terraform/`   
	- `terraform init` (get providers)  
	- `terraform plan -var-file="secret.tfvars"` (this make sure credentials work and let you inspect prepared resources)   
	- `terraform apply -var-file="secret.tfvars"` 

10. Setup ksqlDB.  
	- Create a ksqldb cluster. All default is fine.  
	- Go to Streams tab -> Import topics as stream -> choose coinbase_avro.  
	- Go to Editor tab -> run the two queries in the transform_changes.sql under the resources/ folder, one at a time.  
	- Now you should already have two streams created: coinbase_avro_explode, coinbase_avro_flat. You should also have Two topics created that have the suffix coinbase_avro_explode and coinbase_avro_flat.  

11. Add Confluent Google BigQuery Sink v2 Connector. 
	- Choose topic to stream from: choose the topic that has "coinbase_avro_flat" as suffix.  
	- Use an existing API key: Enter CLUSTER_API_KEY, CLUSTER_API_SECRET (to allow the connector to only have permissions to that Kafka cluster).  
	- Connect with Google Cloud: Set OAuth 2.0 permission to connect to BigQuery.  
	- Specify BigQuery project id and dataset id(dezoom_coinbase_stream_terraform) of your desired BigQuery table to stream to.  
	- Config and set kafka record key/value format both AVRO.  
	- In advanced config > Auto create tables, select Non-partitioned.  


## 2. Usage   
After finishing all the setup steps above:    
1. Simply run `python producer_coinbase.py`.  Streaming begins.  
It should look something like this:  
<img width="791" alt="terminal_view_streaming" src="https://github.com/josephj1o4e1/kafka-project-coinbase/assets/13396370/cdb76be8-fdd8-464c-8d63-750457eb43dd">
Check if your data is sent to the BigQuery Table.  

2. BigQuery table Partitioning and Clustering.  
	Have a look at bigquery_partition.sql and run the sql query in your BigQuery project to partition and cluster the table.  
	Change `TABLE_NAME` and `TABLE_NAME_PARTITIONED_CLUSTERED` to your desired table name.  
	Partitioned by time (hour), and clustered by product_id.  
	After partitioning and clustering the original table, you can compare the performance improvement like this:  
	```
	-- Performance before Partitioning and Clustering: 
	-- process 22.13MB
	SELECT * FROM <TABLE_NAME> 
	where PRODUCT_ID='BTC-EUR' and time between '2024-04-13T07:00:00' and '2024-04-13T9:00:00'
	limit 1000
	;
	-- Performance after Partitioning and Clustering: 
	-- process 2.35MB
	SELECT * FROM <TABLE_NAME_PARTITIONED_CLUSTERED> 
	where PRODUCT_ID='BTC-EUR' and time between '2024-04-13T07:00:00' and '2024-04-13T9:00:00'
	limit 1000
	;
	```

3. Looker Studio.  
	Visualize the data on Looker studio.  
	[Here's the link](https://lookerstudio.google.com/reporting/3711d375-9496-4ce0-be5b-46e5345048c6) of my simple analysis and visualization. 



