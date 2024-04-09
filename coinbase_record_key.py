from typing import Dict


class CoinbaseRecordKey:
    def __init__(self, product_id):
        self.product_id = product_id

    @classmethod
    def from_dict(cls, d: Dict):
        return cls(product_id=d['product_id'])

    def __repr__(self):
        return f'{self.__class__.__name__}: {self.__dict__}'


def dict_to_coinbase_record_key(obj, ctx):
    if obj is None:
        return None

    return CoinbaseRecordKey.from_dict(obj)


def coinbase_record_key_to_dict(coinbase_record_key: CoinbaseRecordKey, ctx):
    return coinbase_record_key.__dict__
