# MiniMax & Volcengine TTS Web Interface

A simple, user-friendly web interface for generating speech using MiniMax and Volcengine TTS APIs. Features include separate User and Admin portals, support for synchronous and asynchronous generation, and EPUB text extraction.

## Features

- **Multi-Provider Support**: Seamlessly switch between MiniMax and Volcengine TTS providers.
- **User Portal**:
  - Select voices from a configured list.
  - Generate audio from text or uploaded EPUB files.
  - Play and download generated audio.
- **Admin Portal**:
  - Secure configuration management.
  - Set API keys, App IDs, and Cluster details.
  - Manage available voices.
- **Async Processing**: Support for large text processing via asynchronous tasks.
- **Structured Logging**: JSON-formatted logs for easy monitoring and debugging.

## Prerequisites

- Python 3.10 or higher.
- API credentials for MiniMax and/or Volcengine.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The application uses a `config.json` file for settings. A default configuration is created on the first run if it doesn't exist.

### Admin Portal

You can configure the application via the web interface at `/admin`.
*   **Default Admin Password**: `admin` (Change this immediately in the Admin portal!).

### `config.json` Structure

```json
{
    "active_provider": "minimax",
    "minimax": {
        "api_key": "YOUR_MINIMAX_API_KEY",
        "group_id": "YOUR_MINIMAX_GROUP_ID"
    },
    "volcengine": {
        "app_id": "YOUR_VOLCENGINE_APP_ID",
        "access_token": "YOUR_VOLCENGINE_ACCESS_TOKEN",
        "secret_key": "YOUR_VOLCENGINE_SECRET_KEY",
        "cluster": "volcano_tts"
    },
    "voices": {
        "minimax": [
            {"name": "Audiobook Male 1", "id": "audiobook_male_1"}
        ],
        "volcengine": [
            {"name": "Standard Female", "id": "BV001_streaming"}
        ]
    },
    "admin_password": "admin"
}
```

## Usage

1.  **Start the server**:
    ```bash
    python run.py
    ```

2.  **Access the User Interface**:
    Open your browser and navigate to `http://127.0.0.1:5000`.

3.  **Access the Admin Interface**:
    Navigate to `http://127.0.0.1:5000/admin` to configure settings.

## Development

### Running Tests

To run the test suite:

```bash
pip install pytest pytest-mock
pytest
```

### Logging

The application uses structured JSON logging. Logs are output to the console (stdout) and include timestamps, log levels, and request details.
