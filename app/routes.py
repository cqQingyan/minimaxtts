from flask import Blueprint, render_template, request, jsonify, send_file, current_app, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app.services.minimax import minimax_client
from app.tasks import submit_async_generation
from app.utils.validators import validate_input
from app.utils.file_processor import process_epub_to_text
from app.models import History, db
from app.extensions import cache
import tempfile
import os
import io
import binascii

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    voices = minimax_client.get_voices()
    return render_template('index.html', voices=voices)

@bp.route('/history')
@login_required
def history():
    # Fetch history for current user, ordered by newest first
    items = History.query.filter_by(user_id=current_user.id).order_by(History.created_at.desc()).all()
    return render_template('history.html', items=items)

@bp.route('/api/generate', methods=['POST'])
@login_required
def generate():
    data = request.json
    voice_id = data.get('voice_id')
    mode = data.get('mode', 'sync')
    text = data.get('text')
    text_file_id = data.get('text_file_id')

    # Optional parameters
    speed = data.get('speed', 1.0)
    vol = data.get('vol', 1.0)
    pitch = data.get('pitch', 0)
    audio_format = data.get('format', 'mp3')

    # Validation
    if not voice_id:
        return jsonify({'error': 'Missing voice_id'}), 400

    errors = validate_input(text=text)
    if errors:
        return jsonify({'error': errors[0]}), 400

    # Get Voice Name for history
    voices = minimax_client.get_voices()
    voice_name = next((v['name'] for v in voices if v['id'] == voice_id), voice_id)

    if mode == 'sync':
        if not text:
            return jsonify({'error': 'Missing text for sync mode'}), 400

        try:
            resp_json = minimax_client.generate_sync(
                text=text, voice_id=voice_id,
                speed=speed, vol=vol, pitch=pitch, format=audio_format
            )

            if resp_json.get('base_resp', {}).get('status_code') != 0:
                 return jsonify({'error': resp_json.get('base_resp', {}).get('status_msg', 'Unknown API Error')}), 400

            hex_audio = resp_json.get('data', {}).get('audio')
            if not hex_audio:
                return jsonify({'error': 'No audio data received'}), 500

            audio_binary = binascii.unhexlify(hex_audio)

            # Save sync generation to history as well (optional, but good for tracking)
            # For now, we won't save the file to disk to keep it simple as sync is usually small,
            # but we could log the event.

            return send_file(
                io.BytesIO(audio_binary),
                mimetype=f'audio/{audio_format}',
                as_attachment=True,
                download_name=f'generated_audio.{audio_format}'
            )
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    else: # Async
        try:
            task_id = submit_async_generation(
                text=text, text_file_id=text_file_id,
                voice_id=voice_id, voice_name=voice_name, user_id=current_user.id,
                speed=speed, vol=vol, pitch=pitch, format=audio_format
            )
            return jsonify({'task_id': task_id, 'status': 'processing'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@bp.route('/api/upload', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Validation
    errors = validate_input(file=file)
    if errors:
        return jsonify({'error': errors[0]}), 400

    filename = secure_filename(file.filename)

    # Handle EPUB vs TXT
    if filename.lower().endswith('.epub'):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.epub') as temp:
                file.save(temp.name)
                temp_path = temp.name

            try:
                text_content = process_epub_to_text(temp_path)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

            if not text_content:
                return jsonify({'error': 'Empty or unreadable EPUB'}), 400

            # Convert to stream for upload
            file_stream = io.BytesIO(text_content.encode('utf-8'))
            upload_filename = filename.replace('.epub', '.txt')
            mimetype = 'text/plain'

        except Exception as e:
            return jsonify({'error': f"EPUB Error: {str(e)}"}), 500
    else:
        file_stream = file.stream
        upload_filename = filename
        mimetype = file.mimetype

    # Upload to MiniMax
    try:
        resp = minimax_client.upload_file(upload_filename, file_stream, mimetype)

        # Check API response status
        if resp.get('base_resp', {}).get('status_code') != 0:
             return jsonify({'error': resp.get('base_resp', {}).get('status_msg', 'Upload failed')}), 400

        return jsonify(resp)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/task_status', methods=['GET'])
@login_required
def check_status():
    task_id = request.args.get('task_id')
    if not task_id:
        return jsonify({'error': 'Missing task_id'}), 400

    # Check DB first
    history = History.query.filter_by(task_id=task_id).first()
    if history:
        return jsonify({
            'status': history.status,
            'download_url': history.file_path,
            'voice_name': history.voice_name
        })

    return jsonify({'status': 'unknown'}), 404
