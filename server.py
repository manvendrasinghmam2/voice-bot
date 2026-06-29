from flask import Flask, request, send_file, jsonify
from google import genai
import edge_tts
import asyncio
import os
import requests

app = Flask(__name__)

# ================= GEMINI =================
client = genai.Client(
    api_key=os.environ["AIzaSyD2wHaPjEhxD7ksWdy5vOlLq8ibuFlMyQg"]
)

# ================= DEEPGRAM =================
DEEPGRAM_API_KEY = os.environ["da64902116d270697c6a8a99c27c7aee2071f62e"]

def speech_to_text(audio_file):
    url = "https://api.deepgram.com/v1/listen"

    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "audio/wav"
    }

    with open(audio_file, "rb") as f:
        response = requests.post(url, headers=headers, data=f)

    data = response.json()

    try:
        return data["results"]["channels"][0]["alternatives"][0]["transcript"]
    except:
        return "I couldn't understand that"

# ================= GEMINI =================
def ask_gemini(text):
    res = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=text
    )
    return res.text

# ================= TTS =================
async def tts(text, file):
    t = edge_tts.Communicate(text, "en-IN-NeerjaNeural")
    await t.save(file)

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

    text = speech_to_text("input.wav")
    print("User:", text)

    reply = ask_gemini(text)
    print("Gemini:", reply)

    speak(reply, "output.mp3")

    return send_file("output.mp3", mimetype="audio/mpeg")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
