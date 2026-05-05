import logging
from libprobe.asset import Asset
from libprobe.check import Check
from ..utils import get_token, get_analytics


async def get_cpu_analytics(asset: Asset, config: dict, token: str):
    dataset = 'cpu.utilization'
    data = await get_analytics(asset, config, token, dataset)

    # this already should be an integer, just to be sure
    cpu_percent = int(data['data']['data']['value'])

    items = [{
        'name': 'cpu.utilization',  # str
        'percentage': cpu_percent,  # int
    }]

    state = {'utilization': items}
    return state


class CheckCpu(Check):
    key = 'cpu'
    unchanged_eol = 0

    @staticmethod
    async def run(asset: Asset, local_config: dict, config: dict) -> dict:

        token = await get_token(asset, local_config, config)
        state = await get_cpu_analytics(asset, config, token)
        return state
