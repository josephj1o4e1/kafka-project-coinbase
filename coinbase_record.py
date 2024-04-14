from typing import List, Dict


class CoinbaseRecord:

    def __init__(self, arr: List[str]):
        self.type = arr[0]
        self.product_id = arr[1]
        self.changes = arr[2]
        self.time = arr[3]

    @classmethod
    def from_dict(cls, d: Dict):
        return cls(arr=[
            d['type'],
            d['product_id'],
            d['changes'],
            d['time']
        ]
        )

    def __repr__(self):
        return f'{self.__class__.__name__}: {self.__dict__}'


def dict_to_coinbase_record(obj, ctx):
    if obj is None:
        return None

    return CoinbaseRecord.from_dict(obj)


def coinbase_record_to_dict(coinbase_record: CoinbaseRecord, ctx):
    return coinbase_record.__dict__
