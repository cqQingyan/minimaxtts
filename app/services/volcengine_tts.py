import requests
import json
import base64
import uuid
import time
from .base import TTSProvider
from .volcengine_lib import SignerV4, Credentials, Request

class VolcengineProvider(TTSProvider):
    # Standard Speech API endpoint (Sync)
    SYNC_API_URL = "https://openspeech.bytedance.com/api/v1/tts"
    # Async API endpoint (Offline Speech Synthesis)
    HOST = "openspeech.bytedance.com"
    SYNC_PATH = "/api/v1/tts"
    ASYNC_SUBMIT_PATH = "/api/v1/tts_async"
    ASYNC_QUERY_PATH = "/api/v1/tts_async"

    def __init__(self, app_id, access_token, secret_key=None, cluster="volcano_tts", voices=None):
        self.app_id = app_id
        # In Volcengine terminology:
        # Access Token usually = AccessKey (AK)
        # Secret Key = SecretKey (SK)
        self.access_key = access_token
        self.secret_key = secret_key
        self.cluster = cluster
        self.voices = voices or []
        self.service = "speech"
        self.region = "cn-north-1"

    def get_voices(self):
        return self.voices

    def _sign_and_send(self, method, path, payload):
        if not self.secret_key:
             headers = {
                "Authorization": f"Bearer; {self.access_key}",
                "Content-Type": "application/json"
            }
             url = f"https://{self.HOST}{path}"
             response = requests.request(method, url, json=payload, headers=headers)
             return response

        # Signing logic
        creds = Credentials(self.access_key, self.secret_key, self.service, self.region)
        req = Request()
        req.set_method(method)
        req.set_host(self.HOST)
        req.set_path(path)
        req.set_headers({'Content-Type': 'application/json'})
        req.set_body(json.dumps(payload))

        SignerV4.sign(req, creds)

        url = f"https://{self.HOST}{path}"
        response = requests.request(method, url, data=req.body, headers=req.headers)
        return response

    def generate_sync(self, text, voice_id, **kwargs):
        req_id = str(uuid.uuid4())

        speed = int(float(kwargs.get('speed', 1.0)) * 10)
        vol = int(float(kwargs.get('vol', 1.0)) * 10)
        pitch = int(float(kwargs.get('pitch', 0)) * 10)
        if float(kwargs.get('pitch', 0)) == 0:
            pitch = 10

        payload = {
            "app": {
                "appid": self.app_id,
                "token": "access_token",
                "cluster": self.cluster
            },
            "user": {
                "uid": "user_default"
            },
            "audio": {
                "voice_type": voice_id,
                "encoding": "mp3",
                "speed": speed,
                "volume": vol,
                "pitch": pitch
            },
            "request": {
                "reqid": req_id,
                "text": text,
                "operation": "query",
                "with_frontend": 1,
                "frontend_type": "unitTson"
            }
        }

        response = self._sign_and_send("POST", self.SYNC_PATH, payload)
        response.raise_for_status()
        resp_json = response.json()

        if resp_json.get("code") != 3000:
             raise Exception(f"Volcengine Error: {resp_json}")

        if "data" not in resp_json:
             raise Exception(f"Volcengine Error (No Data): {resp_json}")

        audio_b64 = resp_json["data"]
        return base64.b64decode(audio_b64)

    def upload_file(self, filename, file_stream, mimetype):
        # Return content as virtual file ID
        content = file_stream.read().decode('utf-8')
        return {"file_id": "RAW_TEXT:" + base64.b64encode(content.encode('utf-8')).decode('utf-8')}

    def submit_async(self, text, text_file_id, voice_id, **kwargs):
        if text_file_id and text_file_id.startswith("RAW_TEXT:"):
            text = base64.b64decode(text_file_id.split(":", 1)[1]).decode('utf-8')

        if not text:
             raise ValueError("Text required for Volcengine Async")

        speed = int(float(kwargs.get('speed', 1.0)) * 10)
        vol = int(float(kwargs.get('vol', 1.0)) * 10)
        pitch = 10
        if float(kwargs.get('pitch', 0)) != 0:
             pitch = int(float(kwargs.get('pitch', 0)) * 10)

        payload = {
            "app": {"appid": self.app_id, "token": "access_token", "cluster": self.cluster},
            "user": {"uid": "user_default"},
            "audio": {
                "voice_type": voice_id,
                "encoding": "mp3",
                "speed": speed,
                "volume": vol,
                "pitch": pitch
            },
            "request": {
                "reqid": str(uuid.uuid4()),
                "text": text,
                "operation": "submit",
            }
        }

        response = self._sign_and_send("POST", self.ASYNC_SUBMIT_PATH, payload)
        response.raise_for_status()
        resp_json = response.json()

        if resp_json.get("code") != 3000:
             raise Exception(f"Volcengine Async Submit Error: {resp_json}")

        task_id = resp_json.get("data", {}).get("task_id")
        return {"task_id": task_id, "base_resp": {"status_code": 0}} # Normalize return if needed

    def query_async(self, task_id):
        payload = {
             "app": {"appid": self.app_id, "token": "access_token", "cluster": self.cluster},
             "request": {
                 "operation": "query",
                 "task_id": task_id
             }
        }

        response = self._sign_and_send("POST", self.ASYNC_QUERY_PATH, payload)
        response.raise_for_status()
        volc_json = response.json()

        # Normalize to MiniMax structure for frontend compatibility
        # MiniMax: { "base_resp": {"status_code": 0}, "data": { "status": "Success/Processing", "file_id": ..., "download_url": ... } }
        # Volcengine: { "code": 3000, "message": "Success", "data": { "audio_url": "...", "task_status": "Success", ... } }

        # Default mapping
        result = {
            "base_resp": {
                "status_code": 0 if volc_json.get("code") == 3000 else -1,
                "status_msg": volc_json.get("message", "Unknown")
            },
            "data": {}
        }

        volc_data = volc_json.get("data", {})
        volc_status = volc_data.get("task_status", "unknown") # 0: created, 1: processing, 2: success, 3: failed?
        # Actually Volcengine uses strings often or codes?
        # Assuming we just pass it, but better to normalize "Success" string.

        # Map known statuses if possible, or pass through
        result["data"]["status"] = volc_status

        if "audio_url" in volc_data:
            result["data"]["download_url"] = volc_data["audio_url"]
            result["data"]["file_id"] = volc_data.get("reqid") # dummy file_id

        return result

    def retrieve_file(self, file_id):
        if file_id.startswith("http"):
            return {"file": {"download_url": file_id}}
        raise NotImplementedError("Volcengine retrieve by ID not supported")
