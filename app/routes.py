from flask import Blueprint, render_template, request, jsonify, send_file
import io
import tempfile
import os
import binascii
from app.config import config_manager
from app.services.minimax import MinimaxProvider
from app.services.volcengine_tts import VolcengineProvider
from app.utils import extract_text_from_epub

main = Blueprint('main', __name__)

def get_provider():
    config = config_manager.get_all()
    provider_name = config.get('active_provider', 'minimax')

    if provider_name == 'minimax':
        return MinimaxProvider(
            api_key=config['minimax'].get('api_key'),
            group_id=config['minimax'].get('group_id'),
            voices=config['voices'].get('minimax', [])
        )
    elif provider_name == 'volcengine':
        return VolcengineProvider(
            app_id=config['volcengine'].get('app_id'),
            access_token=config['volcengine'].get('access_token'),
            secret_key=config['volcengine'].get('secret_key'),
            cluster=config['volcengine'].get('cluster'),
            voices=config['voices'].get('volcengine', [])
        )
    else:
        raise ValueError(f"Unknown provider: {provider_name}")

@main.route('/')
def index():
    provider = get_provider()
    voices = provider.get_voices()
    return render_template('index.html', voices=voices)

@main.route('/admin')
def admin_page():
    return render_template('admin.html')

@main.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    password = data.get('password')
    if password == config_manager.get('admin_password', 'admin'):
        return jsonify({'status': 'success'})
    return jsonify({'status': 'failed', 'message': 'Invalid password'}), 401

@main.route('/api/admin/config', methods=['GET', 'POST'])
def admin_config():
    if request.method == 'GET':
        return jsonify(config_manager.get_all())

    if request.method == 'POST':
        new_config = request.json
        config_manager.update(new_config)
        return jsonify({'status': 'success'})

@main.route('/api/check_connection', methods=['POST'])
def check_connection():
    # Helper to check connection for current or tested config
    data = request.json or {}
    # If data provided, temporarily instantiate provider
    # Otherwise use current config

    # We need to determine which provider we are checking.
    # The frontend should ideally send "provider" and "config"
    # But existing frontend sends api_key/group_id for MiniMax.

    provider_type = data.get('provider')

    try:
        if provider_type:
            # Test specific credentials
            if provider_type == 'minimax':
                provider = MinimaxProvider(
                    api_key=data.get('api_key'),
                    group_id=data.get('group_id'),
                    voices=[]
                )
                voice_id = "audiobook_male_1" # Default test
            elif provider_type == 'volcengine':
                provider = VolcengineProvider(
                    app_id=data.get('app_id'),
                    access_token=data.get('access_token'),
                    secret_key=data.get('secret_key'),
                    cluster=data.get('cluster'),
                    voices=[]
                )
                voice_id = "BV001_streaming" # Default test
            else:
                 return jsonify({'status': 'failed', 'message': 'Unknown provider'}), 400
        else:
            # Use current configured provider
            provider = get_provider()
            voices = provider.get_voices()
            voice_id = voices[0]['id'] if voices else "unknown"

        # Try to generate a short text
        try:
             # Just generate "test"
             provider.generate_sync("test", voice_id)
             return jsonify({'status': 'success', 'message': 'Connection successful'})
        except Exception as e:
             return jsonify({'status': 'failed', 'message': str(e)}), 400

    except Exception as e:
        return jsonify({'status': 'failed', 'message': f"Setup Error: {str(e)}"}), 500


@main.route('/api/upload', methods=['POST'])
def upload_file():
    provider = get_provider()

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = file.filename.lower()
    file_stream = file.stream
    mimetype = file.mimetype

    if filename.endswith('.epub'):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.epub') as temp_file:
                file.save(temp_file.name)
                temp_path = temp_file.name

            try:
                text_content = extract_text_from_epub(temp_path)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

            if not text_content:
                return jsonify({'error': 'Failed to extract text from EPUB'}), 400

            file_stream = io.BytesIO(text_content.encode('utf-8'))
            filename = filename.replace('.epub', '.txt')
            mimetype = 'text/plain'

        except Exception as e:
            return jsonify({'error': f'EPUB processing failed: {str(e)}'}), 500

    try:
        # Provider specific upload
        result = provider.upload_file(filename, file_stream, mimetype)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    provider = get_provider()

    voice_id = data.get('voice_id')
    mode = data.get('mode', 'sync')

    if not voice_id:
         return jsonify({'error': 'Missing voice_id'}), 400

    if mode == 'sync':
        text = data.get('text')
        if not text:
             return jsonify({'error': 'Missing text'}), 400
        try:
            audio_data = provider.generate_sync(text, voice_id, **data)
            return send_file(
                io.BytesIO(audio_data),
                mimetype='audio/mpeg',
                as_attachment=True,
                download_name='generated_audio.mp3'
            )
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        text = data.get('text')
        text_file_id = data.get('text_file_id')
        if not text and not text_file_id:
            return jsonify({'error': 'Missing text or file_id'}), 400

        try:
            result = provider.submit_async(text, text_file_id, voice_id, **data)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@main.route('/api/query', methods=['GET'])
def query():
    task_id = request.args.get('task_id')
    if not task_id:
        return jsonify({'error': 'Missing task_id'}), 400

    provider = get_provider()
    try:
        result = provider.query_async(task_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/api/retrieve', methods=['GET'])
def retrieve():
    file_id = request.args.get('file_id')
    if not file_id:
        return jsonify({'error': 'Missing file_id'}), 400

    provider = get_provider()
    try:
        result = provider.retrieve_file(file_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
