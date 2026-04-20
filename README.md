<div align="center">
  <h1>HushMap</h1>
  <h3>AI Intelligent Room Monitor</h3>
  <br />
  <p>
    <a href="https://svelte.dev"><img src="https://img.shields.io/badge/SvelteKit-FF3E00?style=for-the-badge&logo=svelte&logoColor=white" alt="SvelteKit"></a>
    <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI"></a>
    <a href="https://www.mongodb.com/"><img src="https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB"></a>
    <a href="https://m5stack.com/"><img src="https://img.shields.io/badge/IoT-M5GO-blue?style=for-the-badge&logo=microchip&logoColor=white" alt="M5GO"></a>
    <a href="https://docker.com"><img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"></a>
  </p>
</div>

<br/>

HushMap bridges the gap between hardware sensors and top-tier artificial intelligence pipelines (e.g. **Terp AI**, **ElevenLabs**, **YOLOv8**, and **Gemini**), delivering a seamless real-time learning assistant combined with live noise and occupancy metrics.

---

## System Architecture

### 1. Web Dashboard (`/website`)
A responsive, high-fidelity PWA frontend written in Svelte 5 and styled seamlessly with Catppuccin color guidelines.
* **Powered By**: SvelteKit, Vite, and Bun.
* **Features**: Live interactive map tracking, responsive UI, persistent theming, and an autonomous browser-based Voice Agent calling modal interface.
* **Setup**:
  ```bash
  cd website
  bun install
  bun run dev --open
  ```

### 2. AI Backend Services (`/backend`)
A blazing fast asynchronous HTTP server facilitating audio chunking and sensor metrics logic over full-duplex sockets.
* **Core Capabilities**:
  * **Voice Socket Pipelining**: WebSockets (`/ws/voice`) that hook incoming 16-bit PCM arrays into `faster-whisper`.
  * **LLM Context Augmentation**: Seamlessly aggregates live noise statistics (Decibel levels per location) to feed contextual history to the AI engine. Uses **TerpAI** with a seamless fallback to **Gemini 2.5 Flash** if TerpAI is unavailable!
  * **Computer Vision Endpoint**: Exposes a `YOLOv8` tensor API (`/api/vision/room-status`) to parse webcam imagery, pinpoint seating capacities, and locate available chairs algorithmically.
  * **Dynamic Data Source**: Data can either be fetched in real-time from a **MongoDB** database, or simulated on-the-fly via an in-memory generator depending on the `USE_DB` environment flag.
* **Setup**:
  ```bash
  cd backend
  pip install -r requirements.txt
  uvicorn server:app --host 0.0.0.0 --port 8000
  ```
  > [!WARNING]
  > Host devices must have `ffmpeg`, `libgl1-mesa-glx`, and `libglib2.0-0` binaries natively installed to encode audio buffers and execute OpenCV rendering.

### 3. M5GO Hardware Node (`/m5go`)
C-based MicroPython binaries tailored strictly for the IoT edge nodes traversing the physical campus.
* **Features**: Connects internally wired I2S Microphone blocks to route direct byte arrays securely out across WPA/WPA2 networks into the main API gateway using minimal payload overhead. Push-button PTT interfaces built directly into the screen chassis.

---

## Docker Production Setup

The entire monolithic architecture cleanly orchestrates via docker compose. Frontends compile out via SSR, and Python APIs wire natively within a segregated container network loop.

```bash
docker-compose up --build
```
> The global deployment interface listens on port `8000`.

---

For IoT clients, update `/m5go/main.py` explicitly to broadcast to your running router IP namespace matching your specific VLAN.