# kafka-project-coinbase
## Introduction  
This is a python Kafka project (DE zoom camp) streaming Coinbase WebSocket feed market data.  
**Environment**  
OS: WSL (Linux AMD64)  
Package Manager: Conda  

**Problem description:**  
  This repository addresses the need for real-time monitoring of Coinbase market data updates, focusing on orders and trades. By implementing a streaming data pipeline, it enables traders to stay informed about trading volume and values across various virtual currencies on Coinbase.    
	We achieve this by streaming data from Coinbase's ["Exchange Websocket Direct Market Data"](https://docs.cloud.coinbase.com/exchange/docs/websocket-overview) feeding it into Confluent Kafka, and ultimately processing it in BigQuery and Looker for batch analytics and visualizations.  


This streaming data pipeline encompasses the following key aspects:  

**Cloud:**  
	The project is developed in Confluent Cloud and BigQuery. Terraform is used as my IaC tool.  
 
**Data ingestion (choose either batch or stream):**  
	Using consumer/producers and streaming technologies like Kafka streaming from local producer python script to Confluent Cloud.  
 
**Data warehouse:**   
	Streamed data to BigQuery tables, and the tables are partitioned and clustered in a way that makes sense for the upstream queries.   
  Partitioning data on the timestamp column at the hourly level can significantly improve query performance for time-based queries.   
  Clustering by PRODUCT_ID ensures that the data within each partition is physically sorted on the product ID column, which makes sense for GROUP BY clauses.   
  
**Transformations:**   
	Utilized ksqlDB to perform real-time data transformations, enrichments, and aggregations on the incoming data streams from Coinbase.   
 
**Dashboard:**   
	[My Looker Dashboard](https://lookerstudio.google.com/reporting/3711d375-9496-4ce0-be5b-46e5345048c6) that visualizes simple analytical results after 10 hours of continuous streaming.   
 
**Reproducibility:**  
	Please follow the next section to reproduce the pipeline.    
 

## How to use the code, step-by-step:   

