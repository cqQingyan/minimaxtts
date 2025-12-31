import json
from unittest.mock import patch

def test_index_route(client):
    # Authenticate
    client.post('/login', data={'username': 'admin', 'password': 'admin'})

    response = client.get('/')
    assert response.status_code == 200
    assert b'MiniMax TTS' in response.data

def test_history_route(client):
    # Authenticate
    client.post('/login', data={'username': 'admin', 'password': 'admin'})

    response = client.get('/history')
    assert response.status_code == 200
    assert b'Generation History' in response.data

@patch('app.services.minimax.minimax_client.generate_sync')
def test_generate_sync_api(mock_sync, client):
    # Authenticate
    client.post('/login', data={'username': 'admin', 'password': 'admin'})

    # Mock return
    mock_sync.return_value = {
        'base_resp': {'status_code': 0},
        'data': {'audio': 'aabbcc'} # Hex string
    }

    data = {
        'mode': 'sync',
        'voice_id': 'voice-1',
        'text': 'Hello world'
    }

    response = client.post('/api/generate',
                           data=json.dumps(data),
                           content_type='application/json')

    assert response.status_code == 200
    assert response.mimetype == 'audio/mp3'

@patch('app.services.minimax.minimax_client.generate_async')
def test_generate_async_api(mock_async, client):
    # Authenticate
    client.post('/login', data={'username': 'admin', 'password': 'admin'})

    # Mock return
    mock_async.return_value = {'task_id': 'task-123'}

    data = {
        'mode': 'async',
        'voice_id': 'voice-1',
        'text': 'Long text here'
    }

    response = client.post('/api/generate',
                           data=json.dumps(data),
                           content_type='application/json')

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['task_id'] == 'task-123'
    assert json_data['status'] == 'processing'

def test_generate_validation_error(client):
    client.post('/login', data={'username': 'admin', 'password': 'admin'})

    # Missing voice_id
    response = client.post('/api/generate',
                           data=json.dumps({'text': 'hi'}),
                           content_type='application/json')
    assert response.status_code == 400
