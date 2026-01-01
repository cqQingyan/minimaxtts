import requests
import binascii
from .base import TTSProvider

class MinimaxProvider(TTSProvider):
    API_BASE_URL = "https://api.minimaxi.com"

    def __init__(self, api_key, group_id=None, voices=None):
        self.api_key = api_key
        self.group_id = group_id
        self.voices = voices or []

    def get_voices(self):
        return self.voices

    def generate_sync(self, text, voice_id, **kwargs):
        if not self.api_key:
             raise ValueError("Missing API Key for MiniMax")

        url = f"{self.API_BASE_URL}/v1/t2a_v2"
        if self.group_id:
             url += f"?GroupId={self.group_id}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Normalize params
        speed = float(kwargs.get('speed', 1))
        vol = float(kwargs.get('vol', 1))
        pitch = int(kwargs.get('pitch', 0))

        payload = {
            "model": "speech-2.6-hd",
            "text": text,
            "stream": False,
            "voice_setting": {
                "voice_id": voice_id,
                "speed": speed, "vol": vol, "pitch": pitch
            },
            "audio_setting": {
                "sample_rate": 32000, "bitrate": 128000, "format": "mp3", "channel": 1
            }
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        resp_json = response.json()

        if resp_json.get('base_resp', {}).get('status_code') != 0:
             raise Exception(f"MiniMax API Error: {resp_json.get('base_resp', {}).get('status_msg')}")

        hex_audio = resp_json.get('data', {}).get('audio')
        if not hex_audio:
            raise Exception("No audio data received")

        return binascii.unhexlify(hex_audio)

    def upload_file(self, filename, file_stream, mimetype):
        url = f"{self.API_BASE_URL}/v1/files/upload"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        files = {
            'file': (filename, file_stream, mimetype)
        }
        data = {
            'purpose': 't2a_async_input'
        }

        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()
        return response.json()

    def submit_async(self, text, text_file_id, voice_id, **kwargs):
        url = f"{self.API_BASE_URL}/v1/t2a_async_v2"
        if self.group_id:
             url += f"?GroupId={self.group_id}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Normalize params
        speed = float(kwargs.get('speed', 1))
        vol = float(kwargs.get('vol', 1))
        pitch = int(kwargs.get('pitch', 0))

        payload = {
            "model": "speech-2.6-hd",
            "voice_setting": {
                "voice_id": voice_id,
                "speed": speed, "vol": vol, "pitch": pitch
            },
            "audio_setting": {
                "audio_sample_rate": 32000, "bitrate": 128000, "format": "mp3", "channel": 1
            }
        }

        if text_file_id:
            payload['text_file_id'] = int(text_file_id)
        else:
            payload['text'] = text

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json() # Returns {'task_id': ..., ...}

    def query_async(self, task_id):
        url = f"{self.API_BASE_URL}/v1/query/t2a_async_query_v2"
        if self.group_id:
             url += f"?GroupId={self.group_id}"

        params = {'task_id': task_id}
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    def retrieve_file(self, file_id):
        url = f"{self.API_BASE_URL}/v1/files/retrieve"
        params = {'file_id': file_id}
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
