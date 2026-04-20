# Build frontend
FROM oven/bun:latest AS builder

WORKDIR /project/website
COPY website/package.json website/bun.lock ./
RUN bun install --frozen-lockfile

COPY website/ .
RUN mkdir -p ../backend && bun run build

# Backend and final image
FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y ffmpeg libgl1 libglib2.0-0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY scripts/ /scripts/
# Copy static build from builder
COPY --from=builder /project/backend/static /app/static

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]