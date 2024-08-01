from flask import Flask, request, send_file, render_template, jsonify
from flask_cors import CORS
import io
from gtts import gTTS

app = Flask(__name__)
CORS(app)

def text_to_speech_hindi(text):
    tts = gTTS(text=text, lang='hi', slow=False)
    audio_io = io.BytesIO()
    tts.write_to_fp(audio_io)
    audio_io.seek(0)
    return audio_io

@app.route('/')
def home():
    return render_template('Hindi Text-to-Speech Converter Interface.html')

@app.route('/convert', methods=['POST'])
def convert():
    data = request.json
    text = data['text']

    try:
        audio_io = text_to_speech_hindi(text)
        
        return send_file(
            audio_io,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='hindi_speech.mp3'
        )
    except Exception as e:
        app.logger.error(f"Error in conversion: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)