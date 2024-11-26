import logging
import aiohttp
from dateutil import parser
from datetime import datetime, timedelta
from libprobe.asset import Asset
from libprobe.exceptions import IncompleteResultException
from ..utils import get_token, DEF_API_VERSION, DEF_SECURE, DEF_PORT


DEF_ALERT_HOURS = 24  # return alers from the past 24 hours


async def get_logs_alert(asset: Asset, check_config: dict, token: str):
    address = check_config.get('address')
    if not address:
        address = asset.name
    headers = {'X-Auth-Session': token}
    api_version = check_config.get('version', DEF_API_VERSION)
    secure = check_config.get('secure', DEF_SECURE)
    port = check_config.get('port', DEF_PORT)
    alert_hours = check_config.get('hours', DEF_ALERT_HOURS)

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


async def check_alerts(
        asset: Asset,
        asset_config: dict,
        check_config: dict) -> dict:
    token = await get_token(asset, asset_config, check_config)
    state = await get_logs_alert(asset, check_config, token)
    return state
