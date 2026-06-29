from flask import Flask, request, send_file, jsonify
from google import genai
import edge_tts
import asyncio
import os
import requests

app = Flask(__name__)

# ================= GEMINI =================
client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

# ================= DEEPGRAM =================
DEEPGRAM_API_KEY = os.environ["DEEPGRAM_API_KEY"]

def speech_to_text(audio_file):
    url = "https://api.deepgram.com/v1/listen?model=nova-2&language=hi"

    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "audio/wav"
    }

    with open(audio_file, "rb") as f:
        response = requests.post(url, headers=headers, data=f)

    try:
        return response.json()["results"]["channels"][0]["alternatives"][0]["transcript"]
    except:
        return "I couldn't understand"

# ================= GEMINI =================
def ask_gemini(text):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=text
    )
    return response.text

# ================= TTS =================
async def tts(text, file):
    communicate = edge_tts.Communicate(
        text,
        "en-IN-NeerjaNeural"
    )
    await communicate.save(file)

def speak(text, file):
    asyncio.run(tts(text, file))

# ================= ROUTES =================
@app.route("/")
def home():
    return jsonify({"status": "running"})

@app.route("/process_audio", methods=["POST"])
def process_audio():

    with open("input.wav", "wb") as f:
        f.write(request.data)

    # STT
    text = speech_to_text("input.wav")
    print("User:", text)

    # Gemini
    reply = ask_gemini(text)
    print("Bot:", reply)

    # TTS
    speak(reply, "output.mp3")

    return send_file("output.mp3", mimetype="audio/mpeg")

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
