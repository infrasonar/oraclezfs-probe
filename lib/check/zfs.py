from libprobe.asset import Asset
from ..utils import get_token



async def check_zfs(
        asset: Asset,
        asset_config: dict,
        check_config: dict) -> dict:

    token = await get_token(asset, asset_config, check_config)

    ...

    return {}
