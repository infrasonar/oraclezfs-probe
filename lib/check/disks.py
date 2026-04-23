import logging
import aiohttp
from libprobe.asset import Asset
from libprobe.check import Check
from ..utils import get_token, DEF_API_VERSION, DEF_SECURE, DEF_PORT
from ..connector import get_connector


async def get_disks(asset: Asset, config: dict, token: str):
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
        f'/api/system/{api_version}/disks'
    )
    logging.info(f'GET {url}')

    async with aiohttp.ClientSession(connector=get_connector()) as session:
        async with session.get(url, headers=headers, ssl=False) as resp:
            assert resp.status // 100 == 2, \
                f'response status code: {resp.status}. reason: {resp.reason}.'
            data = await resp.json()

    data = data['disks']

    _root = data.get("root", 0)
    _var = data.get('var', 0)
    _update = data.get('update', 0)
    _stash = data.get('stash', 0)
    _dump = data.get('dump', 0)
    _cores = data.get('cores', 0)
    _unknown = data.get('unknown', 0)
    _free = data.get('free', 0)

    total = sum((_root, _var, _update, _stash, _dump, _cores, _unknown, _free))

    size = {
        'name': 'disks',  # str
        'total': total,  # int
        'free': _free,  # int
        'root': _root,  # int
        'var': _var,  # int
        'update': _update,  # int
        'stash': _stash,  # int
        'dump': _dump,  # int
        'cores': _cores,  # int
        'unknown': _unknown  # int
    }

    disks = []
    for name, disk in data.items():
        if isinstance(disk, dict) and 'label' in disk and 'state' in disk:
            disks.append({
                'name': name,  # str
                'label': disk['label'],  # str
                'state': disk['state'],  # str
            })

    return {
        'size': [size],  # single item
        'disks': disks
    }


class CheckDisks(Check):
    key = 'disks'
    unchanged_eol = 0

    @staticmethod
    async def run(asset: Asset, local_config: dict, config: dict) -> dict:

        token = await get_token(asset, local_config, config)
        state = await get_disks(asset, config, token)
        return state
