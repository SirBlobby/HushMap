import os
import io
import struct
import tempfile
import subprocess
import requests
import json
import base64
import urllib.request
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv
from vision import analyze_room_image

from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Setup
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client.study_buddy_db
study_rooms_collection = db.study_rooms

# Pydantic models for Study Room Data
class GeoJSONPoint(BaseModel):
    type: str = "Point"
    coordinates: List[float]

class StudyRoomData(BaseModel):
    room_id: Optional[str] = None
    location: GeoJSONPoint
    db: float
    date: Optional[datetime] = None

SAMPLE_RATE = 16000
BITS_PER_SAMPLE = 16
NUM_CHANNELS = 1

CONVERSATION_ID = os.getenv("TERP_AI_CONVERSATION_ID", "5e752e56-06c6-ec73-1f13-456029ce1299")
HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "authorization": f"Bearer {os.getenv('TERP_AI_BEARER_TOKEN', '')}",
    "content-type": "application/json",
    "origin": "https://patriotai.gmu.edu",
    "referer": f"https://patriotai.gmu.edu/chat/8c3fc7f0-7c8b-4f2f-849c-5e2a45915066/{CONVERSATION_ID}",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "x-timezone": "America/New_York",
}

def _write_wav_to_buffer(pcm_data: bytes) -> bytes:
    """Wrap raw PCM data in a WAV header and return the full WAV bytes."""
    data_size = len(pcm_data)
    byte_rate = SAMPLE_RATE * NUM_CHANNELS * (BITS_PER_SAMPLE // 8)
    block_align = NUM_CHANNELS * (BITS_PER_SAMPLE // 8)

    buf = io.BytesIO()
    buf.write(b"RIFF")
    buf.write(struct.pack("<I", 36 + data_size))
    buf.write(b"WAVE")
    buf.write(b"fmt ")
    buf.write(struct.pack("<I", 16))
    buf.write(struct.pack("<H", 1))  # PCM
    buf.write(struct.pack("<H", NUM_CHANNELS))
    buf.write(struct.pack("<I", SAMPLE_RATE))
    buf.write(struct.pack("<I", byte_rate))
    buf.write(struct.pack("<H", block_align))
    buf.write(struct.pack("<H", BITS_PER_SAMPLE))
    buf.write(b"data")
    buf.write(struct.pack("<I", data_size))
    buf.write(pcm_data)
    return buf.getvalue()

def _transcribe_pcm(pcm_data: bytes) -> str:
    """Transcribe raw PCM audio using faster-whisper via a temp WAV file."""
    from faster_whisper import WhisperModel
    wav_data = _write_wav_to_buffer(pcm_data)

    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".wav")
    try:
        with os.fdopen(tmp_fd, "wb") as f:
            f.write(wav_data)

        # Initialize the model (using base model for speed)
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(tmp_path, beam_size=5)
        text = " ".join([segment.text for segment in segments])
        return text.strip()
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def get_terp_ai_response(message: str) -> str:
    """Send text to Terp AI and return the full response."""
    url = f"https://patriotai.gmu.edu/api/internal/userConversations/{CONVERSATION_ID}/segments"
    data = json.dumps({
        "question": message,
        "visionImageIds": [],
        "attachmentIds": [],
        "segmentTraceLogLevel": "NonPersisted"
    }).encode("utf-8")

    req = urllib.request.Request(url, data=data, method="POST")
    for key, value in HEADERS.items():
        req.add_header(key, value)

    full_response = ""
    event = None
    try:
        with urllib.request.urlopen(req) as response:
            while True:
                line = response.readline()
                if not line:
                    break
                line = line.decode("utf-8").strip()
                if line.startswith("event: "):
                    event = line[7:]
                elif line.startswith("data: "):
                    data = line[6:]
                    decoded = base64.b64decode(data).decode("utf-8")
                    if event == "response-updated":
                        full_response += decoded
    except Exception as e:
        print(f"Terp AI error: {e}")
        return "I am sorry, there was an error connecting to Terp AI."
    
    return full_response

def _convert_to_pcm(audio_data: bytes, input_format: str = "mp3") -> bytes | None:
    """Convert audio data to 16-bit 16 kHz mono PCM using ffmpeg."""
    try:
        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-f", input_format, "-i", "pipe:0",
                "-f", "s16le",
                "-acodec", "pcm_s16le",
                "-ar", str(SAMPLE_RATE),
                "-ac", str(NUM_CHANNELS),
                "pipe:1",
            ],
            input=audio_data,
            capture_output=True,
            timeout=15,
        )

        if result.returncode != 0:
            print(f"ffmpeg conversion failed: {result.stderr.decode()[:200]}")
            return None

        return result.stdout

    except FileNotFoundError:
        print("ffmpeg not installed")
        return None
    except subprocess.TimeoutExpired:
        print("ffmpeg conversion timed out")
        return None

