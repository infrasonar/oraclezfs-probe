import logging
import aiohttp
from libprobe.asset import Asset
from ..utils import (
    get_token, as_int, as_float, DEF_API_VERSION, DEF_SECURE, DEF_PORT)
from ..connector import get_connector


async def get_luns(asset: Asset, check_config: dict, token: str):
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
        f'/api/storage/{api_version}/luns'
    )

    logging.info(f'GET {url}')

    async with aiohttp.ClientSession(connector=get_connector()) as session:
        async with session.get(url, headers=headers, ssl=False) as resp:
            assert resp.status // 100 == 2, \
                f'response status code: {resp.status}. reason: {resp.reason}.'
            data = await resp.json()

    luns = []
    for lun in data['luns']:
        usage = lun.get('usage', {})
        stmfguid = lun.get('stmfguid', lun.get('lunguid'))

        luns.append({
            'name': lun['canonical_name'],  # str
            'sparse': lun['sparse'],  # bool
            'volsize': int(lun['volsize']),  # int
            'volblocksize': int(lun['volblocksize']),  # int
            'usage_available': as_int(usage, 'available'),  # int?
            'usage_total': as_int(usage, 'total'),  # int?
            'usage_data': as_int(usage, 'data'),  # int?
            'usage_compressratio': as_float(usage, 'compressratio'),  # float?
            'usage_snapshots': as_float(usage, 'snapshots'),  # float?
            'usage_loading': usage.get('loading'),  # bool?
            'status': lun.get('status'),  # str
            'stmfguid': stmfguid,  # str
        })

    state = {'luns': luns}
    return state


async def check_storage(
        asset: Asset,
        asset_config: dict,
        check_config: dict) -> dict:
    token = await get_token(asset, asset_config, check_config)
    state = await get_luns(asset, check_config, token)
    return state
