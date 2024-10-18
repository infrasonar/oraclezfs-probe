import aiohttp
import time
from libprobe.asset import Asset


DEFAULT_API_VERSION = 'v2'  # v1 or v2
DEFAULT_SECURE = True
DEFAULT_PORT = 215

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

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, ssl=False) as resp:
            assert resp.status // 100 == 2, \
                f'response status code: {resp.status}. reason: {resp.reason}.'
            token = resp.headers.get('X-Auth-Session')
            assert token, 'missing `X-Auth-Session` token in response'

    # Resister the token with the current time-stamp
    _tokens[asset.id] = time.time(), token

    return token
