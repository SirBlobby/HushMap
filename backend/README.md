<div align="center">
  <h1>HushMap: AI Services API</h1>
  <p>
    <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"></a>
    <a href="https://python.org"><img src="https://img.shields.io/badge/Python_3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
    <img src="https://img.shields.io/badge/Ultralytics-YOLOv8-FF0000?style=for-the-badge" alt="YOLOv8 Vision">
    <img src="https://img.shields.io/badge/Whisper-STT-4A90E2?style=for-the-badge" alt="Whisper">
  </p>
  <p><i>The central nervous system linking physical M5GO devices, external Computer Vision tensors, and Conversational NLP APIs synchronously.</i></p>
</div>

---

## Setup Instructions

### Prerequisites
1. **Python 3.10+** is strictly recommended to support asynchronous typing paradigms.
2. **FFmpeg** must be successfully registered onto your OS PATH environments. This engine handles the core conversions decoding MP3 output arrays into 16-bit, 16kHz Mono arrays natively required for browser contexts:
   - **Ubuntu/Debian**: `sudo apt install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Windows**: Install globally via the [FFmpeg website](https://ffmpeg.org/download.html).

### Environment Initialization

Bootstrap the virtual environment and initialize project dependencies:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration Tokens

Provide runtime keys securely targeting TerpAI context queues, Gemini Fallback, and ElevenLabs synthesized avatars within a `.env` dotfile:

```ini
ELEVENLABS_API_KEY=sk_...
ELEVENLABS_VOICE_ID=JBFqnCBsd6RMkjVDRZzb
TERP_AI_BEARER_TOKEN=eyJhbGciOiJSUz...
TERP_AI_CONVERSATION_ID=37fa27cc-...
GEMINI_API_KEY=AIza...
MONGODB_URI=mongodb+srv://...
USE_DB=false
```

*Note: `USE_DB` controls whether the application connects to MongoDB (`true`) or uses on-the-fly generated in-memory data for demonstrations (`false`).*

To invoke the engine, simply execute Uvicorn across your `0.0.0.0` loopback:

```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

---

## Gateway Pipelines

### Full-Duplex Subroutines (`/ws/voice`)

This WebSocket proxy establishes a fully integrated multi-turn communication bridge seamlessly interacting between Edge node Hardware APIs (ESP32/M5GO/Browsers) and NLP architectures.

1. **Int16 Byte Array Exchange**: Devices connect to `ws://<server_ip>:8000/ws/voice` and push raw binary frames asynchronously over the socket.
2. **Contextual Augmentation**: The server waits for the `"stop_listening"` payload event to signify a completed audio snippet. That float array is cast through `faster-whisper` and combined seamlessly with real-time decibel tracking telemetry parameters natively attached into the AI user conversation chunk. We utilize **Terp AI** with an automatic, seamless fallback to **Gemini 2.5 Flash** if the primary Terp service is unavailable.
3. **TTS Pipeline Rendering**: Output predictions are caught instantly, forwarded natively into the `ElevenLabs` TTS interface rendering `pcm_16000` wav codecs, and alerted back down to clients using a `tts_ready` dispatcher.

### Tensor Vision Endpoints (`/api/vision/room-status`)

Leveraging OpenCV bindings layered beneath a YOLOv8-driven bounding box topology detector, this `POST` API analyzes raw camera image buffers returning capacity logic natively. 

> [!NOTE] 
> This API calculates euclidean distances algorithmically detecting adjacent proximities between "person" classifiers and untaken "chair" bounding frames to accurately diagnose available seats inside crowded architectures!

**Response Output Protocol:**
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
  ]
}
```

---

## Database Registries

* `GET /api/study-rooms/history`: Pulls the active global repository of logged architectural noise measurements captured universally within the preceding 24 hours. (Uses MongoDB or in-memory generated data based on the `USE_DB` flag).
* `GET /api/study-rooms`: Pulls generic unstructured noise lists.

> [!IMPORTANT]
> The browser frontend strictly configures standard Web Audio API's `ScriptProcessorNode` interfaces routing data synchronously to this backend! Wait to close down pipelines until *after* all WS queues have successfully been delivered.