import logging
import aiohttp
from libprobe.asset import Asset
from ..utils import get_token, DEF_API_VERSION, DEF_SECURE, DEF_PORT
from ..connector import get_connector


async def get_memory(asset: Asset, check_config: dict, token: str):
    address = check_config.get('address')
    if not address:
        address = asset.name
    headers = {'X-Auth-Session': token}
    api_version = check_config.get('version', DEF_API_VERSION)
    secure = check_config.get('secure', DEF_SECURE)
    port = check_config.get('port', DEF_PORT)

    protocol = 'https' if secure else 'http'

    url = (
        f'{protocol}://{address}:{port}'
        f'/api/system/{api_version}/memory'
    )
    logging.info(f'GET {url}')

    async with aiohttp.ClientSession(connector=get_connector()) as session:
        async with session.get(url, headers=headers, ssl=False) as resp:
            assert resp.status // 100 == 2, \
                f'response status code: {resp.status}. reason: {resp.reason}.'
            data = await resp.json()

    memory = data['memory']
    item = {
        'name': 'memory',
        'cache': memory['cache'],  # int
        'kernel': memory['kernel'],  # int
        'management': memory['management'],  # int
        'other': memory['other'],  # int
        'unused': memory['unused'],  # int
    }

    return {'memory': [item]}


async def check_memory(
        asset: Asset,
        asset_config: dict,
        check_config: dict) -> dict:
    token = await get_token(asset, asset_config, check_config)
    state = await get_memory(asset, check_config, token)
    return state
