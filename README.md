# BitCamp 2026 - AI Study Buddy & Room Monitor

This project is a comprehensive solution featuring an M5GO smart device integration, an AI Voice and Vision Backend, and a Svelte frontend dashboard. It connects physical hardware to advanced AI models (Terp AI, ElevenLabs, YOLOv8) to provide a real-time study buddy experience and a study room occupancy monitor.

## Project Architecture

### 1. Website Frontend (`/website` & Root)
A SvelteKit application providing the user interface for our system.
- Powered by `sv` (Svelte CLI) and Bun.
- Configured for production deployment via Docker.

**Developing:**
```bash
cd website
bun install
bun run dev --open
```

### 2. AI Backend Services (`/backend`)
A FastAPI backend providing two core capabilities:
- **Real-time Voice WebSockets (`/ws/voice`)**: Connects the M5GO device to STT (faster-whisper), an LLM (Terp AI), and TTS (ElevenLabs). It streams audio bytes natively over WebSockets.
- **Vision Occupancy API (`/api/vision/room-status`)**: Uses YOLOv8 object detection to identify people and chairs in a room image, determining if a study room is fully occupied and pairing the closest person to an available chair.

**Developing:**
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8000
```
*(Requires `ffmpeg`, `libgl1-mesa-glx`, and `libglib2.0-0` installed on your system)*

### 3. M5GO Device (`/m5go`)
MicroPython scripts for the M5Stack M5GO device.
- Uses `uwebsockets` to connect to the backend.
- High-quality audio I2S configuration for the internal microphone and speaker.
- Push-to-talk integration: Hold Button A to talk to the AI, release to get an audio response back.

## Docker Setup

The entire stack can be run via Docker Compose, which builds both the Svelte website and the Python AI Backend into a single seamless container.

```bash
docker-compose up --build
```

- **App (Frontend + Backend)**: Runs on port `8000`

## Configuration

Make sure you set up your `.env` variables before running the Docker containers or local servers.

Create a `.env` in the `/backend` folder:
```ini
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=JBFqnCBsd6RMkjVDRZzb
TERP_AI_BEARER_TOKEN=your_jwt_token_here
TERP_AI_CONVERSATION_ID=5e752e56-06c6-ec73-1f13-456029ce1299
MONGODB_URI=mongodb_url_here
```

Update the `/m5go/main.py` file to include your Wi-Fi credentials and the correct local IP for the WebSocket (`WS_URL`).