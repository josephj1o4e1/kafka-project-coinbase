-- On the WebUI of ksqldb -> Streams tab, import coinbase_avro topic as a stream
CREATE STREAM coinbase_avro
WITH (
    KAFKA_TOPIC = 'coinbase_avro',
    VALUE_FORMAT = 'AVRO',
    KEY_FORMAT = 'AVRO'
)
;

-- Firstly, Explode nested array "changes" to multiple rows. 
-- ksqlDB adds the implicit columns ROWTIME and ROWKEY to every stream and table, which represent the corresponding Kafka message timestamp and message key
-- https://docs.ksqldb.io/en/0.7.1-ksqldb/developer-guide/ksqldb-reference/create-stream/#description
CREATE STREAM coinbase_avro_explode AS
SELECT
    ROWKEY,  
    type,
    product_id,
    EXPLODE(changes) AS change,
    time
FROM
    coinbase_avro
EMIT CHANGES
;


-- Secondly, Unnest coinbase_avro_explode "change" to multiple columns. change[0] should be metadata, skip it. 
CREATE STREAM coinbase_avro_flat AS
SELECT
    ROWKEY,  -- Include the ROWKEY column in the projection
    type,
    product_id,
    change[1] AS change_side,
    CAST(change[2] AS DOUBLE) AS change_price,
    CAST(change[3] AS DOUBLE) AS change_size,
    time
FROM
    coinbase_avro_explode
EMIT CHANGES
;
