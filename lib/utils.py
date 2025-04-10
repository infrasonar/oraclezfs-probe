import asyncio
import aiohttp
import time
import logging
from typing import Optional
from collections import defaultdict
from libprobe.asset import Asset
from .connector import get_connector

DEF_API_VERSION = 'v2'  # v1 or v2
DEF_SECURE = True
DEF_PORT = 215

# MAX_TOKEN_AGE is usually 15 minutes, we choose 12 minutes to be safe
MAX_TOKEN_AGE = 720

# Token registration; Prevent new tokens for each request
_tokens: dict[int, tuple[float, str]] = dict()
_locks: dict[int, asyncio.Lock] = defaultdict(asyncio.Lock)


async def get_token(
        asset: Asset,
        asset_config: dict,
        check_config: dict) -> str:
    async with _locks[asset.id]:
        token_reg = _tokens.get(asset.id)
        if token_reg is not None:
            ts, token = token_reg
            if ts + MAX_TOKEN_AGE > time.time():
                return token

        address = check_config.get('address')
        if not address:
            address = asset.name

        api_version = check_config.get('version', DEF_API_VERSION)
        secure = check_config.get('secure', DEF_SECURE)
        port = check_config.get('port', DEF_PORT)

        try:
            username = asset_config['username']
            password = asset_config['password']
        except KeyError:
            raise Exception(
                'missing username or password in local asset config')

        headers = {
            'X-Auth-User': username,
            'X-Auth-Key': password
        }
        protocol = 'https' if secure else 'http'
        url = f'{protocol}://{address}:{port}/api/access/{api_version}'

        logging.info(f'POST {url}')

        async with aiohttp.ClientSession(connector=get_connector()) as session:
            async with session.post(url, headers=headers, ssl=False) as resp:
                assert resp.status // 100 == 2, \
                    f'response status code: {resp.status}. ' \
                    f'reason: {resp.reason}.'
                token = resp.headers.get('X-Auth-Session')
                assert token, 'missing `X-Auth-Session` token in response'

        # Resister the token with the current time-stamp
        _tokens[asset.id] = time.time(), token

        return token


def as_int(d: dict, k: str) -> Optional[int]:
    x = d.get(k)
    if x is not None:
        return int(x)


def as_float(d: dict, k: str) -> Optional[float]:
    x = d.get(k)
    if x is not None:
        return float(x)


async def get_analytics(asset: Asset, check_config: dict, token: str,
                        dataset: str) -> dict:
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
        f'/api/analytics/{api_version}/datasets/{dataset}/data?span=minute'
    )

    logging.info(f'GET {url}')

    async with aiohttp.ClientSession(connector=get_connector()) as session:
        async with session.get(url, headers=headers, ssl=False) as resp:
            assert resp.status // 100 == 2, \
                f'response status code: {resp.status}. reason: {resp.reason}.'
            data = await resp.json()

    return data
