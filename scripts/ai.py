#!/usr/bin/env python3
import base64
import urllib.request
import urllib.error
import json
import sys

CONVERSATION_ID = "5e3fb381-ce00-76db-0c03-7757f7521af1"

HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6ImtTQTY0dEFUMEx3RERELTdXbG5VRU1TQXBULXR2dl94WUtWc0lHNW1nR1kiLCJ0eXAiOiJKV1QifQ.eyJ1cG4iOiIzMDY0NDY5Yi1mM2E4LTQwOTktYThlYy00ODUwZWI2YjFkZWUiLCJpcCI6IkVudHJhSWQiLCJlbWFpbCI6Imp3dTEyMzQ0QHVtZC5lZHUiLCJ1dm8iOnsiaWQiOiIzMDY0NDY5Yi1mM2E4LTQwOTktYThlYy00ODUwZWI2YjFkZWUiLCJuIjoiSm9saWUgV3UifSwidXIiOltdLCJjYXAiOlsiYTc5YmUyMTMtMTBhZS00MWE3LWJjZmYtOTdkMmI2YmE3MDY5Il0sInYiOiIyLjI2MDUuNDQ3Mi4wIiwibmJmIjoxNzc1OTUzMjU0LCJleHAiOjE3NzU5NTUwNTQsImlhdCI6MTc3NTk1MzI1NCwiaXNzIjoiaHR0cHM6Ly9uZWJ1bGFvbmUuYWkiLCJhdWQiOiJOZWJ1bGFPbmUifQ.DiIFp_bJsPqghC5smL6KNc_vJEcpXLB97VHbU3YFciNQTsENiJ3nBUXWo7Ob36JdqYcb9pIZmnhV-IronFQwDg910jqtJ7-jM-Qdc5UbUAynU07BvCmCFrebIn45BwSMix1C-YZMEdH8hw_oAxLAIC9iK03luJAvJQbJKuENucPN3ashpL0MFRWMv2CEa0a1adRAG9SMUtM8KChbD95dqX9gKLxd6gUcnkUT24C18W904NBwDUj-q6Yq0zjEhBghAlUX_AaNH0wsfH9FTRKD_LBJ5iZ2l1aZNmsFMZC7GTUr1_tPQDp03j4__74o1fE9EGOG68j4uVvJPiXWg68UBQ",
    "content-type": "application/json",
    "origin": "https://terpai.umd.edu",
    "referer": "https://terpai.umd.edu/chat/1eaa95ea-9b73-4850-8534-d1552401513a/5e3fb381-ce00-76db-0c03-7757f7521af1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "x-cosmos-session-219665": "0:-1#4733",
    "x-cosmos-session-446290": "0:-1#107702",
    "x-cosmos-session-58544": "0:-1#1960055",
    "x-cosmos-session-875088": "0:-1#119189",
    "x-cosmos-session-890600": "0:-1#454777",
    "x-timezone": "America/New_York",
}

def send_message(message: str, conversation_id: str = CONVERSATION_ID):
    url = f"https://terpai.umd.edu/api/internal/userConversations/{conversation_id}/segments"
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
    print("Terp AI Chat - Type 'quit' or 'exit' to exit\n")
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