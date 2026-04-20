import os
import io
import struct
import tempfile
import subprocess
import asyncio
import requests
import json
import base64
import urllib.request
import time
import sys

# Add scripts directory to path to import fake data generator
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))
try:
    from generate_fake_data import get_fake_data
except ImportError:
    print("Warning: Could not import get_fake_data from scripts/generate_fake_data.py")
    def get_fake_data(locations): return []

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv
from vision import analyze_room_image
from google import genai

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


USE_DB = os.getenv("USE_DB", "false").lower() == "true"

import certifi
if USE_DB:
    MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    mongo_client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = mongo_client.study_buddy_db
    study_rooms_collection = db.study_rooms
else:
    print("Running in in-memory mode. MongoDB is disabled. Set USE_DB=true to enable.")

# Fake data cache
_fake_data_cache = None
_fake_data_cache_time = 0

def _get_cached_fake_data():
    global _fake_data_cache, _fake_data_cache_time
    now = time.time()
    # Cache for 5 minutes (300 seconds)
    if _fake_data_cache is None or now - _fake_data_cache_time > 300:
        # Assuming UMD_LOCATIONS is defined further down, but we can just use the global
        _fake_data_cache = get_fake_data(UMD_LOCATIONS)
        _fake_data_cache_time = now
    return _fake_data_cache


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

CONVERSATION_ID = os.getenv("TERP_AI_CONVERSATION_ID", "37fa27cc-542a-c8a8-9c31-9d1954fdc1d2")
HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7",
    "authorization": f"Bearer {os.getenv('TERP_AI_BEARER_TOKEN', '')}",
    "baggage": "sentry-environment=TerpAI,sentry-release=2.2605.4472,sentry-public_key=c41f6dfb98d5bed12037e17e78c2c5d3,sentry-trace_id=250c82a03041415b99422d838ccc7003,sentry-org_id=4504359075840000,sentry-sampled=false,sentry-sample_rand=0.34017479518051186,sentry-sample_rate=0",
    "content-type": "application/json",
    "origin": "https://terpai.umd.edu",
    "priority": "u=1, i",
    "referer": f"https://terpai.umd.edu/chat/1eaa95ea-9b73-4850-8534-d1552401513a/{CONVERSATION_ID}",
    "sec-ch-ua": "\"Chromium\";v=\"146\", \"Not-A.Brand\";v=\"24\", \"Microsoft Edge\";v=\"146\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "sentry-trace": "250c82a03041415b99422d838ccc7003-9a9ec11d7fd0293b-0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0",
    "x-cosmos-session-281286": "0:-1",
    "x-cosmos-session-295334": "0:-1",
    "x-cosmos-session-317755": "0:-1",
    "x-cosmos-session-382299": "0:-1",
    "x-cosmos-session-418988": "0:-1",
    "x-cosmos-session-793952": "0:-1",
    "x-request-id": "6a128b8a-7f63-4f97-a40b-bfd31b4a376e",
    "x-timezone": "America/New_York",
}

