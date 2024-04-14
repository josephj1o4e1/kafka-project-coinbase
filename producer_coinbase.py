import os
import csv
from time import sleep
from typing import Dict, List

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField

from coinbase_record_key import CoinbaseRecordKey, coinbase_record_key_to_dict
from coinbase_record import CoinbaseRecord, coinbase_record_to_dict

import asyncio, base64, hashlib, hmac, json, os, time, websockets

from dotenv import load_dotenv
load_dotenv()

# INPUT_DATA_PATH = os.environ["INPUT_DATA_PATH"]
# Coinbase
SANDBOX_API_KEY = str(os.environ.get('SANDBOX_API_KEY'))
SANDBOX_PASSPHRASE = str(os.environ.get('SANDBOX_PASSPHRASE'))
SANDBOX_SECRET_KEY = str(os.environ.get('SANDBOX_SECRET_KEY'))
# URI = 'wss://ws-feed-public.sandbox.exchange.coinbase.com'
URI = 'wss://ws-direct.sandbox.exchange.coinbase.com'
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
# all_product_ids = ['POND-USDC', 'VOXEL-USDC', 'DOT-USDT', 'SYN-USD', 'AXS-USD', 'WBTC-BTC', 'AVAX-USDC', 'AKT-USDC', 'FORTH-USD', 'FLOW-USD', 'ABT-USDC', 'MINA-USDT', 'CELR-USDC', 'TRAC-USDC', 'IDEX-USD', 'ACS-USD', 'BAL-USD', 'SEI-USDC', 'BCH-EUR', 'CRO-USDT', 'ATOM-USDC', 'RNDR-USDT', 'ZRX-USD', 'SWFTC-USD', 'SNX-GBP', 'APE-USD', 'WCFG-USDC', 'CVX-USD', 'MSOL-USDC', 'T-USDC', 'EUROC-EUR', 'GMT-USDC', 'CGLD-GBP', 'XTZ-GBP', 'LSETH-USDC', 'FORT-USD', 'ATOM-BTC', 'RNDR-EUR', 'C98-USD', 'ROSE-USDC', 'BADGER-USD', 'ILV-USDC', 'INV-USDC', 'LOKA-USDC', 'SUKU-USD', 'HOPR-USDC', 'AGLD-USD', 'TRB-USDC', 'LINK-EUR', 'MAGIC-USDC', 'ZETA-USDC', 'LPT-USD', 'SPELL-USD', '1INCH-USDC', 'USDC-EUR', 'CRV-USDC', 'SUPER-USDC', 'SOL-USDC', 'API3-USDC', 'AXS-USDC', 'ATOM-EUR', 'HBAR-USD', 'MATH-USDC', 'COVAL-USDC', 'ALGO-BTC', 'YFI-USDC', 'GAL-USD', 'EOS-USDC', 'CHZ-GBP', 'DNT-USD', 'FET-USDC', 'ABT-USD', 'ALGO-GBP', 'FIS-USD', 'CRV-USD', 'BADGER-USDC', 'OGN-USD', 'VOXEL-USD', 'WAXL-USDC', 'ELA-USDC', 'PNG-USDC', 'PRIME-USDC', 'STX-USDC', 'BOBA-USDC', 'GUSD-USDC', 'USDT-EUR', 'MKR-USDC', 'ADA-ETH', 'AAVE-GBP', 'UMA-USD', 'GTC-USD', 'TIA-USDC', 'LTC-USDC', 'MASK-USDT', 'MAGIC-USD', 'ILV-USD', 'INJ-USD', 'XCN-USD', 'PLU-USDC', 'LQTY-USDC', 'CRV-EUR', 'SHPING-USDC', 'SHIB-GBP', 'ANKR-GBP', 'UNI-GBP', 'LOKA-USD', 'DNT-USDC', 'HFT-USD', 'LIT-USDC', 'QNT-USDT', 'AMP-USDC', 'POLS-USDC', 'BIT-USDC', 'MATIC-USDC', 'HIGH-USDC', 'TNSR-USD', 'BLZ-USDC', 'AXS-USDT', 'KSM-USD', 'BAND-USDC', 'SEAM-USDC', 'HOPR-USD', 'DOGE-EUR', 'BCH-USD', 'OXT-USDC', 'ETH-EUR', 'PYUSD-USD', 'CRO-USD', 'LIT-USD', 'CHZ-USD', 'ARKM-USDC', 'CTX-USDC', 'JASMY-USDT', 'ATOM-GBP', 'PRQ-USDC', 'OGN-USDC', 'FARM-USD', 'AAVE-BTC', 'USDT-USD', 'GYEN-USDC', 'AUCTION-USDC', 'RONIN-USDC', 'SYN-USDC', 'YFI-BTC', 'XYO-USD', 'GODS-USDC', 'DEXT-USDC', 'KRL-USD', 'OXT-USD', 'SPA-USD', 'NMR-USD', 'AUDIO-USDC', 'APT-USDT', 'EGLD-USD', 'EGLD-USDC', 'PRO-USD', 'PERP-USD', 'MLN-USDC', 'QI-USDC', 'BAT-USD', 'FORT-USDC', 'ENS-EUR', 'ICP-EUR', 'XTZ-USDC', 'STORJ-USD', 'DIMO-USD', 'BCH-USDC', 'PYR-USD', 'WAMPL-USD', 'RARI-USD', 'DAI-USDC', 'XRP-USDC', 'NEAR-USDC', 'DOGE-GBP', 'DOGE-USD', 'VTHO-USD', 'AERO-USDC', 'ENS-USDC', 'XLM-USD', 'LDO-USDC', 'MINA-USDC', 'RAD-USDC', '1INCH-EUR', 'T-USD', 'XRP-EUR', 'SHIB-EUR', 'XLM-EUR', 'SPELL-USDC', 'FIDA-USD', 'CHZ-USDT', 'MKR-BTC', 'BCH-BTC', 'AUCTION-USD', 'TVK-USD', 'DAR-USDC', 'RONIN-USD', 'ACH-USDC', 'APE-EUR', 'ICP-GBP', 'DIA-USD', 'XLM-USDT', 'ADA-USD', 'HONEY-USD', 'BAL-USDC', 'XTZ-EUR', 'AAVE-USDC', 'LINK-USDC', 'BNT-USDC', 'BONK-USDC', 'MATH-USD', 'CHZ-EUR', 'FLOW-USDC', 'ADA-BTC', 'WAMPL-USDC', 'AVAX-USD', 'ZEC-USDC', 'LRC-BTC', 'XRP-USDT', 'GTC-USDC', 'DASH-USD', 'AAVE-USD', 'ACH-USD', 'ALICE-USD', 'QI-USD', 'MASK-USD', 'ALEPH-USD', 'PNG-USD', 'GAL-USDC', 'AAVE-EUR', 'STX-USD', 'NKN-USD', 'UMA-USDC', 'DESO-USDC', 'LTC-BTC', 'IMX-USD', 'ERN-USD', 'OSMO-USDC', 'TNSR-USDC', 'DOT-EUR', 'ETC-GBP', 'ALEPH-USDC', 'BCH-GBP', 'RBN-USD', 'WBTC-USDC', 'STRK-USD', 'ATOM-USDT', 'PUNDIX-USD', 'EUROC-USD', 'KNC-USDC', 'SOL-BTC', 'ICP-USD', 'SHDW-USDC', 'LTC-USD', 'SHIB-USDT', 'DOT-USD', 'BTRST-USD', 'BAT-BTC', 'JTO-USD', 'ANKR-USDC', 'CHZ-USDC', 'HBAR-USDT', 'ATOM-USD', 'AURORA-USDC', 'SAND-USDC', 'VARA-USD', 'VARA-USDC', 'AUDIO-USD', 'STX-USDT', 'TRAC-USD', 'NEAR-USDT', 'LTC-GBP', 'ALICE-USDC', 'INV-USD', 'ETH-BTC', 'ALGO-USD', 'ETH-USD', 'LPT-USDC', 'RPL-USD', 'RAI-USDC', 'SOL-GBP', 'AXL-USDC', '1INCH-USD', 'FOX-USD', 'CGLD-USDC', 'ROSE-USDT', 'PUNDIX-USDC', 'AIOZ-USDC', 'LINK-USD', 'TRU-USD', 'SEAM-USD', 'SWFTC-USDC', 'LRC-USDT', 'GYEN-USD', 'ENS-USDT', 'OCEAN-USDC', 'ZETA-USD', 'ORCA-USD', 'SUKU-USDC', 'PAX-USD', 'ASM-USDC', 'NCT-USDC', 'LINK-ETH', 'REQ-USDC', 'BAND-USD', 'CELR-USD', 'DOGE-USDC', 'ENJ-USDC', 'WAXL-USD', 'GRT-USD', 'MTL-USD', 'OP-USDT', 'WBTC-USD', 'EOS-USD', 'CBETH-USDC', 'CVC-USD', 'AMP-USD', 'AURORA-USD', 'KRL-USDC', 'EUROC-USDC', 'GMT-USDT', 'SAND-USD', 'CLV-USD', 'GRT-USDC', 'ETH-GBP', 'GRT-EUR', 'GLM-USDC', 'MATIC-BTC', 'POLS-USD', 'VELO-USD', 'ROSE-USD', 'APT-USDC', 'ETH-USDT', 'CVC-USDC', 'NKN-USDC', 'AST-USD', 'DASH-BTC', 'SKL-USD', 'DYP-USDC', 'XCN-USDC', 'ARPA-USD', 'AXS-BTC', 'ADA-USDC', 'HBAR-USDC', 'BONK-USD', 'BTC-GBP', 'USDT-USDC', 'AST-USDC', 'CVX-USDC', 'EOS-EUR', 'HONEY-USDC', 'FIL-GBP', 'ZRX-USDC', 'VET-USDC', 'FX-USD', 'ETH-USDC', 'LCX-USDC', 'DEXT-USD', 'PLU-USD', 'REQ-USD', 'NEAR-USD', 'ARKM-USD', 'INDEX-USD', 'MNDE-USD', 'IOTX-USD', 'JASMY-USDC', 'ANKR-BTC', 'METIS-USDC', 'AXL-USD', 'MATIC-USDT', 'LINK-GBP', 'AVAX-BTC', 'HFT-USDC', 'ORCA-USDC', 'USDT-GBP', 'XLM-USDC', 'ICP-USDT', 'GNO-USDC', 'NCT-USD', 'SPA-USDC', 'ARB-USDC', 'ETC-USD', 'ALGO-EUR', 'CRO-EUR', 'LSETH-USD', 'INJ-USDC', 'QNT-USDC', 'RLC-USD', '1INCH-GBP', 'BOBA-USD', 'KAVA-USD', 'RENDER-USDC', 'HNT-USDC', 'ENJ-BTC', 'API3-USD', 'MANA-USDC', 'DAI-USD', 'DOT-GBP', 'USDC-GBP', 'RENDER-USD', 'DIMO-USDC', 'TIME-USDC', 'UNI-USD', 'SHDW-USD', 'POWR-USDC', 'MSOL-USD', 'SNX-BTC', 'SOL-USD', 'PYR-USDC', 'BAT-EUR', 'ADA-EUR', 'AVT-USD', 'XTZ-USD', 'BAT-ETH', 'MKR-USD', 'C98-USDC', 'VET-USD', 'BLZ-USD', 'BTC-EUR', 'POND-USD', 'KNC-USD', 'TIME-USD', 'DIA-USDC', 'GRT-BTC', 'ONDO-USD', 'IOTX-USDC', 'FIL-BTC', 'MOBILE-USD', 'SKL-USDC', 'GFI-USD', 'DOGE-USDT', 'GNO-USD', 'SUI-USD', 'OSMO-USD', 'OP-USDC', 'ETC-EUR', 'PRIME-USD', 'CLV-USDC', 'SHPING-USD', 'ACS-USDC', 'SNX-USD', 'ICP-USDC', 'ENS-USD', 'MINA-EUR', 'SUSHI-USD', 'LCX-USD', 'LRC-USDC', 'SUPER-USD', 'INDEX-USDC', 'SUI-USDC', 'LINK-BTC', 'RNDR-USDC', 'MASK-USDC', 'RLC-USDC', 'DYP-USD', 'QNT-USD', '00-USD', 'RARI-USDC', 'NMR-USDC', 'ANKR-EUR', 'ASM-USD', 'AVAX-EUR', 'FLR-USD', 'ADA-USDT', 'MINA-USD', 'APT-USD', 'AKT-USD', 'CBETH-ETH', 'WCFG-USD', 'AVAX-USDT', 'XRP-USD', 'LRC-USD', 'GLM-USD', 'XYO-USDC', 'MPL-USDC', 'PERP-USDC', 'COMP-USDC', 'XTZ-BTC', 'FORTH-USDC', 'ALCX-USDC', 'MANA-EUR', 'FLOW-USDT', 'CTSI-USDC', 'KSM-USDC', 'FIS-USDC', 'LINK-USDT', 'MLN-USD', 'COMP-BTC', 'COMP-USD', 'SOL-EUR', 'AGLD-USDC', 'ARB-USD', 'MTL-USDC', 'ARPA-USDC', 'IDEX-USDC', 'UNI-BTC', 'SNX-USDC', 'CTX-USD', 'LDO-USD', 'METIS-USD', 'GUSD-USD', 'FX-USDC', 'DAR-USD', 'SNX-EUR', '1INCH-BTC', 'BNT-USD', 'FIDA-USDC', 'YFI-USD', 'MEDIA-USDC', 'AIOZ-USD', 'ALGO-USDC', 'COTI-USD', 'UNI-USDC', 'ANKR-USD', 'SEI-USD', 'HNT-USD', 'BAL-BTC', 'TVK-USDC', 'CGLD-USD', 'BICO-USDT', 'PYUSD-USDC', 'DOT-BTC', 'ORN-USDC', 'UNI-EUR', 'ERN-USDC', 'RNDR-USD', 'SAND-USDT', 'AXS-EUR', 'FIL-EUR', 'ETH-DAI', 'BICO-EUR', 'MPL-USD', 'RAI-USD', 'MOBILE-USDC', 'ENJ-USD', 'IMX-USDC', 'MUSE-USD', 'VTHO-USDC', 'EOS-BTC', 'LSETH-ETH', 'SOL-ETH', 'VELO-USDC', 'BIGTIME-USD', 'RBN-USDC', 'MANA-ETH', 'BTC-USDC', 'GMT-USD', 'BIT-USD', 'AVT-USDC', 'TIA-USD', 'CRV-GBP', 'GST-USDC', 'FOX-USDC', 'ORN-USD', 'MASK-GBP', 'MDT-USD', 'GRT-GBP', 'OCEAN-USD', '00-USDC', 'AERGO-USDC', 'BLUR-USD', 'ETC-BTC', 'APE-USDC', 'ICP-BTC', 'MUSE-USDC', 'FARM-USDC', 'MEDIA-USD', 'BTRST-USDC', 'ENJ-USDT', 'BTC-USD', 'JASMY-USD', 'ONDO-USDC', 'FET-USD', 'ADA-GBP', 'RARE-USDC', 'ALCX-USD', 'BAT-USDC', 'PRQ-USD', 'CRV-BTC', 'FLR-USDC', 'GFI-USDC', 'AERO-USD', 'ZEN-USD', 'ELA-USD', 'MDT-USDC', 'CRO-USDC', 'GODS-USD', 'CGLD-BTC', 'AERGO-USD', 'DOGE-BTC', 'PRO-USDC', 'GHST-USD', 'LTC-EUR', 'COVAL-USD', 'FIL-USDC', 'TRB-USD', 'APE-USDT', 'SUSHI-USDC', 'MATIC-USD', 'TRU-USDC', 'ZEN-USDC', 'BLUR-USDC', 'STRK-USDC', 'RPL-USDC', 'BICO-USDC', 'MATIC-EUR', 'MATIC-GBP', 'CBETH-USD', 'PAX-USDC', 'POWR-USD', 'SHIB-USD', 'COTI-USDC', 'LQTY-USD', 'MANA-USD', 'BIGTIME-USDC', 'DOT-USDC', 'MASK-EUR', 'CGLD-EUR', 'DASH-USDC', 'FET-USDT', 'OP-USD', 'MNDE-USDC', 'ETC-USDC', 'CTSI-USD', 'HIGH-USD', 'ZEC-USD', 'BICO-USD', 'GHST-USDC', 'STORJ-USDC', 'KAVA-USDC', 'JTO-USDC', 'GST-USD', 'RARE-USD', 'IMX-USDT', 'XLM-BTC', 'SOL-USDT', 'SHIB-USDC', 'FIL-USD', 'RAD-USD', 'DESO-USD', 'BTC-USDT', 'ZEC-BTC', 'MANA-BTC']

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

    
    
    async def publish(self, topic: str, channel: str='level2', product_ids: List[str]=['BTC-USD']):
        signature_b64, timestamp = await generate_signature()
        subscribe_message = json.dumps({
            'type': 'subscribe',
            'channels': [{'name': channel, 'product_ids': product_ids}],
            'signature': signature_b64,
            'key': SANDBOX_API_KEY,
            'passphrase': SANDBOX_PASSPHRASE,
            'timestamp': timestamp
        })

        while True:
            try:
                async with websockets.connect(URI, ping_interval=None) as websocket:
                    await websocket.send(subscribe_message)
                    i=0
                    while True:
                        response = await websocket.recv()
                        json_response = json.loads(response)
                        print(f'coinbase json resp = {json_response}')
                        if i<len(product_ids)+1: 
                            # skip first two loops since it returns records with keys=['type', 'channels'] and ['type', 'product_id', 'asks', 'bids', 'time']
                            i+=1
                            continue
                        key = CoinbaseRecordKey(product_id=json_response['product_id']) # keys=['type', 'product_id', 'changes', 'time']
                        
                        # for change in json_response['changes']: # unnest array of arrays to separate rows (BigQuery doesn't accept nested arrays for avro files), but using KSQL to unnest might be better. 
                        #     value = CoinbaseRecord(arr=[json_response['type'], json_response['product_id'], change, json_response['time']])
                        value = CoinbaseRecord(arr=[json_response['type'], json_response['product_id'], json_response['changes'], json_response['time']])
                        try:
                            self.producer.produce(topic=topic,
                                        key=self.key_serializer(key, SerializationContext(topic=topic,
                                                                                            field=MessageField.KEY)),
                                        value=self.value_serializer(value, SerializationContext(topic=topic,
                                                                                                field=MessageField.VALUE)),
                                        on_delivery=delivery_report)
                            self.producer.poll(0) # !! timeout=0: triggers the sending of messages from the internal buffer to the Kafka cluster, and serve (won't serve until conditions met. for example, accumulated>=batch.num.messages) any delivery reports from previous produce-calls, or none, without blocking.
                        except Exception as e:
                            print(f"Exception while producing record - {value}: {e}")

            except (websockets.exceptions.ConnectionClosedError, websockets.exceptions.ConnectionClosedOK):
                print('Connection closed, retrying..')
                await asyncio.sleep(1)
            self.producer.flush()
            await asyncio.sleep(1)


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
    product_ids = ['BTC-USD', 'BTC-EUR', 'BTC-GBP'] # the only 3 products subscribable for sandbox environment. 
    try:
        asyncio.run(producer.publish(topic=KAFKA_TOPIC, channel='level2', product_ids=product_ids))
    except KeyboardInterrupt:
        print("Exiting WebSocket..")
    
    

