from flask import Flask, request, send_file
from google import genai
import whisper
import edge_tts
import asyncio

app = Flask(__name__)

client = genai.Client(api_key="AIzaSyD2wHaPjEhxD7ksWdy5vOlLq8ibuFlMyQg")
model = whisper.load_model("base")

def stt(file):
    return model.transcribe(file)["text"]

def gemini(text):
    res = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=text
    )
    return res.text

async def tts(text, out):
    t = edge_tts.Communicate(text, "en-IN-NeerjaNeural")
    await t.save(out)

def speak(text, out):
    asyncio.run(tts(text, out))

@app.route("/process_audio", methods=["POST"])
def process():
    with open("in.wav", "wb") as f:
        f.write(request.data)

    text = stt("in.wav")
    reply = gemini(text)

    speak(reply, "out.mp3")

    return send_file("out.mp3", mimetype="audio/mpeg")

@app.route("/")
def home():
    return {"status": "running"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
