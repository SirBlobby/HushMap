# AI Voice Services Backend

This directory contains the FastAPI backend for the AI Voice Agent, facilitating communication between the M5GO device, Terp AI, and ElevenLabs.

## Setup Instructions

### Prerequisites
1. **Python 3.9+** is recommended.
2. **FFmpeg** must be installed on the system to handle audio format conversions (MP3 to 16-bit 16kHz PCM).
   - On Ubuntu/Debian: `sudo apt install ffmpeg`
   - On macOS: `brew install ffmpeg`
   - On Windows: Download from the [FFmpeg website](https://ffmpeg.org/download.html) and add to PATH.

### Installation

1. Navigate to the `ai_services` directory.
2. (Optional but recommended) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Update the `.env` file in this directory with your credentials:

```ini
ELEVENLABS_API_KEY=sk_...
ELEVENLABS_VOICE_ID=JBFqnCBsd6RMkjVDRZzb
TERP_AI_BEARER_TOKEN=eyJhbGciOiJSUz...
TERP_AI_CONVERSATION_ID=37fa27cc-542a-c8a8-9c31-9d1954fdc1d2
MONGODB_URI=mongodb+srv://...
```

## Running the Server

Start the FastAPI application using Uvicorn:

```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```
This will start the server and make it accessible on your local network on port 8000.

## WebSocket Endpoints

### `/ws/voice`

This is the primary WebSocket endpoint used by the M5GO device for real-time voice communication.

**Protocol Flow:**

1. **Connection:** The client establishes a WebSocket connection to `ws://<server_ip>:8000/ws/voice`.
2. **Streaming Audio (Client -> Server):** While the user holds the record button, the client continuously sends binary frames containing raw audio data.
   - **Expected Format:** 16-bit signed integer, 16 kHz, Mono PCM.
3. **End of Audio Signal (Client -> Server):** When the user releases the button, the client sends a JSON text frame to signal the end of the recording:
   ```json
   {
       "event": "stop_listening"
   }
   ```
4. **Processing (Server):** Upon receiving the `stop_listening` event, the server executes the AI pipeline:
   - Transcribes the accumulated Int16 PCM audio organically using `faster-whisper`.
   - Injects a MongoDB aggregate map of the latest 24hr Campus Location noise levels seamlessly into the LLM system prompt.
   - Sends the transcribed text & location context to the Terp AI conversational endpoint and waits for the full response.
   - Streams the Terp AI response text directly to ElevenLabs TTS and demands `pcm_16000` via URL flags natively!
5. **TTS Endpoint Notification**: The server saves the TTS audio buffer and pushes a JSON:
   ```json
   {
       "event": "tts_ready",
       "size": 105000
   }
   ```
6. **Audio Callback**: Client queries `GET /api/tts-audio` to play the binary wav response.

## REST Endpoints

### `/api/vision/room-status` (POST)

This endpoint uses a YOLO object detection model to detect people and chairs in a room image, determining if the room is full and pairing the closest chairs to people.

**Request:**
- `file`: (Required) The image file to analyze (e.g., JPEG, PNG) sent as multipart form-data.

**Response:**
Returns a JSON object detailing the room status, counts, and pairings.

```json
{
  "room_status": "full",
  "counts": {
    "people": 2,
    "chairs": 2
  },
  "pairs": [
    {
      "person_index": 0,
      "chair_index": 1,
      "distance": 150.5
    }
  ],
  "details": {
    "people": [ ... ],
    "chairs": [ ... ]
  }
}
```

### `/api/study-rooms` (GET)

Returns a list of all recorded study room data.

### `/api/study-rooms/history` (GET)

Returns a list of all recorded study room data from the last 24 hours, sorted by most recent first.

**Response:**
```json
{
  "data": [
    {
      "location": {
        "type": "Point",
        "coordinates": [-77.3079, 38.8315]
      },
      "db": 65.2,
      "date": "2026-04-12T14:30:00.000Z"
    }
  ]
}
```

## Client Integration Notes

For the ESP32/M5GO hardware client (`m5go/main.py`), ensure you update the `WS_URL` variable to point to the correct internal server IP.

For the Web Frontend (`VoiceButton.svelte`), it uses standard Web Audio API's `ScriptProcessorNode` to bridge the Float32 arrays strictly into 16-Bit Mono over a dynamic WebSocket tunnel automatically.

```python
# In m5go/main.py
WS_URL = "ws://192.168.1.100:8000/ws/voice" 
```
