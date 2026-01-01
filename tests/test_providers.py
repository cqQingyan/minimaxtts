import unittest
from unittest.mock import MagicMock, patch
from app.services.minimax import MinimaxProvider
from app.services.volcengine_tts import VolcengineProvider
import io

class TestTTSProviders(unittest.TestCase):

    def test_minimax_provider_init(self):
        provider = MinimaxProvider(api_key="test_key", group_id="123")
        self.assertEqual(provider.api_key, "test_key")
        self.assertEqual(provider.group_id, "123")

    @patch('requests.post')
    def test_minimax_generate_sync(self, mock_post):
        provider = MinimaxProvider(api_key="test_key")

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'base_resp': {'status_code': 0},
            'data': {'audio': '001122'} # Hex audio
        }
        mock_post.return_value = mock_response

        audio = provider.generate_sync("hello", "voice_1")
        self.assertEqual(audio, b'\x00\x11\x22')

        # Verify call args
        args, kwargs = mock_post.call_args
        self.assertIn("voice_id", kwargs['json']['voice_setting'])

    def test_volcengine_provider_init(self):
        provider = VolcengineProvider(app_id="app1", access_token="tok1", secret_key="sec1")
        self.assertEqual(provider.app_id, "app1")
        self.assertEqual(provider.access_key, "tok1")
        self.assertEqual(provider.secret_key, "sec1")

    @patch('requests.request') # Since Volc uses request() inside _sign_and_send
    def test_volcengine_generate_sync_saas(self, mock_req):
        # Test without Secret Key (SaaS mode)
        provider = VolcengineProvider(app_id="app1", access_token="tok1")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'code': 3000,
            'data': 'AQID' # Base64 for 010203
        }
        mock_req.return_value = mock_response

        audio = provider.generate_sync("hello", "voice_1")
        self.assertEqual(audio, b'\x01\x02\x03')

        args, kwargs = mock_req.call_args
        self.assertIn("Authorization", kwargs['headers'])
        self.assertTrue(kwargs['headers']['Authorization'].startswith("Bearer"))

    @patch('requests.request')
    def test_volcengine_generate_sync_signed(self, mock_req):
        # Test with Secret Key (Signed mode)
        provider = VolcengineProvider(app_id="app1", access_token="tok1", secret_key="sec1")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'code': 3000,
            'data': 'AQID'
        }
        mock_req.return_value = mock_response

        audio = provider.generate_sync("hello", "voice_1")
        self.assertEqual(audio, b'\x01\x02\x03')

        args, kwargs = mock_req.call_args
        # Should have Authorization header but NOT simple Bearer
        self.assertIn("Authorization", kwargs['headers'])
        self.assertIn("HMAC-SHA256", kwargs['headers']['Authorization'])

if __name__ == '__main__':
    unittest.main()
