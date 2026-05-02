from flask import Flask, request, render_template, jsonify
import logging
import requests
import time
import os
from supabase import create_client
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)
print("🚀 Starting Flask app")
print("📍 Use /test-call to simulate a recording webhook or /voicemails to fetch stored entries")

# ==============================
# 🔑 TWILIO CONFIG (USE ENV IN REAL PROJECT)
# ==============================
TWILIO_SID = "AC5dcbf7e14fbac81a32e290b7dda8225f"
TWILIO_AUTH = "26855e62d563051a76edbd3f4dfb4391"
TWILIO_NUMBER = "+17406380402"
ADMIN_NUMBER = "+919629509259"

twilio_client = Client(TWILIO_SID, TWILIO_AUTH)

# ==============================
# ☁️ SUPABASE CONFIG
# ==============================
SUPABASE_URL = "https://lcnpkbvarexofobmgjcy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxjbnBrYnZhcmV4b2ZvYm1namN5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYwODEwMTAsImV4cCI6MjA5MTY1NzAxMH0.iaTpI9TpOu3xjtYKVOqelxTfmqgL86VO1zClLnT3JXQ"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ==============================
# 🏠 HOME
# ==============================
@app.route("/")
def home():
    return render_template("voice.html")

# ==============================
# 📞 VOICE FLOW
# ==============================
@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()

    response.say("Please leave your voicemail after the beep.")

    response.record(
        action="/recording",
        max_length=60,
        play_beep=True
    )

    return str(response)

# ==============================
# 🎙️ RECORDING CALLBACK
# ==============================
@app.route("/recording", methods=["POST"])
def recording():

    print("\n📩 Twilio Incoming Request")

    recording_url = request.form.get("RecordingUrl")
    caller = request.form.get("From")

    print("Caller:", caller)
    print("Recording URL:", recording_url)

    if not recording_url:
        return "No recording URL"

    try:
        # ✅ safer format: prefer the original URL, but add .mp3 for Twilio recording URLs when needed
        if recording_url.lower().endswith((".mp3", ".wav", ".mpeg")):
            audio_url = recording_url
        else:
            audio_url = recording_url + ".mp3"

        print("⬇️ Downloading audio...", audio_url)

        response = requests.get(audio_url, timeout=15)

        if response.status_code == 404 and not recording_url.lower().endswith(".mp3"):
            fallback_url = recording_url
            print("⚠️ 404 from .mp3 download, retrying original URL:", fallback_url)
            response = requests.get(fallback_url, timeout=15)
            audio_url = fallback_url

        if response.status_code != 200:
            print("❌ Download failed", response.status_code, response.headers.get("Content-Type"), response.text[:200])
            return "Download failed"

        filename = f"{caller}_{int(time.time())}.mp3"

        # ==============================
        # 💾 SAVE LOCALLY
        # ==============================
        local_path = os.path.join(UPLOAD_FOLDER, filename)

        with open(local_path, "wb") as f:
            f.write(response.content)

        # ==============================
        # ☁️ UPLOAD TO SUPABASE STORAGE
        # ==============================
        supabase.storage.from_("recordings").upload(
            filename,
            response.content,
            {"content-type": "audio/mpeg"}
        )

        public_url = f"{SUPABASE_URL}/storage/v1/object/public/recordings/{filename}"

        print("☁️ Uploaded:", public_url)

        # ==============================
        # 🗄️ SAVE TO DATABASE
        # ==============================
        result = supabase.table("voicemails").insert({
            "caller": caller,
            "audio_url": public_url,
        }).execute()

        if getattr(result, "error", None):
            print("❌ DB INSERT FAILED", result.error)
            return jsonify({"error": "DB insert failed", "details": str(result.error)}), 500

        print("✅ DB INSERT SUCCESS")
        print("result.data:", getattr(result, "data", None))

        # ==============================
        # 📩 SMS TO ADMIN
        # ==============================
        try:
            message = twilio_client.messages.create(
                body=f"📩 New voicemail from {caller}\nListen: {public_url}",
                from_=TWILIO_NUMBER,
                to=ADMIN_NUMBER
                )
            print("📨 SMS SID:", message.sid)
        except Exception as e:
            print("❌ SMS ERROR:", str(e))

    except Exception as e:
        print("❌ ERROR:", str(e))
        return str(e)
    return "OK"

# ==============================
# 🧪 TEST ROUTE
# ==============================
@app.route("/test-call")
def test_call():

    data = {
        "RecordingUrl": "https://www.image2url.com/r2/default/audio/1776143437457-b7db775a-4f01-4b9b-b605-a40e610d5065.mp3",
        "From": "+919876543567"
    }

    requests.post("http://127.0.0.1:5000/recording", data=data)

    return "Test triggered"

# ==============================
# 🎤 UPLOAD FROM BROWSER
# ==============================
@app.route("/upload-voice", methods=["POST"])
def upload_voice():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        # Save locally
        filename = f"browser_{int(time.time())}.webm"
        local_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(local_path)

        # Upload to Supabase
        with open(local_path, "rb") as f:
            supabase.storage.from_("recordings").upload(
                filename,
                f.read(),
                {"content-type": "audio/webm"}
            )

        public_url = f"{SUPABASE_URL}/storage/v1/object/public/recordings/{filename}"

        # Save to DB
        result = supabase.table("voicemails").insert({
            "caller": "browser",
            "audio_url": public_url,
        }).execute()

        if getattr(result, "error", None):
            print("❌ DB INSERT FAILED", result.error)
            return jsonify({"error": "DB insert failed", "details": str(result.error)}), 500

        print("✅ Browser upload DB INSERT SUCCESS")
        print("result.data:", getattr(result, "data", None))
        # Send SMS to admin
        try:
            message = twilio_client.messages.create(
                body=f"📩 New voicemail from browser user\nListen: {public_url}",
                from_=TWILIO_NUMBER,
                to=ADMIN_NUMBER
            )
            print("📨 SMS SID (browser):", message.sid)
        except Exception as e:
            print("❌ SMS ERROR (browser):", str(e))
        return jsonify({"success": True, "url": public_url})
    except Exception as e:
        print("❌ UPLOAD ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

# ==============================
# 📋 LIST VOICEMAILS
# ==============================
@app.route("/voicemails")
def voicemails():
    try:
        result = supabase.table("voicemails").select("*").order("id", desc=True).limit(20).execute()
        if getattr(result, "error", None):
            return f"DB error: {result.error}", 500
        rows = getattr(result, "data", [])
        html = "<h2>Recent Voicemails</h2><ul>"
        for row in rows:
            html += f'<li><b>{row.get("caller")}</b>: <a href="{row.get("audio_url")}">Listen</a></li>'
        html += "</ul>"
        return html
    except Exception as e:
        return f"Error: {e}", 500

# ==============================
# 🚀 RUN SERVER
# ==============================
if __name__ == "__main__":
    app.run(debug=True)