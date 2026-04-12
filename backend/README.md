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

Update the `.env` file in this directory with your ElevenLabs credentials:

```ini
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=JBFqnCBsd6RMkjVDRZzb
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
   - Transcribes the accumulated PCM audio using `faster-whisper`.
   - Sends the transcribed text to the Terp AI conversational endpoint and waits for the full response.
   - Sends the Terp AI response text to ElevenLabs TTS.
   - Converts the received TTS audio to 16-bit 16kHz Mono PCM.
5. **Streaming Response (Server -> Client):** The server sends the converted PCM audio back to the client as binary frames.
6. **End of Response (Server -> Client):** The server sends an empty binary frame (`b""`) to signal that playback is complete.

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

For the ESP32/M5GO client (`m5go/main.py`), ensure you update the `WS_URL` variable to point to the correct local IP address of the machine running this backend server.

```python
# In m5go/main.py
WS_URL = "ws://192.168.1.100:8000/ws/voice" 
```
