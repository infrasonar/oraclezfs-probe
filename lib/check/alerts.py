import logging
from libprobe.asset import Asset
from ..utils import get_token, get_logs_alert


async def check_alerts(
        asset: Asset,
        asset_config: dict,
        check_config: dict) -> dict:
    try:
        token = await get_token(asset, asset_config, check_config)
    except Exception:
        logging.exception('Failed to retrieve token')
        raise

    try:
        state = await get_logs_alert(asset, check_config, token)
    except Exception:
        logging.exception('Failed to get alerts')
        raise

    return state
