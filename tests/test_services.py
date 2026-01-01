import pytest
from app.services.minimax import MinimaxProvider
from app.services.volcengine_tts import VolcengineProvider

def test_minimax_generate_sync_missing_key():
    provider = MinimaxProvider(api_key="")
    with pytest.raises(ValueError, match="Missing API Key"):
        provider.generate_sync("test", "voice")

def test_minimax_generate_sync(mocker):
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.json.return_value = {
        'base_resp': {'status_code': 0},
        'data': {'audio': '48656c6c6f'} # "Hello" in hex
    }

    provider = MinimaxProvider(api_key="test_key")
    result = provider.generate_sync("text", "voice_id")

    assert result == b'Hello'
    mock_post.assert_called_once()

def test_volcengine_generate_sync(mocker):
    mock_request = mocker.patch('requests.request')
    mock_request.return_value.json.return_value = {
        'code': 3000,
        'data': 'SGVsbG8=' # "Hello" in base64
    }

    provider = VolcengineProvider(app_id="id", access_token="token")
    result = provider.generate_sync("text", "voice_id")

    assert result == b'Hello'
    mock_request.assert_called_once()
