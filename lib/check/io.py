import logging
from libprobe.asset import Asset
from libprobe.check import Check
from ..utils import get_token, get_analytics


async def get_io_analytics(asset: Asset, config: dict, token: str):
    # I/O operations per second broken down by disk
    dataset = 'io.ops[disk]'
    data = await get_analytics(asset, config, token, dataset)

    data = data['data']['data']
    ops_disk = []

    for obj in data.get('data', []):
        ops_disk.append({
            'name': obj['key'],  # str
            'ops': int(obj['value']),  # int
        })

    # I/O operations per second broken down by type of operation
    dataset = 'io.ops[op]'
    data = await get_analytics(asset, config, token, dataset)

    data = data['data']['data']
    read, write = 0, 0

    for obj in data.get('data', []):
        if obj['key'] == 'read':
            read = int(obj['value'])  # ensure int
        elif obj['key'] == 'write':
            write = int(obj['value'])  # ensure int
        else:
            # log other than read/write operation
            logging.debug(obj['key'])

    ops_op = [{
        'name': 'io.ops[op]',
        'read': read,  # int
        'write': write,  # int
    }]

    state = {
        'ops_op': ops_op,
        'ops_disk': ops_disk,
    }
    return state


class CheckIo(Check):
    key = 'io'
    unchanged_eol = 14400

    @staticmethod
    async def run(asset: Asset, local_config: dict, config: dict) -> dict:

        token = await get_token(asset, local_config, config)
        state = await get_io_analytics(asset, config, token)
        return state
