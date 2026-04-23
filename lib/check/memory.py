import logging
import aiohttp
from libprobe.asset import Asset
from libprobe.check import Check
from ..utils import get_token, DEF_API_VERSION, DEF_SECURE, DEF_PORT
from ..connector import get_connector


async def get_memory(asset: Asset, config: dict, token: str):
    address = config.get('address')
    if not address:
        address = asset.name
    headers = {'X-Auth-Session': token}
    api_version = config.get('version', DEF_API_VERSION)
    secure = config.get('secure', DEF_SECURE)
    port = config.get('port', DEF_PORT)

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


class CheckMemory(Check):
    key = 'memory'
    unchanged_eol = 0

    @staticmethod
    async def run(asset: Asset, local_config: dict, config: dict) -> dict:

        token = await get_token(asset, local_config, config)
        state = await get_memory(asset, config, token)
        return state
