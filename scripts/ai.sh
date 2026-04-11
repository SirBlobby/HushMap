#!/bin/bash
# patriotai.sh - Send a message to Patriot AI and decode the streamed response
# Usage: ./patriotai.sh "Your message here" [conversation_id]

CONVERSATION_ID="${2:-5e752e56-06c6-ec73-1f13-456029ce1299}"
MESSAGE="${1:-Hello}"

curl -s -N -X POST "https://patriotai.gmu.edu/api/internal/userConversations/${CONVERSATION_ID}/segments" \
  -H 'accept: */*' \
  -H 'accept-language: en-US,en;q=0.9' \
  -H 'authorization: Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6InJDaTAwaFQ0ZjlhM3JtcXJuSUYtZEpyNnpMWEdNQllwSS1YcGVrN1g4dFUiLCJ0eXAiOiJKV1QifQ.eyJ1cG4iOiJjNDQ2ZDlhMC00YWZjLTQ5YzAtOWQ2YS1lYTM4YWZjODM4NTIiLCJpcCI6IkVudHJhSWQiLCJlbWFpbCI6ImdtYW5qdW5hQGdtdS5lZHUiLCJ1dm8iOnsiaWQiOiJjNDQ2ZDlhMC00YWZjLTQ5YzAtOWQ2YS1lYTM4YWZjODM4NTIiLCJuIjoiR2FnYW4gTWFuanVuYXRoYSJ9LCJ1ciI6W10sImNhcCI6W10sInYiOiIyLjI2MDUuNDQ3Mi4wIiwibmJmIjoxNzc1OTE5OTc1LCJleHAiOjE3NzU5MjE3NzUsImlhdCI6MTc3NTkxOTk3NSwiaXNzIjoiaHR0cHM6Ly9uZWJ1bGFvbmUuYWkiLCJhdWQiOiJOZWJ1bGFPbmUifQ.YQQZ0An_VFutZx_xLGkI3TN8e9qUR-rs5IzGoSbuVJWd8FEq2wFNK5xoH4m8kPuviE-4GoRtiEaQANNRwA9T1VNolk4ydvbcmSlwfTA4rXQ0v0d-Evy_g-K1AasJBqqgo3bQI4YTVeWaLFckr9XFq3gVLoNdhANtq6YxsVtIGvBS7Y6nrO14EhxzBJ9e9PQXtTqmp4yxvO0DmTN1D4Se6tgWqxpA31muq3Lk3QsWeu1QaAOlS6vDf6xCbLslOtM1I5dHyZc5TuMD67v8dcUEoUtlRLevPZQPe0l-398p3c2cgCkAyzJsGQiVZK7q80lr7q0YMPu8eLdb_fv9yZU_PA' \
  -H 'content-type: application/json' \
  -H 'origin: https://patriotai.gmu.edu' \
  -H 'referer: https://patriotai.gmu.edu/chat/8c3fc7f0-7c8b-4f2f-849c-5e2a45915066/5e752e56-06c6-ec73-1f13-456029ce1299' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36' \
  -H 'x-cosmos-session-219665: 0:-1#4733' \
  -H 'x-cosmos-session-446290: 0:-1#107702' \
  -H 'x-cosmos-session-58544: 0:-1#1960055' \
  -H 'x-cosmos-session-875088: 0:-1#119189' \
  -H 'x-cosmos-session-890600: 0:-1#454777' \
  -H 'x-timezone: America/New_York' \
  --data-raw "{\"question\":\"${MESSAGE}\",\"visionImageIds\":[],\"attachmentIds\":[],\"segmentTraceLogLevel\":\"NonPersisted\"}" \
| while IFS= read -r line; do
    if [[ "$line" == event:* ]]; then
      EVENT="${line#event: }"
    elif [[ "$line" == data:* ]]; then
      DATA="${line#data: }"
      DECODED=$(echo "$DATA" | base64 --decode 2>/dev/null)
      case "$EVENT" in
        "response-updated")
          printf "%s" "$DECODED"
          ;;
        "step-update")
          echo -e "\n[${DECODED}]" >&2
          ;;
        "conversation-and-segment-id")
          echo -e "\n[IDs: ${DECODED}]" >&2
          ;;
        "no-more-data")
          echo ""
          ;;
      esac
    fi
  done