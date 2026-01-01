from abc import ABC, abstractmethod
import io

class TTSProvider(ABC):
    @abstractmethod
    def get_voices(self):
        """Return a list of dicts with 'name' and 'id'."""
        pass

    @abstractmethod
    def generate_sync(self, text, voice_id, **kwargs):
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
    def upload_file(self, filename, file_stream, mimetype):
        """Upload a file for async processing."""
        pass

    @abstractmethod
    def submit_async(self, text, text_file_id, voice_id, **kwargs):
        """Submit an async task."""
        pass

    @abstractmethod
    def query_async(self, task_id):
        """Query status of async task."""
        pass

    @abstractmethod
    def retrieve_file(self, file_id):
        """Retrieve result file content."""
        pass
