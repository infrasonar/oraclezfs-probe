import aiohttp
import time
import logging
from dateutil import parser
from datetime import datetime, timedelta
from libprobe.asset import Asset
from libprobe.exceptions import IncompleteResultException


DEFAULT_API_VERSION = 'v2'  # v1 or v2
DEFAULT_SECURE = True
DEFAULT_PORT = 215
DEFAULT_ALERT_HOURS = 24  # return alers from the past 24 hours

# MAX_TOKEN_AGE is usually 15 minutes, we choose 12 minutes to be safe
MAX_TOKEN_AGE = 720

# Token registration; Prevent new tokens for each request
_tokens: dict[int, tuple[float, str]] = dict()


async def get_token(
        asset: Asset,
        asset_config: dict,
        check_config: dict) -> str:

    token_reg = _tokens.get(asset.id)
    if token_reg is not None:
        ts, token = token_reg
        if ts + MAX_TOKEN_AGE > time.time():
            return token

    address = check_config.get('address')
    if not address:
        address = asset.name

    api_version = check_config.get('version', DEFAULT_API_VERSION)
    secure = check_config.get('secure', DEFAULT_SECURE)
    port = check_config.get('port', DEFAULT_PORT)

    try:
        username = asset_config['username']
        password = asset_config['password']
    except KeyError:
        raise Exception('missing username or password in local asset config')

    headers = {
        'X-Auth-User': username,
        'X-Auth-Key': password
    }
    protocol = 'https' if secure else 'http'
    url = f'{protocol}://{address}:{port}/api/access/{api_version}'

    logging.debug(f'Headers: {headers}')
    logging.info(f'POST {url}')

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, ssl=False) as resp:
            assert resp.status // 100 == 2, \
                f'response status code: {resp.status}. reason: {resp.reason}.'
            token = resp.headers.get('X-Auth-Session')
            assert token, 'missing `X-Auth-Session` token in response'

    # Resister the token with the current time-stamp
    _tokens[asset.id] = time.time(), token

    return token


async def get_logs_alert(asset: Asset, check_config: dict, token: str):
    address = check_config.get('address')
    if not address:
        address = asset.name
    headers = {'X-Auth-Session': token}
    api_version = check_config.get('version', DEFAULT_API_VERSION)
    secure = check_config.get('secure', DEFAULT_SECURE)
    port = check_config.get('port', DEFAULT_PORT)
    alert_hours = check_config.get('hours', DEFAULT_ALERT_HOURS)

    start = (datetime.utcnow() - timedelta(hours=alert_hours))
    index = start.isoformat(sep='T', timespec='seconds') + 'Z'

    protocol = 'https' if secure else 'http'
    url = (
        f'{protocol}://{address}:{port}'
        f'/api/log/{api_version}/logs/alert?start={index}'
    )

    logging.info(f'GET {url}')

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, ssl=False) as resp:
            assert resp.status // 100 == 2, \
                f'response status code: {resp.status}. reason: {resp.reason}.'
            data = await resp.json()

    uuids = set()  # TODO: remove if 100% sure uuids are unique
    logs = []
    state = {}

    if data:
        for log in data['logs']:
            log['timestamp'] = int(parser.parse(log['timestamp']).timestamp())
            uuid = log.pop('uuid')
            log['name'] = uuid
            if uuid in uuids:
                logging.error('UUID not unique')
            else:
                logs.append(log)
            uuids.add(uuid)

    state['logs'] = logs
    state['records'] = [{
        'name': 'count',
        'count': len(logs),
        'since': int(start.timestamp()),
        'hours': alert_hours,
    }]

    if len(logs) != len(uuids):
        raise IncompleteResultException('UUIDs are not unique', result=state)

    return state
