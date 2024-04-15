-- On the WebUI of ksqldb -> Streams tab, import coinbase_avro topic as a stream
-- Firstly, Explode nested array "changes" to multiple rows. 
CREATE STREAM coinbase_avro_explode AS
SELECT
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
