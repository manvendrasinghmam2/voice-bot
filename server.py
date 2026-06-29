from flask import Flask, request, jsonify, send_file
from google import genai
import edge_tts
import asyncio
import requests
import uuid
import os

app = Flask(__name__)

# =============================
# CONFIG
# =============================
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
DEEPGRAM_API_KEY = os.environ["DEEPGRAM_API_KEY"]

client = genai.Client(api_key=GEMINI_API_KEY)

AUDIO_FOLDER = "audio"

if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)


# =============================
# SPEECH TO TEXT
# =============================
def speech_to_text(filename):

    url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true"

    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "audio/wav"
    }

    with open(filename, "rb") as f:
        r = requests.post(url, headers=headers, data=f)

    data = r.json()

    try:
        return data["results"]["channels"][0]["alternatives"][0]["transcript"]
    except:
        return ""


# =============================
# GEMINI
# =============================
def ask_gemini(text):

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=text
    )

    return response.text


# =============================
# TEXT TO SPEECH
# =============================
async def tts(text, output):

    communicate = edge_tts.Communicate(
        text,
        "en-IN-NeerjaNeural"
    )

    await communicate.save(output)


# =============================
# HOME
# =============================
@app.route("/")
def home():
    return jsonify({
        "status": "running"
    })


# =============================
# PROCESS AUDIO
# =============================
@app.route("/process_audio", methods=["POST"])
def process_audio():

    uid = str(uuid.uuid4())

    wav_file = os.path.join(AUDIO_FOLDER, uid + ".wav")
    mp3_file = os.path.join(AUDIO_FOLDER, uid + ".mp3")

    with open(wav_file, "wb") as f:
        f.write(request.data)

    text = speech_to_text(wav_file)

    if text == "":
        return jsonify({
            "error": "Speech not detected"
        }), 400

    reply = ask_gemini(text)

    asyncio.run(tts(reply, mp3_file))

    return jsonify({
        "message": reply,
        "file_id": uid,
        "stream_url": "/audio/" + uid
    })


# =============================
# AUDIO DOWNLOAD
# =============================
@app.route("/audio/<file_id>")
def audio(file_id):

    file = os.path.join(AUDIO_FOLDER, file_id + ".mp3")

    if not os.path.exists(file):
        return "Not Found", 404

    return send_file(file, mimetype="audio/mpeg")


# =============================
# MAIN
# =============================
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
