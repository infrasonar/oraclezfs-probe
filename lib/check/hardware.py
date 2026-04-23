import logging
import aiohttp
from libprobe.asset import Asset
from libprobe.check import Check
from ..utils import get_token, DEF_API_VERSION, DEF_SECURE, DEF_PORT
from ..connector import get_connector


async def get_hardware(asset: Asset, check_config: dict, token: str):
    address = check_config.get('address')
    if not address:
        address = asset.name
    headers = {'X-Auth-Session': token}
    api_version = check_config.get('version', DEF_API_VERSION)
    secure = check_config.get('secure', DEF_SECURE)
    port = check_config.get('port', DEF_PORT)

    protocol = 'https' if secure else 'http'

    ##############################
    # Chassis
    ##############################
    url = (
        f'{protocol}://{address}:{port}'
        f'/api/hardware/{api_version}/chassis'
    )
    logging.info(f'GET {url}')

    async with aiohttp.ClientSession(connector=get_connector()) as session:
        async with session.get(url, headers=headers, ssl=False) as resp:
            assert resp.status // 100 == 2, \
                f'response status code: {resp.status}. reason: {resp.reason}.'
            data = await resp.json()

    names = set()
    chassis = []
    for item in data['chassis']:
        name = item['name']
        if name in names:
            name = item['href']  # this is unique and never equal to a name
        else:
            names.add(name)

        chassis.append({
            'name': name,  # str
            'faulted': item['faulted'],  # bool
            'manufacturer': item['manufacturer'],  # str
            'model': item['model'],  # str
            'serial': item['serial'],  # str
            'type': item['type'],  # str
            'rpm': item.get('rpm'),  # int?
            'part': item.get('part'),  # str?
            'locate': item.get('locate'),  # bool?
        })

    return {'chassis': chassis}


class CheckHardware(Check):
    key = 'hardware'
    unchanged_eol = 14400

    @staticmethod
    async def run(asset: Asset, local_config: dict, config: dict) -> dict:

        token = await get_token(asset, local_config, config)
        state = await get_hardware(asset, config, token)
        return state
