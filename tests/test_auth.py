from flask_login import current_user

def test_login_page_loads(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_login_success(client, app):
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'admin'
    }, follow_redirects=True)

    assert response.status_code == 200
    # Check if we are redirected to index and logged in
    with client.session_transaction() as sess:
        assert '_user_id' in sess
    assert b'MiniMax TTS' in response.data

def test_login_failure(client):
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'wrongpassword'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

def test_logout(client):
    # Login first
    client.post('/login', data={'username': 'admin', 'password': 'admin'})

    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data

    # Verify session cleared
    with client.session_transaction() as sess:
        assert '_user_id' not in sess

def test_unauthorized_access(client):
    response = client.get('/')
    # Should redirect to login
    assert response.status_code == 302
    assert 'login' in response.location
