#!/usr/bin/env python3
import base64
import urllib.request
import urllib.error
import json
import sys
import uuid

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

CONVERSATION_ID = "5e3fb381-ce00-76db-0c03-7757f7521af1"
CHAT_ID = "1eaa95ea-9b73-4850-8534-d1552401513a"

HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6ImtTQTY0dEFUMEx3RERELTdXbG5VRU1TQXBULXR2dl94WUtWc0lHNW1nR1kiLCJ0eXAiOiJKV1QifQ.eyJ1cG4iOiIzMDY0NDY5Yi1mM2E4LTQwOTktYThlYy00ODUwZWI2YjFkZWUiLCJpcCI6IkVudHJhSWQiLCJlbWFpbCI6Imp3dTEyMzQ0QHVtZC5lZHUiLCJ1dm8iOnsiaWQiOiIzMDY0NDY5Yi1mM2E4LTQwOTktYThlYy00ODUwZWI2YjFkZWUiLCJuIjoiSm9saWUgV3UifSwidXIiOltdLCJjYXAiOlsiYTc5YmUyMTMtMTBhZS00MWE3LWJjZmYtOTdkMmI2YmE3MDY5Il0sInYiOiIyLjI2MDUuNDQ3Mi4wIiwibmJmIjoxNzc1OTUzMjU0LCJleHAiOjE3NzU5NTUwNTQsImlhdCI6MTc3NTk1MzI1NCwiaXNzIjoiaHR0cHM6Ly9uZWJ1bGFvbmUuYWkiLCJhdWQiOiJOZWJ1bGFPbmUifQ.DiIFp_bJsPqghC5smL6KNc_vJEcpXLB97VHbU3YFciNQTsENiJ3nBUXWo7Ob36JdqYcb9pIZmnhV-IronFQwDg910jqtJ7-jM-Qdc5UbUAynU07BvCmCFrebIn45BwSMix1C-YZMEdH8hw_oAxLAIC9iK03luJAvJQbJKuENucPN3ashpL0MFRWMv2CEa0a1adRAG9SMUtM8KChbD95dqX9gKLxd6gUcnkUT24C18W904NBwDUj-q6Yq0zjEhBghAlUX_AaNH0wsfH9FTRKD_LBJ5iZ2l1aZNmsFMZC7GTUr1_tPQDp03j4__74o1fE9EGOG68j4uVvJPiXWg68UBQ",
    "content-type": "application/json",
    "cookie": "_ga=GA1.1.602107016.1755869183; _ga_0HWJZKFYZR=GS2.1.s1755881712$o2$g1$t1755883404$j59$l0$h0; nmstat=9fc3b4a6-4cfc-0e78-dc36-dacf7a9c2035; _hjSessionUser_2558111=eyJpZCI6IjFhZDBjMGU4LTA0NWUtNWQxOS1iMTQ3LWI1OTVlMzIxZjAwMiIsImNyZWF0ZWQiOjE3NzU3NzM4MDU2ODQsImV4aXN0aW5nIjpmYWxzZX0=; dtCookie=v_4_srv_9_sn_C923FD12CFA9E0718B2147BD3710C41A_perc_100000_ol_0_mul_1_app-3Af9eed1d550ab4737_1; rxVisitor=17757738068740O0ICIGCE4KHG1MJ665QAFA4SR22A0RF; rxvt=1775782042876|1775780238463; dtSa=-; dtPC=9$373815254_472h-vCQDHRKJPLNDWPEKUQMUGAPAUGKCIVKVG-0e0; _ga_E9M33B2469=GS2.1.s1775780532$o2$g0$t1775780532$j60$l0$h0",
    "origin": "https://terpai.umd.edu",
    "priority": "u=1, i",
    "referer": f"https://terpai.umd.edu/chat/{CHAT_ID}/{CONVERSATION_ID}",
    "sec-ch-ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "x-cosmos-session-295334": "0:-1#744338",
    "x-cosmos-session-317755": "0:-1#190318",
    "x-cosmos-session-382299": "0:-1#263838",
    "x-cosmos-session-418988": "0:-1#4049357",
    "x-cosmos-session-793952": "0:-1#13795",
    "x-timezone": "America/New_York",
}

# The parent segment ID to chain from — update this to your latest segment
INITIAL_PARENT_SEGMENT_ID = "849e2305-e7a8-4ad3-8d1b-acf89b39af2c"


def send_message(message: str, conversation_id: str = CONVERSATION_ID, parent_segment_id: str = None):
    url = f"https://terpai.umd.edu/api/internal/userConversations/{conversation_id}/segments"

    body = {
        "question": message,
        "visionImageIds": [],
        "attachmentIds": [],
        "segmentTraceLogLevel": "NonPersisted",
    }

    if parent_segment_id:
        body["lineage"] = {
            "parentSegmentId": parent_segment_id,
            "lineageType": "Question"
        }

    payload = json.dumps(body).encode("utf-8")

    # Generate fresh per-request headers
    sentry_trace_id = uuid.uuid4().hex
    sentry_span_id = uuid.uuid4().hex[:16]
    headers = dict(HEADERS)
    headers["x-request-id"] = str(uuid.uuid4())
    headers["sentry-trace"] = f"{sentry_trace_id}-{sentry_span_id}-0"
    headers["baggage"] = (
        f"sentry-environment=TerpAI,sentry-release=2.2605.4472,"
        f"sentry-public_key=c41f6dfb98d5bed12037e17e78c2c5d3,"
        f"sentry-trace_id={sentry_trace_id},"
        f"sentry-org_id=4504359075840000,"
        f"sentry-sampled=false,sentry-sample_rand=0.5,sentry-sample_rate=0"
    )

    req = urllib.request.Request(url, data=payload, method="POST")
    for key, value in headers.items():
        req.add_header(key, value)

    event = None
    new_segment_id = None

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
                    raw = line[6:]
                    try:
                        decoded = base64.b64decode(raw).decode("utf-8")
                    except Exception:
                        decoded = raw

                    if event == "response-updated":
                        print(decoded, end="", flush=True)
                    elif event == "step-update":
                        print(f"\n[step: {decoded}]", file=sys.stderr)
                    elif event == "conversation-and-segment-id":
                        print(f"\n[IDs: {decoded}]", file=sys.stderr)
                        try:
                            ids = json.loads(decoded)
                            # Try common key names for the segment ID
                            new_segment_id = (
                                ids.get("segmentId")
                                or ids.get("id")
                                or ids.get("segment_id")
                            )
                        except Exception:
                            pass
                    elif event == "no-more-data":
                        print()

    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()}", file=sys.stderr)
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}", file=sys.stderr)

    return new_segment_id


def main():
    print("Terp AI Chat - Type 'quit' or 'exit' to exit\n")
    last_segment_id = INITIAL_PARENT_SEGMENT_ID

    while True:
        try:
            message = input("You: ").strip()
            if message.lower() in ("quit", "exit"):
                break
            if not message:
                continue

            print("AI: ", end="", flush=True)
            new_id = send_message(message, parent_segment_id=last_segment_id)
            if new_id:
                last_segment_id = new_id
            print()

        except (KeyboardInterrupt, EOFError):
            break

    print("\nGoodbye!")


if __name__ == "__main__":
    main()