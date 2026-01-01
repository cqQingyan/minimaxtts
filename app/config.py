import json
import os
import shutil
from typing import Any, Dict, Optional, List

CONFIG_FILE = 'config.json'

DEFAULT_CONFIG: Dict[str, Any] = {
    "active_provider": "minimax",
    "minimax": {
        "api_key": "",
        "group_id": ""
    },
    "volcengine": {
        "app_id": "",
        "access_token": "",
        "secret_key": "",
        "cluster": "volcano_tts"
    },
    "voices": {
        "minimax": [
            {"name": "Audiobook Male 1", "id": "audiobook_male_1"},
            {"name": "Audiobook Male 2", "id": "audiobook_male_2"},
            {"name": "Audiobook Female 1", "id": "audiobook_female_1"},
            {"name": "Audiobook Female 2", "id": "audiobook_female_2"}
        ],
        "volcengine": [
            {"name": "Standard Female (BV001_streaming)", "id": "BV001_streaming"},
            {"name": "Standard Male (BV002_streaming)", "id": "BV002_streaming"}
        ]
    },
    "admin_password": "admin"
}

class ConfigManager:
    def __init__(self, filepath: str = CONFIG_FILE) -> None:
        self.filepath: str = filepath
        self._config: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        if not os.path.exists(self.filepath):
            self._config = DEFAULT_CONFIG
            self.save()
            return

        with open(self.filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Migration: Check if old format
        if "api_key" in data and "active_provider" not in data:
            self._migrate_v1_to_v2(data)
        else:
            self._config = data

    def _migrate_v1_to_v2(self, old_data: Dict[str, Any]) -> None:
        print("Migrating config from v1 to v2...")
        new_config = DEFAULT_CONFIG.copy()

        # Move MiniMax keys
        new_config['minimax']['api_key'] = old_data.get('api_key', '')
        new_config['minimax']['group_id'] = old_data.get('group_id', '')

        # Move admin password
        new_config['admin_password'] = old_data.get('admin_password', 'admin')

        # Move voices to MiniMax list (assuming old voices were MiniMax)
        if 'voices' in old_data:
            new_config['voices']['minimax'] = old_data['voices']

        self._config = new_config
        self.save()

    def save(self) -> None:
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=4, ensure_ascii=False)

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._config[key] = value
        self.save()

    def get_all(self) -> Dict[str, Any]:
        return self._config

    def update(self, new_data: Dict[str, Any]) -> None:
        self._config.update(new_data)
        self.save()

config_manager = ConfigManager()
