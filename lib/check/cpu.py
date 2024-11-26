import logging
from libprobe.asset import Asset
from ..utils import get_token, get_analytics


async def get_cpu_analytics(asset: Asset, check_config: dict, token: str):
    dataset = 'cpu.utilization'
    data = await get_analytics(asset, check_config, token, dataset)

    # this already should be an integer, just to be sure
    cpu_percent = int(data['data']['data']['value'])

    items = [{
        'name': 'cpu.utilization',  # str
        'percentage': cpu_percent,  # int
    }]

    state = {'utilization': items}
    return state


async def check_cpu(
        asset: Asset,
        asset_config: dict,
        check_config: dict) -> dict:
    token = await get_token(asset, asset_config, check_config)
    state = await get_cpu_analytics(asset, check_config, token)
    return state