def _write_wav_to_buffer(pcm_data: bytes, sample_rate: int = SAMPLE_RATE) -> bytes:
    """Wrap raw PCM data in a WAV header and return the full WAV bytes."""
    data_size = len(pcm_data)
    byte_rate = sample_rate * NUM_CHANNELS * (BITS_PER_SAMPLE // 8)
    block_align = NUM_CHANNELS * (BITS_PER_SAMPLE // 8)

    buf = io.BytesIO()
    buf.write(b"RIFF")
    buf.write(struct.pack("<I", 36 + data_size))
    buf.write(b"WAVE")
    buf.write(b"fmt ")
    buf.write(struct.pack("<I", 16))
    buf.write(struct.pack("<H", 1))
    buf.write(struct.pack("<H", NUM_CHANNELS))
    buf.write(struct.pack("<I", sample_rate))
    buf.write(struct.pack("<I", byte_rate))
    buf.write(struct.pack("<H", block_align))
    buf.write(struct.pack("<H", BITS_PER_SAMPLE))
    buf.write(b"data")
    buf.write(struct.pack("<I", data_size))
    buf.write(pcm_data)
    return buf.getvalue()

def _transcribe_pcm(pcm_data: bytes, sample_rate: int = SAMPLE_RATE) -> str:
    """Transcribe raw PCM audio using faster-whisper via a temp WAV file."""
    from faster_whisper import WhisperModel
    print(f"  Using sample rate: {sample_rate} Hz")


    num_samples = len(pcm_data) // 2
    if num_samples > 0:
        samples = list(struct.unpack(f"<{num_samples}h", pcm_data[:num_samples * 2]))
        min_s, max_s = min(samples), max(samples)
        mean_s = sum(samples) / num_samples
        rms = (sum(s * s for s in samples) / num_samples) ** 0.5
        print(f"  PCM stats (raw): {num_samples} samples, min={min_s}, max={max_s}, mean={mean_s:.1f}, RMS={rms:.1f}")


        dc_offset = int(round(mean_s))
        samples = [max(-32768, min(32767, s - dc_offset)) for s in samples]
        pcm_data = struct.pack(f"<{num_samples}h", *samples)


        rms_fixed = (sum(s * s for s in samples) / num_samples) ** 0.5
        print(f"  PCM stats (fixed): DC offset removed={dc_offset}, RMS={rms_fixed:.1f}")

    wav_data = _write_wav_to_buffer(pcm_data, sample_rate=sample_rate)

    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".wav")
    try:
        with os.fdopen(tmp_fd, "wb") as f:
            f.write(wav_data)


        debug_path = os.path.join(os.path.dirname(__file__), "debug_audio.wav")
        with open(debug_path, "wb") as df:
            df.write(wav_data)
        print(f"  Debug WAV saved to: {debug_path}")


        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, info = model.transcribe(tmp_path, beam_size=5)
        seg_list = list(segments)
        print(f"  Whisper: {len(seg_list)} segments, language={info.language}, prob={info.language_probability:.2f}")
        for i, seg in enumerate(seg_list):
            print(f"    Seg {i}: [{seg.start:.1f}s-{seg.end:.1f}s] '{seg.text}'")
        text = " ".join([seg.text for seg in seg_list])
        return text.strip()
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def get_terp_ai_response(message: str) -> str:
    """Send text to Terp AI and return the full response. Fallback to Gemini if needed."""
    url = f"https://terpai.umd.edu/api/internal/userConversations/{CONVERSATION_ID}/segments"
    payload = {
        "question": message,
        "visionImageIds": [],
        "attachmentIds": [],
        "segmentTraceLogLevel": "NonPersisted",
        "lineage": {
            "parentSegmentId": "83f997ca-5089-4568-ae23-fb2d5a6d5855",
            "lineageType": "Question"
        }
    }

    full_response = ""
    event = None
    try:
        resp = requests.post(url, json=payload, headers=HEADERS, stream=True, timeout=10, verify=False)
        resp.raise_for_status()
        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue
            if line.startswith("event: "):
                event = line[7:]
            elif line.startswith("data: "):
                data = line[6:]
                decoded = base64.b64decode(data).decode("utf-8")
                if event == "response-updated":
                    full_response += decoded
        resp.close()
        if full_response:
            return full_response
        else:
            raise Exception("Empty response from Terp AI")
    except Exception as e:
        print(f"Terp AI error, falling back to Gemini: {e}")
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key or api_key == "your_gemini_api_key":
                return "Terp AI is unavailable and Gemini fallback is not configured."
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=message
            )
            return response.text
        except Exception as gemini_e:
            print(f"Gemini fallback error: {gemini_e}")
            return "I am sorry, both Terp AI and the Gemini fallback encountered an error."


def _convert_to_pcm(audio_data: bytes, input_format: str = "mp3") -> Optional[bytes]:
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

