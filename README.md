# kafka-project-coinbase

![project-techstack-logo](assets/images/dezoom-project-techstack.drawio.svg)

## Introduction  
This is the final project repo of Kafka streaming data pipeline for real-time Coinbase market data analysis.   
### **Environment:**  
OS: WSL (Linux AMD64)  
Package Manager: Conda  

### **Problem description:**  
This repository addresses the need for real-time monitoring of Coinbase market data updates, focusing on orders and trades. By implementing a streaming data pipeline, it enables traders to stay informed about trading volume and values across various virtual currencies on Coinbase.    
We achieve this by streaming data from Coinbase's ["Exchange Websocket Direct Market Data"](https://docs.cloud.coinbase.com/exchange/docs/websocket-overview) feeding it into Confluent Kafka, and ultimately processing it in BigQuery and Looker for batch analytics and visualizations.  


This streaming data pipeline encompasses the following key aspects:  

### **Cloud:**  
The project is developed in Confluent Cloud and BigQuery. Terraform is used as my IaC tool.  
 
### **Data ingestion:**  
Using consumer/producers and streaming technologies like Kafka streaming from local producer python script to Confluent Cloud.  
 
### **Data warehouse:**   
Streamed data to BigQuery tables, and the tables are partitioned and clustered in a way that makes sense for the upstream queries.   
Partitioning data on the timestamp column at the hourly level can significantly improve query performance for time-based queries.   
Clustering by PRODUCT_ID ensures that the data within each partition is physically sorted on the product ID column, which makes sense for GROUP BY clauses.   
  
### **Transformations:**   
Utilized ksqlDB to perform real-time data transformations, enrichments, and aggregations on the incoming data streams from Coinbase.   
 
### **Dashboard:**   
[My Interactive Looker Dashboard](https://lookerstudio.google.com/reporting/3711d375-9496-4ce0-be5b-46e5345048c6) that visualizes simple analytical results after 10 hours of continuous streaming.   
<img width="635" height="354" alt="image" src="https://github.com/josephj1o4e1/kafka-project-coinbase/assets/13396370/f4bc361d-9837-4c86-b810-7285fb1c44fe">
<img width="354" height="354" alt="image" src="https://github.com/josephj1o4e1/kafka-project-coinbase/assets/13396370/454c4a59-851a-4560-bcaa-8420dbefaa88">
<img width="782" alt="image" src="https://github.com/josephj1o4e1/kafka-project-coinbase/assets/13396370/64021220-3a6a-414e-84bf-a21ccc2bb522">


 
### **Reproducibility:**  
Please follow the next section to reproduce the pipeline.    
 

## Reproduce this pipeline, step-by-step:   

