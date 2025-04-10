import logging
import aiohttp
from dateutil import parser
from libprobe.asset import Asset
from ..utils import get_token, DEF_API_VERSION, DEF_SECURE, DEF_PORT
from ..connector import get_connector


async def get_problems(asset: Asset, check_config: dict, token: str):
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
        f'/api/problem/{api_version}/problems'
    )

    logging.info(f'GET {url}')

    async with aiohttp.ClientSession(connector=get_connector()) as session:
        async with session.get(url, headers=headers, ssl=False) as resp:
            assert resp.status // 100 == 2, \
                f'response status code: {resp.status}. reason: {resp.reason}.'
            data = await resp.json()

    problems = []
    for problem in data['problems']:
        try:
            timestr = problem.get('diagnosed', problem.get('timestamp'))
            timestamp = int(parser.parse(timestr).timestamp())
        except Exception:
            timestamp = None

        problems.append({
            'name': problem['uuid'],  # str
            'code': problem['code'],  # str
            'description': problem['description'],  # str
            'severity': problem['severity'],  # str
            'type': problem['type'],  # str
            'impact': problem.get('impact'),  # str?
            'action': problem.get('action'),  # str?
            'response': problem.get('response'),  # str?
            'repairable': problem.get('repairable'),  # bool?
            'timestamp': timestamp,  # int?
        })

    state = {'problems': problems}
    return state


async def check_problems(
        asset: Asset,
        asset_config: dict,
        check_config: dict) -> dict:
    token = await get_token(asset, asset_config, check_config)
    state = await get_problems(asset, check_config, token)
    return state
