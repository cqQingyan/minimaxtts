from abc import ABC, abstractmethod
import io
from typing import List, Dict, Any, Union, Optional

class TTSProvider(ABC):
    @abstractmethod
    def get_voices(self) -> List[Dict[str, str]]:
        """Return a list of dicts with 'name' and 'id'."""
        pass

    @abstractmethod
    def generate_sync(self, text: str, voice_id: str, **kwargs: Any) -> bytes:
        """
        Generate audio synchronously.
        Should return a dictionary with audio data or raise exception.
        Commonly returns {'data': {'audio': hex_string}} or similar,
        but we should normalize this return value.
        For now, let's stick to returning the raw provider response
        and handling normalization in the caller or here.
        Actually, let's normalize to bytes if possible, but the current app expects hex from MiniMax.
        To support multi-provider, we should probably return audio bytes directly.
        """
        pass

    @abstractmethod
    def upload_file(self, filename: str, file_stream: Any, mimetype: str) -> Dict[str, Any]:
        """Upload a file for async processing."""
        pass

    @abstractmethod
    def submit_async(self, text: Optional[str], text_file_id: Optional[str], voice_id: str, **kwargs: Any) -> Dict[str, Any]:
        """Submit an async task."""
        pass

    @abstractmethod
    def query_async(self, task_id: str) -> Dict[str, Any]:
        """Query status of async task."""
        pass

    @abstractmethod
    def retrieve_file(self, file_id: str) -> Dict[str, Any]:
        """Retrieve result file content."""
        pass
