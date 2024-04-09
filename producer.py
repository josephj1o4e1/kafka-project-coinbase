import os
import csv
from time import sleep
from typing import Dict

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField

from ride_record_key import RideRecordKey, ride_record_key_to_dict
from ride_record import RideRecord, ride_record_to_dict

# from settings import RIDE_KEY_SCHEMA_PATH, RIDE_VALUE_SCHEMA_PATH, \
#     SCHEMA_REGISTRY_URL, BOOTSTRAP_SERVERS, INPUT_DATA_PATH, KAFKA_TOPIC

from dotenv import load_dotenv
load_dotenv()

INPUT_DATA_PATH = os.environ["INPUT_DATA_PATH"]
RIDE_KEY_SCHEMA_PATH = os.environ["RIDE_KEY_SCHEMA_PATH"]
RIDE_VALUE_SCHEMA_PATH = os.environ["RIDE_VALUE_SCHEMA_PATH"]
SCHEMA_REGISTRY_URL = os.environ["SCHEMA_REGISTRY_URL"]
SCHEMA_REGISTRY_API_KEY = os.environ["SCHEMA_REGISTRY_API_KEY"]
SCHEMA_REGISTRY_API_SECRET = os.environ["SCHEMA_REGISTRY_API_SECRET"]
BOOTSTRAP_SERVERS = os.environ["BOOTSTRAP_SERVERS"]
CLUSTER_API_KEY = os.environ["CLUSTER_API_KEY"]
CLUSTER_API_SECRET = os.environ["CLUSTER_API_SECRET"]
KAFKA_TOPIC = 'rides_avro' #os.environ["KAFKA_TOPIC"]


def delivery_report(err, msg):
    if err is not None:
        print("Delivery failed for record {}: {}".format(msg.key(), err))
        return
    print('Record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.topic(), msg.partition(), msg.offset()))


class RideAvroProducer:
    def __init__(self, props: Dict):
        # Schema Registry and Serializer-Deserializer Configurations
        key_schema_str = self.load_schema(props['schema.key'])
        value_schema_str = self.load_schema(props['schema.value'])
        schema_registry_props = props['schema_registry_props']
        schema_registry_client = SchemaRegistryClient(schema_registry_props)
        self.key_serializer = AvroSerializer(schema_registry_client, key_schema_str, ride_record_key_to_dict)
        self.value_serializer = AvroSerializer(schema_registry_client, value_schema_str, ride_record_to_dict)

        # Producer Configuration
        producer_props = props['producer_props']
        self.producer = Producer(producer_props)

    @staticmethod
    def load_schema(schema_path: str):
        path = os.path.realpath(os.path.dirname(__file__))
        with open(f"{path}/{schema_path}") as f:
            schema_str = f.read()
        return schema_str

    @staticmethod
    def delivery_report(err, msg):
        if err is not None:
            print("Delivery failed for record {}: {}".format(msg.key(), err))
            return
        print('Record {} successfully produced to {} [{}] at offset {}'.format(
            msg.key(), msg.topic(), msg.partition(), msg.offset()))

    @staticmethod
    def read_records(resource_path: str):
        ride_records, ride_keys = [], []
        with open(resource_path, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)  # skip the header
            for row in reader:
                ride_records.append(RideRecord(arr=[row[0], row[3], row[4], row[9], row[16]]))
                ride_keys.append(RideRecordKey(vendor_id=int(row[0])))
        return zip(ride_keys, ride_records)

    def publish(self, topic: str, records: [RideRecordKey, RideRecord]):
        for key_value in records:
            key, value = key_value
            try:
                self.producer.produce(topic=topic,
                                      key=self.key_serializer(key, SerializationContext(topic=topic,
                                                                                        field=MessageField.KEY)),
                                      value=self.value_serializer(value, SerializationContext(topic=topic,
                                                                                              field=MessageField.VALUE)),
                                      on_delivery=delivery_report)
            except KeyboardInterrupt:
                print(f'Keyboard Interrupt!!')
                break
            except Exception as e:
                print(f"Exception while producing record - {value}: {e}")

        self.producer.flush()
        sleep(1)


if __name__ == "__main__":
    config = {
        'producer_props': {
            'bootstrap.servers': BOOTSTRAP_SERVERS,
            'security.protocol': 'SASL_SSL',
            'sasl.mechanism': 'PLAIN',
            'sasl.username': CLUSTER_API_KEY,
            'sasl.password': CLUSTER_API_SECRET
        },
        'schema_registry_props': {'url': SCHEMA_REGISTRY_URL, \
                  'basic.auth.user.info': f'{SCHEMA_REGISTRY_API_KEY}:{SCHEMA_REGISTRY_API_SECRET}'},
        'schema.key': RIDE_KEY_SCHEMA_PATH,
        'schema.value': RIDE_VALUE_SCHEMA_PATH
    }

    producer = RideAvroProducer(props=config)
    ride_records = producer.read_records(resource_path=INPUT_DATA_PATH)

    producer.publish(topic=KAFKA_TOPIC, records=ride_records)

