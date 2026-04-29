from flask import Flask, request, jsonify, send_file
import subprocess
import os
import uuid
import requests

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/merge', methods=['POST'])
def merge_video_audio():
    data = request.json
    video_url = data.get('video_url')
    audio_url = data.get('audio_url')
    
    if not video_url or not audio_url:
        return jsonify({"error": "video_url and audio_url required"}), 400

    job_id = str(uuid.uuid4())
    video_path = f"/tmp/{job_id}_video.mp4"
    audio_path = f"/tmp/{job_id}_audio.mp3"
    output_path = f"/tmp/{job_id}_output.mp4"

    with open(video_path, 'wb') as f:
        f.write(requests.get(video_url).content)
    with open(audio_path, 'wb') as f:
        f.write(requests.get(audio_url).content)

    cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-i', audio_path,
        '-vf', 'crop=ih*9/16:ih,scale=1080:1920',
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-shortest',
        '-movflags', '+faststart',
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        return jsonify({"error": result.stderr}), 500

    return send_file(output_path, mimetype='video/mp4', as_attachment=True, download_name='short.mp4')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
