from flask import Flask, request, jsonify, Response, stream_with_context
import os
import speech_recognition as sr
from moviepy.editor import VideoFileClip
from werkzeug.utils import secure_filename
import time
import uuid
import math

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv'}
CHUNK_DURATION = 60  # Process 60 seconds at a time

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/convert', methods=['POST'])
def convert_video_to_text():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    video_file = request.files['video']
    
    if video_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(video_file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    unique_filename = f"{uuid.uuid4()}_{secure_filename(video_file.filename)}"
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

    def generate():
        video_clip = None
        try:
            # Save the uploaded video
            video_file.save(video_path)
            yield "data: {\"status\": \"Uploading\", \"progress\": 5}\n\n"

            # Load the video and get its duration
            video_clip = VideoFileClip(video_path)
            total_duration = video_clip.duration
            num_chunks = math.ceil(total_duration / CHUNK_DURATION)

            recognizer = sr.Recognizer()
            full_text = ""

            for i in range(num_chunks):
                start_time = i * CHUNK_DURATION
                end_time = min((i + 1) * CHUNK_DURATION, total_duration)
                
                # Extract audio chunk
                audio_chunk = video_clip.subclip(start_time, end_time).audio
                audio_chunk_path = os.path.join(app.config['UPLOAD_FOLDER'], f"chunk_{i}.wav")
                audio_chunk.write_audiofile(audio_chunk_path, verbose=False, logger=None)

                # Perform speech recognition on the chunk
                with sr.AudioFile(audio_chunk_path) as source:
                    audio = recognizer.record(source)
                chunk_text = recognizer.recognize_google(audio)
                full_text += chunk_text + " "

                # Clean up the audio chunk file
                os.remove(audio_chunk_path)

                # Calculate and yield progress
                progress = min(5 + (i + 1) * 95 / num_chunks, 99)  # Cap at 99% to leave room for final processing
                yield f"data: {{\"status\": \"Processing\", \"progress\": {progress:.0f}, \"text\": \"{full_text.strip()}\"}}\n\n"

            yield f"data: {{\"status\": \"Completed\", \"progress\": 100, \"text\": \"{full_text.strip()}\"}}\n\n"

        except Exception as e:
            yield f"data: {{\"status\": \"Error\", \"error\": \"{str(e)}\"}}\n\n"

        finally:
            if video_clip:
                video_clip.close()
            if os.path.exists(video_path):
                os.remove(video_path)

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)