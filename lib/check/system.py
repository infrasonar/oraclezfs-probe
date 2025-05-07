import logging
import aiohttp
import datetime
from typing import Optional
from libprobe.asset import Asset
from ..utils import get_token, DEF_API_VERSION, DEF_SECURE, DEF_PORT
from ..connector import get_connector


def dt(date_string: Optional[str]) -> Optional[int]:
    return None if date_string is None else \
        int(datetime.datetime.fromisoformat(date_string).timestamp())


async def get_version(asset: Asset, check_config: dict, token: str):
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
        f'/api/system/{api_version}/version'
    )
    logging.info(f'GET {url}')

    async with aiohttp.ClientSession(connector=get_connector()) as session:
        async with session.get(url, headers=headers, ssl=False) as resp:
            assert resp.status // 100 == 2, \
                f'response status code: {resp.status}. reason: {resp.reason}.'
            data = await resp.json()

    version = data['version']

    item = {
        'name': 'version_info',
        'nodename': version.get('nodename'),  # str?
        'mkt_product': version.get('mkt_product'),  # str?
        'product': version.get('product'),  # str?
        'version': version.get('version'),  # str?
        'install_time': dt(version.get('install_time')),  # int?
        'update_time': dt(version.get('update_time')),  # int?
        'boot_time': dt(version.get('boot_time')),  # int?
        'asn': version.get('asn'),  # str?
        'csn': version.get('csn'),  # str?
        'part': version.get('part'),  # str?
        'urn': version.get('urn'),  # str?
        'navname': version.get('navname'),  # str?
        'navagent': version.get('navagent'),  # str?
        'http': version.get('http'),  # str?
        'ssl': version.get('ssl'),  # str?
        'ak_version': version.get('ak_version'),  # str?
        'ak_release': version.get('ak_release'),  # str?
        'os_version': version.get('os_version'),  # str?
        'bios_version': version.get('bios_version'),  # str?
        'sp_version': version.get('sp_version'),  # str?
    }

    return {'version': [item]}


async def check_system(
        asset: Asset,
        asset_config: dict,
        check_config: dict) -> dict:
    token = await get_token(asset, asset_config, check_config)
    state = await get_version(asset, check_config, token)
    return state
