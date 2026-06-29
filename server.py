from flask import Flask, request, send_file, jsonify
from google import genai
import edge_tts
import asyncio
import os

app = Flask(__name__)

# Environment Variable se API key lo
client = genai.Client(
    api_key=os.environ["AIzaSyD2wHaPjEhxD7ksWdy5vOlLq8ibuFlMyQg"]
)

# ---------- Speech To Text ----------
def speech_to_text(audio_file):
    """
    Yahan baad me Deepgram / Google STT /
    AssemblyAI API call aayegi.
    """
    return "Hello"

# ---------- Gemini ----------
def ask_gemini(text):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=text
    )
    return response.text

# ---------- Text To Speech ----------
async def create_voice(text, filename):
    communicate = edge_tts.Communicate(
        text,
        "en-IN-NeerjaNeural"
    )
    await communicate.save(filename)

# ---------- API ----------
@app.route("/")
def home():
    return jsonify({
        "status": "running"
    })

@app.route("/process_audio", methods=["POST"])
def process_audio():

    with open("input.wav", "wb") as f:
        f.write(request.data)

    user_text = speech_to_text("input.wav")

    reply = ask_gemini(user_text)

    asyncio.run(create_voice(reply, "output.mp3"))

    return send_file(
        "output.mp3",
        mimetype="audio/mpeg"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
