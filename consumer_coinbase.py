import os
from typing import Dict, List

from confluent_kafka import Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField

from coinbase_record_key import dict_to_coinbase_record_key
from coinbase_record import dict_to_coinbase_record

from dotenv import load_dotenv
load_dotenv()

INPUT_DATA_PATH = os.environ["INPUT_DATA_PATH"]
COINBASE_KEY_SCHEMA_PATH = os.environ["COINBASE_KEY_SCHEMA_PATH"]
COINBASE_VALUE_SCHEMA_PATH = os.environ["COINBASE_VALUE_SCHEMA_PATH"]
SCHEMA_REGISTRY_URL = os.environ["SCHEMA_REGISTRY_URL"]
SCHEMA_REGISTRY_API_KEY = os.environ["SCHEMA_REGISTRY_API_KEY"]
SCHEMA_REGISTRY_API_SECRET = os.environ["SCHEMA_REGISTRY_API_SECRET"]
BOOTSTRAP_SERVERS = os.environ["BOOTSTRAP_SERVERS"]
CLUSTER_API_KEY = os.environ["CLUSTER_API_KEY"]
CLUSTER_API_SECRET = os.environ["CLUSTER_API_SECRET"]
KAFKA_TOPIC = os.environ["KAFKA_TOPIC"]


class CoinbaseAvroConsumer:
    def __init__(self, props: Dict):

        # Schema Registry and Serializer-Deserializer Configurations
        key_schema_str = self.load_schema(props['schema.key'])
        value_schema_str = self.load_schema(props['schema.value'])
        schema_registry_props = props['schema_registry_props']
        schema_registry_client = SchemaRegistryClient(schema_registry_props)
        self.avro_key_deserializer = AvroDeserializer(schema_registry_client=schema_registry_client,
                                                      schema_str=key_schema_str,
                                                      from_dict=dict_to_coinbase_record_key)
        self.avro_value_deserializer = AvroDeserializer(schema_registry_client=schema_registry_client,
                                                        schema_str=value_schema_str,
                                                        from_dict=dict_to_coinbase_record)
        consumer_props = props['consumer_props']
        self.consumer = Consumer(consumer_props)

    @staticmethod
    def load_schema(schema_path: str):
        path = os.path.realpath(os.path.dirname(__file__))
        with open(f"{path}/{schema_path}") as f:
            schema_str = f.read()
        return schema_str

    def consume_from_kafka(self, topics: List[str]):
        self.consumer.subscribe(topics=topics)
        while True:
            try:
                # SIGINT can't be handled when polling, limit timeout to 1 second.
                msg = self.consumer.poll(1.0) # 1.0 milliseconds = timeout......If no data is sent to the consumer, the poll() function will take at least this long.
                if msg is None:
                    continue
                key = self.avro_key_deserializer(msg.key(), SerializationContext(msg.topic(), MessageField.KEY))
                record = self.avro_value_deserializer(msg.value(),
                                                      SerializationContext(msg.topic(), MessageField.VALUE))
                print('New consumer.poll()')
                if record is not None:
                    print("{}, {}".format(key, record))
            except KeyboardInterrupt:
                break

        self.consumer.close()


if __name__ == "__main__":
    config = {
        'consumer_props': {
            'bootstrap.servers': BOOTSTRAP_SERVERS,
            'group.id': 'datatalkclubs.coinbase.avro.consumer',
            'auto.offset.reset': 'earliest',
            'security.protocol': 'SASL_SSL',
            'sasl.mechanism': 'PLAIN',
            'sasl.username': CLUSTER_API_KEY,
            'sasl.password': CLUSTER_API_SECRET
        },
        'schema_registry_props': {'url': SCHEMA_REGISTRY_URL, \
                  'basic.auth.user.info': f'{SCHEMA_REGISTRY_API_KEY}:{SCHEMA_REGISTRY_API_SECRET}'},
        'schema.key': COINBASE_KEY_SCHEMA_PATH,
        'schema.value': COINBASE_VALUE_SCHEMA_PATH
    }    
    avro_consumer = CoinbaseAvroConsumer(props=config)
    avro_consumer.consume_from_kafka(topics=[KAFKA_TOPIC])
