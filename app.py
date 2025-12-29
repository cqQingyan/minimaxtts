from flask import Flask, render_template, request, jsonify, send_file
import requests
import io
import binascii

app = Flask(__name__)

# MiniMax API Constants
API_BASE_URL = "https://api.minimaxi.com"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/check_connection', methods=['POST'])
def check_connection():
    data = request.json
    api_key = data.get('api_key')
    group_id = data.get('group_id')
    
    if not api_key:
        return jsonify({'error': 'Missing API Key'}), 400

    url = f"{API_BASE_URL}/v1/t2a_v2"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Minimal payload for connectivity check
    payload = {
        "model": "speech-2.6-hd",
        "text": "test",
        "stream": False,
        "voice_setting": {
            "voice_id": "audiobook_male_1",
            "speed": 1, "vol": 1, "pitch": 0
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            resp_json = response.json()
            if resp_json.get('base_resp', {}).get('status_code') == 0:
                return jsonify({'status': 'success', 'message': 'Connection successful'})
            else:
                 return jsonify({'status': 'failed', 'message': resp_json.get('base_resp', {}).get('status_msg', 'Unknown API Error')}), 400
        else:
             return jsonify({'status': 'failed', 'message': f"HTTP Error: {response.status_code} - {response.text}"}), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({'status': 'failed', 'message': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    api_key = request.form.get('api_key')
    if not api_key:
        return jsonify({'error': 'Missing API Key'}), 400
        
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    url = f"{API_BASE_URL}/v1/files/upload"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    # MiniMax requires multipart/form-data
    # 'file' is the file object, 'purpose' is a form field
    files = {
        'file': (file.filename, file.stream, file.mimetype)
    }
    data = {
        'purpose': 't2a_async_input'
    }
    
    try:
        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e), 'details': response.text if response else ''}), 500

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    api_key = data.get('api_key')
    group_id = data.get('group_id')
    voice_id = data.get('voice_id')
    mode = data.get('mode', 'sync') # 'sync' or 'async'
    
    # Validation
    if not api_key or not voice_id:
         return jsonify({'error': 'Missing required fields'}), 400
         
    # Common headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    if mode == 'sync':
        text = data.get('text')
        if not text:
             return jsonify({'error': 'Missing text for sync mode'}), 400
             
        url = f"{API_BASE_URL}/v1/t2a_v2"
        payload = {
            "model": "speech-2.6-hd",
            "text": text,
            "stream": False,
            "voice_setting": {
                "voice_id": voice_id,
                "speed": 1, "vol": 1, "pitch": 0
            },
            "audio_setting": {
                "sample_rate": 32000, "bitrate": 128000, "format": "mp3", "channel": 1
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            resp_json = response.json()
            
            if resp_json.get('base_resp', {}).get('status_code') != 0:
                 return jsonify({'error': resp_json.get('base_resp', {}).get('status_msg', 'Unknown API Error')}), 400
            
            hex_audio = resp_json.get('data', {}).get('audio')
            if not hex_audio:
                return jsonify({'error': 'No audio data received'}), 500
                
            try:
                audio_binary = binascii.unhexlify(hex_audio)
            except binascii.Error:
                 return jsonify({'error': 'Failed to decode audio data'}), 500

            return send_file(
                io.BytesIO(audio_binary),
                mimetype='audio/mpeg',
                as_attachment=True,
                download_name='generated_audio.mp3'
            )
        except requests.exceptions.RequestException as e:
            return jsonify({'error': str(e), 'details': response.text if response else ''}), 500

    else: # mode == 'async'
        text = data.get('text')
        text_file_id = data.get('text_file_id')
        
        if not text and not text_file_id:
            return jsonify({'error': 'Missing text or text_file_id for async mode'}), 400

        url = f"{API_BASE_URL}/v1/t2a_async_v2"
        payload = {
            "model": "speech-2.6-hd",
            "voice_setting": {
                "voice_id": voice_id,
                "speed": 1, "vol": 1, "pitch": 1
            },
            "audio_setting": {
                "audio_sample_rate": 32000, "bitrate": 128000, "format": "mp3", "channel": 1
            }
        }
        
        if text_file_id:
            payload['text_file_id'] = int(text_file_id)
        else:
            payload['text'] = text
            
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return jsonify(response.json())
        except requests.exceptions.RequestException as e:
            return jsonify({'error': str(e), 'details': response.text if response else ''}), 500

@app.route('/api/query', methods=['GET'])
def query():
    task_id = request.args.get('task_id')
    api_key = request.args.get('api_key')
    
    if not task_id or not api_key:
        return jsonify({'error': 'Missing required parameters'}), 400
        
    url = f"{API_BASE_URL}/v1/query/t2a_async_query_v2"
    params = {'task_id': task_id}
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e), 'details': response.text if response else ''}), 500

@app.route('/api/retrieve', methods=['GET'])
def retrieve():
    file_id = request.args.get('file_id')
    api_key = request.args.get('api_key')
    
    if not file_id or not api_key:
        return jsonify({'error': 'Missing required parameters'}), 400
        
    url = f"{API_BASE_URL}/v1/files/retrieve"
    params = {'file_id': file_id}
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e), 'details': response.text if response else ''}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
