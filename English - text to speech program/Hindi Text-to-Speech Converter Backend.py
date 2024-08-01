from flask import Flask, request, send_file, render_template, jsonify
from flask_cors import CORS
import io
import os
import tempfile
from gtts import gTTS
import pyttsx3

app = Flask(__name__)
CORS(app)

def text_to_speech_gtts(text, lang='hi'):
    tts = gTTS(text=text, lang=lang, slow=False)
    audio_io = io.BytesIO()
    tts.write_to_fp(audio_io)
    audio_io.seek(0)
    return audio_io

def text_to_speech_pyttsx3(text, gender, mood):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    
    if gender == 'female' and len(voices) > 1:
        engine.setProperty('voice', voices[1].id)
    else:
        engine.setProperty('voice', voices[0].id)
    
    if mood in ['happy', 'joyful']:
        engine.setProperty('rate', 150)
        engine.setProperty('pitch', 110)
    elif mood in ['sad', 'crying', 'unhappy', 'weeping']:
        engine.setProperty('rate', 120)
        engine.setProperty('pitch', 90)
    else:  # neutral
        engine.setProperty('rate', 130)
        engine.setProperty('pitch', 100)
    
    audio_io = io.BytesIO()
    engine.save_to_file(text, 'temp.wav')
    engine.runAndWait()
    with open('temp.wav', 'rb') as f:
        audio_io.write(f.read())
    os.remove('temp.wav')
    audio_io.seek(0)
    return audio_io

@app.route('/')
def home():
    return render_template('Hindi Text-to-Speech Converter Interface.html')

@app.route('/convert', methods=['POST'])
def convert():
    data = request.json
    text = data['text']
    gender = data['gender']
    mood = data['mood']

    try:
        # Uncomment the method you want to use
        # audio_io = text_to_speech_gtts(text)
        audio_io = text_to_speech_pyttsx3(text, gender, mood)
        
        return send_file(
            audio_io,
            mimetype='audio/wav',
            as_attachment=True,
            download_name='speech.wav'
        )
    except Exception as e:
        app.logger.error(f"Error in conversion: {str(e)}")
        return jsonify({"error": "An error occurred during conversion"}), 500

if __name__ == '__main__':
    app.run(debug=True)