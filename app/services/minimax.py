import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from flask import current_app
from app.extensions import cache
from typing import Dict, List, Optional, Union, Any

class MinimaxClient:
    def __init__(self):
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def _get_headers(self) -> Dict[str, str]:
        api_key = current_app.config['MINIMAX_API_KEY']
        if not api_key:
            raise ValueError("MiniMax API Key not configured")
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _get_url(self, endpoint: str) -> str:
        base_url = current_app.config['MINIMAX_API_URL']
        group_id = current_app.config.get('MINIMAX_GROUP_ID')
        url = f"{base_url}{endpoint}"
        if group_id:
            url += f"?GroupId={group_id}"
        return url

    @cache.cached(timeout=3600, key_prefix='voices_list')
    def get_voices(self) -> List[Dict[str, str]]:
        return [
            {"name": "Audiobook Male 1", "id": "audiobook_male_1"},
            {"name": "Audiobook Male 2", "id": "audiobook_male_2"},
            {"name": "Audiobook Female 1", "id": "audiobook_female_1"},
            {"name": "Audiobook Female 2", "id": "audiobook_female_2"},
            {"name": "Male 1", "id": "male-qn-qingse"},
            {"name": "Male 2", "id": "male-qn-jingying"},
            {"name": "Female 1", "id": "female-shaonv"},
            {"name": "Female 2", "id": "female-yujie"}
        ]

    def generate_sync(self, text: str, voice_id: str, speed: float = 1.0,
                      vol: float = 1.0, pitch: int = 0, format: str = 'mp3') -> Dict[str, Any]:
        url = self._get_url("/v1/t2a_v2")
        payload = {
            "model": "speech-2.6-hd",
            "text": text,
            "stream": False,
            "voice_setting": {
                "voice_id": voice_id,
                "speed": float(speed),
                "vol": float(vol),
                "pitch": int(pitch)
            },
            "audio_setting": {
                "sample_rate": 32000,
                "bitrate": 128000,
                "format": format,
                "channel": 1
            }
        }

        response = self.session.post(url, json=payload, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def upload_file(self, filename: str, file_stream: Any, mimetype: str) -> Dict[str, Any]:
        url = f"{current_app.config['MINIMAX_API_URL']}/v1/files/upload"
        headers = {"Authorization": f"Bearer {current_app.config['MINIMAX_API_KEY']}"}

        files = {
            'file': (filename, file_stream, mimetype)
        }
        data = {'purpose': 't2a_async_input'}

        response = self.session.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()
        return response.json()

    def generate_async(self, text: Optional[Union[str, List[str]]] = None,
                       text_file_id: Optional[Union[int, str]] = None,
                       voice_id: str = None, speed: float = 1.0,
                       vol: float = 1.0, pitch: int = 0, format: str = 'mp3') -> Dict[str, Any]:
        url = self._get_url("/v1/t2a_async_v2")

        payload = {
            "model": "speech-2.6-hd",
            "voice_setting": {
                "voice_id": voice_id,
                "speed": float(speed),
                "vol": float(vol),
                "pitch": int(pitch)
            },
            "audio_setting": {
                "audio_sample_rate": 32000,
                "bitrate": 128000,
                "format": format,
                "channel": 1
            }
        }

        if text_file_id:
            payload['text_file_id'] = int(text_file_id)
        elif text:
            if isinstance(text, list):
                payload['text'] = "\n".join(text)
            else:
                payload['text'] = text
        else:
             raise ValueError("Either text or text_file_id must be provided")

        response = self.session.post(url, json=payload, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def query_task(self, task_id: str) -> Dict[str, Any]:
        url = self._get_url("/v1/query/t2a_async_query_v2")
        params = {'task_id': task_id}
        response = self.session.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def retrieve_file(self, file_id: Union[str, int]) -> Dict[str, Any]:
        url = f"{current_app.config['MINIMAX_API_URL']}/v1/files/retrieve"
        params = {'file_id': file_id}
        headers = {"Authorization": f"Bearer {current_app.config['MINIMAX_API_KEY']}"}

        response = self.session.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

minimax_client = MinimaxClient()