def _generate_tts(text: str) -> Optional[bytes]:
    """Generate speech audio from text using ElevenLabs TTS API."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")
    if not api_key or api_key == "your_elevenlabs_api_key_here":
        print("ElevenLabs API key not configured")
        return None


    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=pcm_16000"

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/octet-stream",
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
        pcm_data = resp.content

        if not pcm_data:
            return None

        print(f"TTS: received {len(pcm_data)} bytes of PCM audio")
        return pcm_data

    except requests.exceptions.RequestException as e:
        print(f"ElevenLabs TTS error: {e}")
        return None


_latest_tts_wav = None

@app.get("/api/tts-audio")
async def get_tts_audio():
    global _latest_tts_wav
    if _latest_tts_wav is None:
        return Response(status_code=404, content=b"No audio available")
    return Response(content=_latest_tts_wav, media_type="audio/wav")

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
                        audio_buffer = bytearray()
                        device_sample_rate = msg.get("sample_rate", SAMPLE_RATE)

                        print(f"Received stop_listening event. Buffer size: {len(pcm_data)} bytes, sample_rate: {device_sample_rate} Hz")

                        if len(pcm_data) < 3200:
                            print("Audio too short, ignoring.")
                            await websocket.send_bytes(b"")
                            continue


                        print("Transcribing...")
                        user_text = _transcribe_pcm(pcm_data, sample_rate=device_sample_rate)
                        if not user_text:
                            print("Transcription failed or empty.")
                            await websocket.send_text(json.dumps({"event": "error", "msg": "No speech detected"}))
                            continue

                        print(f"User said: {user_text}")


                        print("Sending to Terp AI...")
                        context_str = get_latest_locations_context()
                        augmented_prompt = f"USER ASKS: {user_text}\n\n[SYSTEM CONTEXT - LATEST UMD ROOM STATS TO HELP YOU ANSWER IF ASKED]:\n{context_str}"
                        ai_response_text = get_terp_ai_response(augmented_prompt)
                        if not ai_response_text:
                            print("No response from Terp AI.")
                            await websocket.send_text(json.dumps({"event": "error", "msg": "No AI response"}))
                            continue

                        print(f"Terp AI response: {ai_response_text}")


                        print("Generating TTS...")
                        tts_pcm = _generate_tts(ai_response_text)

                        if tts_pcm:

                            global _latest_tts_wav
                            _latest_tts_wav = _write_wav_to_buffer(tts_pcm)
                            print(f"TTS WAV ready: {len(_latest_tts_wav)} bytes, serving via /api/tts-audio")
                            await websocket.send_text(json.dumps({
                                "event": "tts_ready",
                                "size": len(_latest_tts_wav)
                            }))
                        else:
                            print("TTS failed.")
                            await websocket.send_text(json.dumps({"event": "error", "msg": "TTS failed"}))

                except json.JSONDecodeError:
                    pass
                except Exception as e:
                    print(f"Error processing message: {e}")
                    await websocket.send_text(json.dumps({"event": "error", "msg": str(e)[:100]}))
    except (WebSocketDisconnect, RuntimeError):
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

def get_latest_locations_context() -> str:
    """Fetch the latest stats for each known location to feed as AI context."""
    room_dict = {loc["id"]: loc["name"] for loc in UMD_LOCATIONS}
    
    if USE_DB:
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        pipeline = [
            {"$match": {"date": {"$gte": twenty_four_hours_ago}}},
            {"$sort": {"date": -1}},
            {"$group": {
                "_id": "$room_id",
                "latest_db": {"$first": "$db"},
                "time": {"$first": "$date"}
            }}
        ]
        latest_stats = list(study_rooms_collection.aggregate(pipeline))
    else:
        fake_data = _get_cached_fake_data()
        latest_stats_map = {}
        # Data is naturally sorted chronologically in our generator, so reverse it
        for d in reversed(fake_data):
            if d["room_id"] not in latest_stats_map:
                latest_stats_map[d["room_id"]] = {
                    "_id": d["room_id"],
                    "latest_db": d["db"],
                    "time": d["date"]
                }
        latest_stats = list(latest_stats_map.values())

    if not latest_stats:
        return "No recent location noise stats available today."

    lines = ["Latest Study Room Stats:"]
    for stat in latest_stats:
        room_id = stat.get("_id")
        name = room_dict.get(room_id, room_id)
        db = stat.get("latest_db", 0.0)

        status = "Quiet"
        if isinstance(db, (int, float)):
            if db >= 65: status = "Loud"
            elif db >= 55: status = "Moderate"

        lines.append(f"- {name}: Noise Level {db:.1f} dB ({status})")

    return "\n".join(lines)

@app.post("/api/study-rooms")
async def create_study_room_data(data: StudyRoomData):

    is_valid_location = False
    req_lng, req_lat = data.location.coordinates[0], data.location.coordinates[1]

    for loc in UMD_LOCATIONS:
        if abs(loc["lng"] - req_lng) < 0.0001 and abs(loc["lat"] - req_lat) < 0.0001:
            is_valid_location = True

            data.location.coordinates = [loc["lng"], loc["lat"]]
            data.room_id = loc["id"]
            break

    if not is_valid_location:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid location. Coordinates must correspond to a known UMD location.")

    if not data.date:
        data.date = datetime.utcnow()
    doc = data.dict()
    
    if USE_DB:
        result = study_rooms_collection.insert_one(doc)
        return {"id": str(result.inserted_id), "room_id": data.room_id, "status": "success"}
    else:
        return {"id": "dummy_id", "room_id": data.room_id, "status": "success (in-memory, not saved)"}

@app.get("/api/study-rooms")
async def get_study_room_data():
    rooms = list(study_rooms_collection.find({}, {"_id": 0}))
    return {"data": rooms}

@app.get("/api/study-rooms/history")
async def get_study_room_history():
    """Get all study room data from the last 24 hours."""
    if USE_DB:
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        rooms = list(study_rooms_collection.find(
            {"date": {"$gte": twenty_four_hours_ago}},
            {"_id": 0}
        ).sort("date", -1))
    else:
        rooms = _get_cached_fake_data()
        # Ensure we don't leak ObjectIds or non-serializable stuff
        # Dates are naturally sorted but let's reverse them to match MongoDB behavior (newest first)
        rooms = list(reversed(rooms))
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
