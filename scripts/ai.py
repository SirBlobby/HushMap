#!/usr/bin/env python3
import base64
import urllib.request
import urllib.error
import json
import sys

CONVERSATION_ID = "5e752e56-06c6-ec73-1f13-456029ce1299"

HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6InJDaTAwaFQ0ZjlhM3JtcXJuSUYtZEpyNnpMWEdNQllwSS1YcGVrN1g4dFUiLCJ0eXAiOiJKV1QifQ.eyJ1cG4iOiJjNDQ2ZDlhMC00YWZjLTQ5YzAtOWQ2YS1lYTM4YWZjODM4NTIiLCJpcCI6IkVudHJhSWQiLCJlbWFpbCI6ImdtYW5qdW5hQGdtdS5lZHUiLCJ1dm8iOnsiaWQiOiJjNDQ2ZDlhMC00YWZjLTQ5YzAtOWQ2YS1lYTM4YWZjODM4NTIiLCJuIjoiR2FnYW4gTWFuanVuYXRoYSJ9LCJ1ciI6W10sImNhcCI6W10sInYiOiIyLjI2MDUuNDQ3Mi4wIiwibmJmIjoxNzc1OTE5OTc1LCJleHAiOjE3NzU5MjE3NzUsImlhdCI6MTc3NTkxOTk3NSwiaXNzIjoiaHR0cHM6Ly9uZWJ1bGFvbmUuYWkiLCJhdWQiOiJOZWJ1bGFPbmUifQ.YQQZ0An_VFutZx_xLGkI3TN8e9qUR-rs5IzGoSbuVJWd8FEq2wFNK5xoH4m8kPuviE-4GoRtiEaQANNRwA9T1VNolk4ydvbcmSlwfTA4rXQ0v0d-Evy_g-K1AasJBqqgo3bQI4YTVeWaLFckr9XFq3gVLoNdhANtq6YxsVtIGvBS7Y6nrO14EhxzBJ9e9PQXtTqmp4yxvO0DmTN1D4Se6tgWqxpA31muq3Lk3QsWeu1QaAOlS6vDf6xCbLslOtM1I5dHyZc5TuMD67v8dcUEoUtlRLevPZQPe0l-398p3c2cgCkAyzJsGQiVZK7q80lr7q0YMPu8eLdb_fv9yZU_PA",
    "content-type": "application/json",
    "origin": "https://patriotai.gmu.edu",
    "referer": "https://patriotai.gmu.edu/chat/8c3fc7f0-7c8b-4f2f-849c-5e2a45915066/5e752e56-06c6-ec73-1f13-456029ce1299",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "x-cosmos-session-219665": "0:-1#4733",
    "x-cosmos-session-446290": "0:-1#107702",
    "x-cosmos-session-58544": "0:-1#1960055",
    "x-cosmos-session-875088": "0:-1#119189",
    "x-cosmos-session-890600": "0:-1#454777",
    "x-timezone": "America/New_York",
}

def send_message(message: str, conversation_id: str = CONVERSATION_ID):
    url = f"https://patriotai.gmu.edu/api/internal/userConversations/{conversation_id}/segments"
    data = json.dumps({
        "question": message,
        "visionImageIds": [],
        "attachmentIds": [],
        "segmentTraceLogLevel": "NonPersisted"
    }).encode("utf-8")

    req = urllib.request.Request(url, data=data, method="POST")
    for key, value in HEADERS.items():
        req.add_header(key, value)

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
                        print(decoded, end="")
                    elif event == "step-update":
                        print(f"\n[{decoded}]", file=sys.stderr)
                    elif event == "conversation-and-segment-id":
                        print(f"\n[IDs: {decoded}]", file=sys.stderr)
                    elif event == "no-more-data":
                        print()
    except urllib.error.HTTPError as e:
        print(f"Error: {e.read().decode()}", file=sys.stderr)
        return

def main():
    print("Patriot AI Chat - Type 'quit' or 'exit' to exit\n")
    while True:
        try:
            message = input("You: ").strip()
            if message.lower() in ("quit", "exit"):
                break
            if not message:
                continue
            print("AI: ", end="")
            send_message(message)
            print()
        except (KeyboardInterrupt, EOFError):
            break
    print("\nGoodbye!")

if __name__ == "__main__":
    main()