def _generate_tts(text: str) -> bytes | None:
    """Generate speech audio from text using ElevenLabs TTS API."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")
    if not api_key or api_key == "your_elevenlabs_api_key_here":
        print("ElevenLabs API key not configured")
        return None

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }

    payload = {
        "text": text,
        "model_id": "eleven_flash_v2_5",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True,
        },
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        mp3_data = resp.content

        if not mp3_data:
            return None

        # Convert MP3 to 16-bit 16 kHz mono PCM
        return _convert_to_pcm(mp3_data, input_format="mp3")

    except requests.exceptions.RequestException as e:
        print(f"ElevenLabs TTS error: {e}")
        return None

@app.websocket("/ws/voice")
async def websocket_voice(websocket: WebSocket):
    await websocket.accept()
    print("Device connected to WebSocket.")
    audio_buffer = bytearray()
    
    try:
        while True:
            data = await websocket.receive()
            
            if "bytes" in data:
                audio_buffer.extend(data["bytes"])
                
            elif "text" in data:
                try:
                    msg = json.loads(data["text"])
                    if msg.get("event") == "stop_listening":
                        pcm_data = bytes(audio_buffer)
                        audio_buffer = bytearray()  # Reset for next time
                        
                        print(f"Received stop_listening event. Buffer size: {len(pcm_data)} bytes.")
                        
                        if len(pcm_data) < 3200:
                            print("Audio too short, ignoring.")
                            await websocket.send_bytes(b"")
                            continue
                            
                        # Step 1: Speech to Text
                        print("Transcribing...")
                        user_text = _transcribe_pcm(pcm_data)
                        if not user_text:
                            print("Transcription failed or empty.")
                            await websocket.send_bytes(b"")
                            continue
                        
                        print(f"User said: {user_text}")
                        
                        # Step 2: Terp AI
                        print("Sending to Terp AI...")
                        ai_response_text = get_terp_ai_response(user_text)
                        if not ai_response_text:
                            print("No response from Terp AI.")
                            await websocket.send_bytes(b"")
                            continue
                        
                        print(f"Terp AI response: {ai_response_text}")
                        
                        # Step 3: Text to Speech
                        print("Generating TTS...")
                        tts_pcm = _generate_tts(ai_response_text)
                        
                        if tts_pcm:
                            print(f"Sending {len(tts_pcm)} bytes of PCM back to device.")
                            await websocket.send_bytes(tts_pcm)
                        else:
                            print("TTS failed.")
                            await websocket.send_bytes(b"")
                            
                except json.JSONDecodeError:
                    pass
                except Exception as e:
                    print(f"Error processing message: {e}")
                    await websocket.send_bytes(b"")
    except WebSocketDisconnect:
        print("Device disconnected.")

@app.post("/api/vision/room-status")
async def check_room_status(file: UploadFile = File(...)):
    contents = await file.read()
    result = analyze_room_image(contents)
    return result

UMD_LOCATIONS = [
	{ "id": 'esj', "name": 'Edward St. John (ESJ)', "lng": -76.94209511596014, "lat": 38.987133359608755 },
	{ "id": 'mckeldin', "name": 'McKeldin Library', "lng": -76.94494907523277, "lat": 38.986021017749366 },
	{ "id": 'hornbake', "name": 'Hornbake Library', "lng": -76.94161787005467, "lat": 38.988233373664826 },
	{ "id": 'stem', "name": 'STEM Library', "lng": -76.93942003731279, "lat": 38.988991437126195 },
	{ "id": 'clarice', "name": 'Clarice Library', "lng": -76.9500912552473, "lat": 38.990547823732285 },
	{ "id": 'yahentamitsi', "name": 'Yahentamitsi', "lng": -76.9448027183373, "lat": 38.99108961575231 },
	{ "id": 'iribe', "name": 'Iribe', "lng": -76.93643838603555, "lat": 38.98933701397555 },
	{ "id": 'reckord', "name": 'Reckord Armory', "lng": -76.93897470250619, "lat": 38.98609556181066 },
	{ "id": 'stamp', "name": 'Stamp Student Union', "lng": -76.94473083972326, "lat": 38.988130238874874 }
]

@app.post("/api/study-rooms")
async def create_study_room_data(data: StudyRoomData):
    # Check if the coordinates match one of the known locations (with small tolerance)
    is_valid_location = False
    req_lng, req_lat = data.location.coordinates[0], data.location.coordinates[1]
    
    for loc in UMD_LOCATIONS:
        if abs(loc["lng"] - req_lng) < 0.0001 and abs(loc["lat"] - req_lat) < 0.0001:
            is_valid_location = True
            # Override coordinates to exactly match known location for consistency
            data.location.coordinates = [loc["lng"], loc["lat"]]
            data.room_id = loc["id"]
            break
            
    if not is_valid_location:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid location. Coordinates must correspond to a known UMD location.")

    if not data.date:
        data.date = datetime.utcnow()
    doc = data.dict()
    result = study_rooms_collection.insert_one(doc)
    return {"id": str(result.inserted_id), "room_id": data.room_id, "status": "success"}

@app.get("/api/study-rooms")
async def get_study_room_data():
    rooms = list(study_rooms_collection.find({}, {"_id": 0}))
    return {"data": rooms}

@app.get("/api/study-rooms/history")
async def get_study_room_history():
    """Get all study room data from the last 24 hours."""
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
    rooms = list(study_rooms_collection.find(
        {"date": {"$gte": twenty_four_hours_ago}}, 
        {"_id": 0}
    ).sort("date", -1))
    return {"data": rooms}

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    static_dir = "static"
    if not os.path.exists(static_dir):
        return {"error": "Static directory not found. Please build the frontend."}
        
    static_path = os.path.join(static_dir, full_path)
    if os.path.isfile(static_path):
        return FileResponse(static_path)
    
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
        
    return {"error": "index.html not found in static directory"}
