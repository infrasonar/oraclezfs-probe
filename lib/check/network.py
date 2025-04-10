import logging
import aiohttp
from libprobe.asset import Asset
from ..utils import get_token, DEF_API_VERSION, DEF_SECURE, DEF_PORT
from ..connector import get_connector


async def get_network(asset: Asset, check_config: dict, token: str):
    state = {}
    address = check_config.get('address')
    if not address:
        address = asset.name
    headers = {'X-Auth-Session': token}
    api_version = check_config.get('version', DEF_API_VERSION)
    secure = check_config.get('secure', DEF_SECURE)
    port = check_config.get('port', DEF_PORT)

    protocol = 'https' if secure else 'http'

    ##############################
    # Routes
    ##############################
    url = (
        f'{protocol}://{address}:{port}'
        f'/api/network/{api_version}/routes'
    )
    logging.info(f'GET {url}')

    async with aiohttp.ClientSession(connector=get_connector()) as session:
        async with session.get(url, headers=headers, ssl=False) as resp:
            assert resp.status // 100 == 2, \
                f'response status code: {resp.status}. reason: {resp.reason}.'
            data = await resp.json()

    routes = []
    for route in data['routes']:
        routes.append({
            'name': route['href'],  # str
            'destination': route['destination'],  # str
            'family': route['family'],  # str
            'gateway': route['gateway'],  # str
            'interface': route['interface'],  # str
            'mask': route.get('mask'),  # int?
            'status': route.get('status'),  # str?
            'type': route['type'],  # str
        })

    ##############################
    # Devices
    ##############################
    url = (
        f'{protocol}://{address}:{port}'
        f'/api/network/{api_version}/devices'
    )
    logging.info(f'GET {url}')

    async with aiohttp.ClientSession(connector=get_connector()) as session:
        async with session.get(url, headers=headers, ssl=False) as resp:
            assert resp.status // 100 == 2, \
                f'response status code: {resp.status}. reason: {resp.reason}.'
            data = await resp.json()

    devices = []
    for device in data['devices']:
        devices.append({
            'name': device['device'],  # str
            'active': device['active'],  # bool
            'duplex': device['duplex'],  # str
            'factory_mac': device['factory_mac'],  # str
            'media': device['media'],  # str
            'speed': device['speed'],  # str (example: 1000 Mbit/s)
            'up': device['up'],  # bool
        })

    ##############################
    # Interfaces
    ##############################
    url = (
        f'{protocol}://{address}:{port}'
        f'/api/network/{api_version}/interfaces'
    )
    logging.info(f'GET {url}')

    async with aiohttp.ClientSession(connector=get_connector()) as session:
        async with session.get(url, headers=headers, ssl=False) as resp:
            assert resp.status // 100 == 2, \
                f'response status code: {resp.status}. reason: {resp.reason}.'
            data = await resp.json()

    interfaces = []
    for iface in data['interfaces']:
        interfaces.append({
            'name': iface['interface'],  # str
            'admin': iface['admin'],  # bool
            'class': iface['class'],  # str
            'curaddrs': iface['curaddrs'],  # list str
            'enable': iface['enable'],  # bool
            'label': iface['label'],  # str
            'links': iface['links'],  # list str
            'state': iface['state'],  # str (example: up)
            'v4addrs': iface['v4addrs'],  # list str
            'v4dhcp': iface['v4dhcp'],  # bool
            'v6addrs': iface['v6addrs'],  # list str
            'v6dhcp': iface['v6dhcp'],  # bool
        })

    state['devices'] = devices
    state['interfaces'] = interfaces
    state['routes'] = routes

    return state


async def check_network(
        asset: Asset,
        asset_config: dict,
        check_config: dict) -> dict:
    token = await get_token(asset, asset_config, check_config)
    state = await get_network(asset, check_config, token)
    return state
