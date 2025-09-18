from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import tempfile
import io

app = Flask(__name__)
CORS(app)

@app.route('/status', methods=['GET'])
def status():
    print(f"Status check from {request.remote_addr}")
    return jsonify({'status': 'online'})

@app.route('/download', methods=['POST'])
def download():
    print(f"Download request from {request.remote_addr}")
    data = request.get_json()
    url = data.get('url') if data else None
    print(f"Requested URL: {url}")
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts = {
                'outtmpl': f'{temp_dir}/%(id)s.%(ext)s',
                'format': 'best/worst',
                'quiet': True,
                'no_warnings': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Accept-Encoding': 'gzip,deflate',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                    'Connection': 'keep-alive'
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_id = info.get('id', 'unknown')
                title = info.get('title', 'Unknown Title')
                ext = info.get('ext', 'mp4')
                filename = f"{video_id}.{ext}"
                filepath = os.path.join(temp_dir, filename)
                
                if os.path.exists(filepath):
                    with open(filepath, 'rb') as f:
                        video_data = f.read()
                    
                    return jsonify({
                        'success': True,
                        'title': title,
                        'video_id': video_id,
                        'filename': filename,
                        'video_data': video_data.hex()
                    })
                else:
                    return jsonify({'error': 'Video file not found'}), 500
        
    except Exception as e:
        print(f"Download error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5055)
