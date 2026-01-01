import pytest
from app.services.factory import get_provider
from app.services.minimax import MinimaxProvider
from app.services.volcengine_tts import VolcengineProvider

def test_get_minimax_provider(mocker):
    mocker.patch('app.config.config_manager.get_all', return_value={
        'active_provider': 'minimax',
        'minimax': {'api_key': 'key', 'group_id': 'group'},
        'voices': {'minimax': []}
    })
    provider = get_provider()
    assert isinstance(provider, MinimaxProvider)
    assert provider.api_key == 'key'

def test_get_volcengine_provider(mocker):
    mocker.patch('app.config.config_manager.get_all', return_value={
        'active_provider': 'volcengine',
        'volcengine': {'app_id': 'id', 'access_token': 'token', 'secret_key': 'secret', 'cluster': 'cluster'},
        'voices': {'volcengine': []}
    })
    provider = get_provider()
    assert isinstance(provider, VolcengineProvider)
    assert provider.app_id == 'id'

def test_get_unknown_provider(mocker):
    mocker.patch('app.config.config_manager.get_all', return_value={
        'active_provider': 'unknown',
    })
    with pytest.raises(ValueError, match="Unknown provider"):
        get_provider()
