import os
import csv
from time import sleep
from typing import Dict

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField

from coinbase_record_key import CoinbaseRecordKey, coinbase_record_key_to_dict
from coinbase_record import CoinbaseRecord, coinbase_record_to_dict

# from ingest_coinbase_sandbox import CoinbaseSandboxIngestion
import asyncio, base64, hashlib, hmac, json, os, time, websockets

from dotenv import load_dotenv
load_dotenv()

# INPUT_DATA_PATH = os.environ["INPUT_DATA_PATH"]
# Coinbase
SANDBOX_API_KEY = str(os.environ.get('SANDBOX_API_KEY'))
SANDBOX_PASSPHRASE = str(os.environ.get('SANDBOX_PASSPHRASE'))
SANDBOX_SECRET_KEY = str(os.environ.get('SANDBOX_SECRET_KEY'))
URI = 'wss://ws-feed-public.sandbox.exchange.coinbase.com'
SIGNATURE_PATH = '/users/self/verify' # path of the API endpoint.
COINBASE_KEY_SCHEMA_PATH = os.environ["COINBASE_KEY_SCHEMA_PATH"]
COINBASE_VALUE_SCHEMA_PATH = os.environ["COINBASE_VALUE_SCHEMA_PATH"]
# Kafka
SCHEMA_REGISTRY_URL = os.environ["SCHEMA_REGISTRY_URL"]
SCHEMA_REGISTRY_API_KEY = os.environ["SCHEMA_REGISTRY_API_KEY"]
SCHEMA_REGISTRY_API_SECRET = os.environ["SCHEMA_REGISTRY_API_SECRET"]
BOOTSTRAP_SERVERS = os.environ["BOOTSTRAP_SERVERS"]
CLUSTER_API_KEY = os.environ["CLUSTER_API_KEY"]
CLUSTER_API_SECRET = os.environ["CLUSTER_API_SECRET"]
KAFKA_TOPIC = os.environ["KAFKA_TOPIC"]


def delivery_report(err, msg):
    if err is not None:
        print("Delivery failed for record {}: {}".format(msg.key(), err))
        return
    print('Record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.topic(), msg.partition(), msg.offset()))


class CoinbaseAvroProducer:
    def __init__(self, props: Dict):
        # Schema Registry and Serializer-Deserializer Configurations
        key_schema_str = self.load_schema(props['schema.key'])
        value_schema_str = self.load_schema(props['schema.value'])
        schema_registry_props = props['schema_registry_props']
        schema_registry_client = SchemaRegistryClient(schema_registry_props)
        self.key_serializer = AvroSerializer(schema_registry_client, key_schema_str, coinbase_record_key_to_dict)
        self.value_serializer = AvroSerializer(schema_registry_client, value_schema_str, coinbase_record_to_dict)

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

    async def generate_signature():
        timestamp = str(time.time())
        message = f'{timestamp}GET{SIGNATURE_PATH}'
        hmac_key = base64.b64decode(SANDBOX_SECRET_KEY)
        signature = hmac.new(
            hmac_key,
            message.encode('utf-8'),
            digestmod=hashlib.sha256).digest()
        signature_b64 = base64.b64encode(signature).decode().rstrip('\n')
        return signature_b64, timestamp
    
    async def publish(self, topic: str, channel: str='level2', product_ids: str='BTC-USD'):
        signature_b64, timestamp = await self.generate_signature()
        subscribe_message = json.dumps({
            'type': 'subscribe',
            'channels': [{'name': channel, 'product_ids': [product_ids]}],
            'signature': signature_b64,
            'key': SANDBOX_API_KEY,
            'passphrase': SANDBOX_PASSPHRASE,
            'timestamp': timestamp
        })

        while True:
            try:
                async with websockets.connect(URI, ping_interval=None) as websocket:
                    await websocket.send(subscribe_message)
                    while True:
                        response = await websocket.recv()
                        json_response = json.loads(response)
                        print(json_response)
                        if i<2: 
                            # skip first two loops since it returns records with keys=['type', 'channels'] and ['type', 'product_id', 'asks', 'bids', 'time']
                            i+=1
                            continue
                        key = CoinbaseRecordKey(product_id=json_response['product_id']) # keys=['type', 'product_id', 'changes', 'time']
                        value = CoinbaseRecord(arr=[json_response['type'], json_response['product_id'], json_response['changes'], json_response['time']])
                        try:
                            self.producer.produce(topic=topic,
                                        key=self.key_serializer(key, SerializationContext(topic=topic,
                                                                                            field=MessageField.KEY)),
                                        value=self.value_serializer(value, SerializationContext(topic=topic,
                                                                                                field=MessageField.VALUE)),
                                        on_delivery=delivery_report)
                        except Exception as e:
                            print(f"Exception while producing record - {value}: {e}")

            except (websockets.exceptions.ConnectionClosedError, websockets.exceptions.ConnectionClosedOK):
                print('Connection closed, retrying..')
                await asyncio.sleep(1)






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
        'schema.key': COINBASE_KEY_SCHEMA_PATH,
        'schema.value': COINBASE_VALUE_SCHEMA_PATH
    }

    producer = CoinbaseAvroProducer(props=config)

    # coinbase_records = producer.read_records(resource_path=INPUT_DATA_PATH)
    # producer.publish(topic=KAFKA_TOPIC, records=coinbase_records)
    try:
        asyncio.run(producer.publish(topic=KAFKA_TOPIC, channel='level2', product_ids='BTC-USD'))
    except KeyboardInterrupt:
        print("Exiting WebSocket..")
    
    

