from unittest.mock import MagicMock, patch
from app.services.minimax import MinimaxClient
from flask import Flask

class TestMinimaxService:
    # Using pytest style

    def setup_method(self):
        self.app = Flask(__name__)
        self.app.config['MINIMAX_API_KEY'] = 'test-key'
        self.app.config['MINIMAX_API_URL'] = 'https://api.test'
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = MinimaxClient()

    def teardown_method(self):
        self.ctx.pop()

    @patch('requests.Session.post')
    def test_upload_file(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {'base_resp': {'status_code': 0}, 'file': {'file_id': 1}}
        mock_post.return_value = mock_resp

        import io
        f = io.BytesIO(b"content")

        self.client.upload_file("test.txt", f, "text/plain")

        args, kwargs = mock_post.call_args
        assert "files" in kwargs
        assert kwargs['data']['purpose'] == 't2a_async_input'
