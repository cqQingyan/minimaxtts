import json
import pytest
from unittest.mock import MagicMock

def test_index_route(client, mocker):
    mocker.patch('app.services.factory.get_provider', return_value=MagicMock(get_voices=lambda: []))
    response = client.get('/')
    assert response.status_code == 200

def test_generate_sync_api(client, mocker):
    # Mocking Factory to return our mock provider is failing because
    # get_provider is called inside the route, but maybe not mocked correctly in the context?
    # Actually, in the previous run it said: "Sync Gen Error: {'error': 'Missing API Key for MiniMax'}"
    # This implies the REAL provider is being called, not the mock.
    # This is because 'from app.services.factory import get_provider' in app/routes.py imports the function object.
    # Patching 'app.services.factory.get_provider' should work IF where it is used (app.routes) looks up the name.
    # BUT if app.routes did "from app.services.factory import get_provider", it has a reference to the function.
    # We must patch 'app.routes.get_provider'.

    mock_provider = MagicMock()
    mock_provider.generate_sync.return_value = b'audio_content'

    mocker.patch('app.routes.get_provider', return_value=mock_provider)

    data = {
        'mode': 'sync',
        'voice_id': 'voice-1',
        'text': 'Hello world'
    }

    response = client.post('/api/generate',
                           json=data)

    if response.status_code != 200:
        print(f"Sync Gen Error: {response.get_json()}")

    assert response.status_code == 200
    assert response.mimetype == 'audio/mpeg'

def test_generate_async_api(client, mocker):
    mock_provider = MagicMock()
    mock_provider.submit_async.return_value = {'task_id': 'task-123'}

    # Same fix here: patch app.routes.get_provider
    mocker.patch('app.routes.get_provider', return_value=mock_provider)

    data = {
        'mode': 'async',
        'voice_id': 'voice-1',
        'text': 'Long text here'
    }

    response = client.post('/api/generate',
                           json=data)

    if response.status_code != 200:
        print(f"Async Gen Error: {response.get_json()}")

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['task_id'] == 'task-123'

def test_generate_validation_error(client):
    # Missing voice_id
    response = client.post('/api/generate',
                           json={'text': 'hi'})
    assert response.status_code == 400
