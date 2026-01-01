from typing import Any, Dict
from app.config import config_manager
from app.services.minimax import MinimaxProvider
from app.services.volcengine_tts import VolcengineProvider
from app.services.base import TTSProvider

def get_provider() -> TTSProvider:
    config: Dict[str, Any] = config_manager.get_all()
    provider_name: str = config.get('active_provider', 'minimax')

    if provider_name == 'minimax':
        return MinimaxProvider(
            api_key=config['minimax'].get('api_key'),
            group_id=config['minimax'].get('group_id'),
            voices=config['voices'].get('minimax', [])
        )
    elif provider_name == 'volcengine':
        return VolcengineProvider(
            app_id=config['volcengine'].get('app_id'),
            access_token=config['volcengine'].get('access_token'),
            secret_key=config['volcengine'].get('secret_key'),
            cluster=config['volcengine'].get('cluster'),
            voices=config['voices'].get('volcengine', [])
        )
    else:
        raise ValueError(f"Unknown provider: {provider_name}")
