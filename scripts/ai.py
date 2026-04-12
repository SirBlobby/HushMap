
import base64
import urllib.request
import urllib.error
import json
import sys
import uuid

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

CONVERSATION_ID = "290c9cab-ab30-3300-2a09-ed08b67fd0f8"
CHAT_ID = "d19b64a3-d339-4d57-b61e-1d7d81844f7b"

HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6ImtTQTY0dEFUMEx3RERELTdXbG5VRU1TQXBULXR2dl94WUtWc0lHNW1nR1kiLCJ0eXAiOiJKV1QifQ.eyJ1cG4iOiIyNjMyMDYyNy1lODMxLTQ5YzQtYjNmYS1jZTA0MzUwYzM3ZTMiLCJpcCI6IkVudHJhSWQiLCJlbWFpbCI6InNuYWdlc2h3QHVtZC5lZHUiLCJ1dm8iOnsiaWQiOiIyNjMyMDYyNy1lODMxLTQ5YzQtYjNmYS1jZTA0MzUwYzM3ZTMiLCJuIjoiU2FtZWVyYSBOYWdlc2h3YXIifSwidXIiOltdLCJjYXAiOlsiYTc5YmUyMTMtMTBhZS00MWE3LWJjZmYtOTdkMmI2YmE3MDY5Il0sInYiOiIyLjI2MDUuNDQ3Mi4wIiwibmJmIjoxNzc1OTYwMjEyLCJleHAiOjE3NzU5NjIwMTIsImlhdCI6MTc3NTk2MDIxMiwiaXNzIjoiaHR0cHM6Ly9uZWJ1bGFvbmUuYWkiLCJhdWQiOiJOZWJ1bGFPbmUifQ.hROwQyDGEHB9qb9dzOLUxsVP_y9_EUsn04qz1GkXPpi2phd1HH7-VlNn1OCrS58V7JqPEB2YiK_ZRYpCPwAMO9BIPpR-cZ_3QO0fJ76qga7m8yXw4uscuD2MID26CuF_urpQfL1mQ8dQkQzcJlQb6RRUrfeDJd210U9jPnTA5gNZ36_RNNLdZkfWtwJGf_v3PH-zp2DNqpBpCWWGQoiHHFi0bAxeiRug4e5l-5nSg6-R9WX0M0nmwe4GZRZxyVwRjLxklO1Iwl0q3cXHGfs-7SX2OUSxJ70acX0-J9YRrKn2s0LHc1j1s-1AWEU8SLkuWRMMmMPYQg9AUVP3K2bHnA",
    "content-type": "application/json",
    "cookie": "_hjSessionUser_2558111=eyJpZCI6ImRiZWU0OTM1LTY4N2YtNTBmYi1iYTRiLTQ0OGQzMGU2YmJmNiIsImNyZWF0ZWQiOjE3MjQ0MjI1NDk3NDAsImV4aXN0aW5nIjp0cnVlfQ==; _ga_J7C3S6XNGQ=GS1.2.1741641087.6.1.1741641118.0.0.0; _ga_GY230X48CS=GS1.1.1741641086.6.1.1741641267.0.0.0; _scid=LJweNfZGjcU7NsVqpXwAu0eh2rLJ-e-J; _ga_F7KW1RHXXJ=GS1.1.1742912613.5.1.1742912797.0.0.0; _ga_384233029=GS1.1.1744312929.5.1.1744312963.0.0.0; _ga_6N9GRW79WF=GS1.1.1744312929.5.1.1744312963.26.0.0; _ga_9PPFFFRJRX=GS1.1.1744480935.2.1.1744481403.0.0.0; _ga_8Y3285ZTEY=GS1.1.1744952270.1.0.1744952277.0.0.0; _ga_K9TWF4LFGP=GS1.1.1744953024.1.0.1744953028.0.0.0; _sctr=1%7C1744948800000; _scid_r=OxweNfZGjcU7NsVqpXwAu0eh2rLJ-e-JYGQd8A; _ga_MQHQPVLC6S=GS1.1.1744953095.3.1.1744953338.0.0.0; _ga_SRFRDRC7G1=GS1.1.1744953418.3.1.1744953560.0.0.0; _ga_NT2KN2BD65=GS1.1.1744998849.9.1.1744999196.50.0.0; _ga_REF6NPHL90=GS1.1.1744998849.9.1.1744999196.0.0.0; _uetvid=36561bc06e1311efb03ab5c34017d187; _ga_3KLZVDGFWL=GS1.1.1745015053.5.1.1745015076.37.0.0; _ga_M6HVP1ZCF9=GS1.1.1745035695.4.0.1745035695.0.0.0; ajs_anonymous_id=%22b532ab47-5c0b-4ecf-8822-f443981350a6%22; _ga_4L4R6J6KT4=GS1.1.1745607087.1.1.1745607223.0.0.0; cf_clearance=wQavNkKoI8yPem3QRdKImMR_z8CC7lcHlWKQiCqQp4E-1746318548-1.2.1.1-Mxp8cxuKNHfg5EdISFbkS.reTpDvTBL86CDxS6n1E0desmF4KWk8jRHerXCyiBGutuFyh3o2pCLmAksl8SqZKzSkg7IYW5awqmDNwRyoNknH4rvoxeTrY413y51QZunpHTKifxrQwxmFbEZhFIyxzkg0BFsiLMg.7K4IFIZMePCVLvs_s6YA2GMqWlgGXXD9XqsI98KYxn2i1bk1I6jsWQ9IN9P_cxWW87BSClEQDHvH3KIMHv1lTMpIZ86lzPsq7DQsNwKMNwrfO1XdKsqaH.dCuUqoHIqQNrT3Qg_wg19bANykYvLREa0IGZTMkQOuu5Ae7CdvL..Zu33sodAnSlMGRwvOWMSVpN9VG633o0E; _ga_F7V05TJ56H=GS2.1.s1746317216$o2$g1$t1746318556$j0$l0$h0; _ga_9QXK71PHV1=GS1.1.1746384515.2.1.1746384560.0.0.0; _ga_RC4XHY2ZT5=GS2.1.s1746730862$o8$g0$t1746730864$j0$l0$h0; _clck=lnjy10%7C2%7Cfvs%7C0%7C1706; _ga_6VXTC1Y945=GS2.1.s1746850953$o26$g1$t1746851105$j0$l0$h0; _ga_XH45N761B7=GS2.1.s1746850953$o26$g1$t1746851105$j0$l0$h0; _ga_D2M3FRVYM7=GS2.1.s1747238510$o31$g1$t1747239071$j0$l0$h0; _ga_W3Y0KTDFVX=GS2.1.s1747592603$o4$g0$t1747592612$j0$l0$h0; _ga_N30MS2LW8D=GS2.2.s1747774722$o3$g0$t1747774722$j0$l0$h0; _ga_PXRHVCCC6N=GS2.2.s1747810639$o8$g0$t1747810639$j0$l0$h0; _ga_6HFQB7M478=GS2.1.s1748670259$o8$g1$t1748671063$j60$l0$h0; _ga_1C3R5LH705=GS2.1.s1749344180$o3$g1$t1749344537$j60$l0$h0; _ga_29TPK5T4VJ=GS2.1.s1749600922$o3$g1$t1749600952$j30$l0$h0; _ga_0ME57WCM7H=GS2.1.s1753213282$o13$g0$t1753213290$j52$l0$h0; _ga_6RJ22ZEGTP=GS2.1.s1753556865$o29$g1$t1753557380$j60$l0$h0; _ga_QFQ5PJP2QH=GS2.1.s1754337674$o55$g1$t1754338156$j60$l0$h0; _ga_0RDH09ZGCK=GS2.1.s1754359762$o34$g1$t1754360015$j60$l0$h0; _ga_3KD4QBE6RB=GS2.1.s1754664962$o4$g1$t1754665018$j4$l0$h0; _ga_4QVNE3V6C4=GS2.1.s1754664852$o7$g1$t1754665383$j3$l0$h0; _ga_XPNWG40YWF=GS2.1.s1755199103$o5$g1$t1755199120$j43$l0$h0; _ga_FWRTZ8V96T=GS2.1.s1755199122$o26$g1$t1755200694$j60$l0$h0; _ga_60LC732FSD=GS2.1.s1756921145$o15$g0$t1756921145$j60$l0$h0; _ga=GA1.1.1995252296.1724421767; _ga_QYVCRT1RJR=GS2.1.s1759207336$o2$g1$t1759207386$j10$l0$h0; _ga_R7NZ5XV4TT=GS2.1.s1770084108$o1$g1$t1770084132$j36$l0$h0; nmstat=34df7750-5a57-a16a-b809-91d39c8cdad7; dtCookie=v_4_srv_12_sn_C3E3A26387C64F65978660E99C21A81F_perc_100000_ol_0_mul_1_app-3Af9eed1d550ab4737_1; monkey=95c3341f-14a4-426c-afd8-38a80519db0c; rxVisitor=1775405101563KQ4KME9Q0OUSAA5FQF00GF7MAF5HBHK7; rxvt=1775406901833|1775405101563; dtPC=12$5101562_270h-vCJMBJTLHBDHWNMMBPPQVPUMAHKMGRERL-0e0; _ga_E9M33B2469=GS2.1.s1775405075$o56$g0$t1775405113$j22$l0$h0; dtSa=true%7CKD%7C-1%7CPage%3A%20dropAdd%3Fnull%7C-%7C1775405138163%7C5101562_270%7Chttps%3A%2F%2Fapp.testudo.umd.edu%2F%7C%7C%7C%2Fmain%2FdropAdd%3Fnull%26termId%3D202608%7C",
    "origin": "https://terpai.umd.edu",
    "priority": "u=1, i",
    "referer": f"https://terpai.umd.edu/chat/{CHAT_ID}/{CONVERSATION_ID}",
    "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "x-cosmos-session-281286": "0:-1
    "x-cosmos-session-295334": "0:-1
    "x-cosmos-session-317755": "0:-1
    "x-cosmos-session-382299": "0:-1
    "x-cosmos-session-418988": "0:-1
    "x-cosmos-session-793952": "0:-1
    "x-timezone": "America/New_York",
}


INITIAL_PARENT_SEGMENT_ID = "d7765a66-a24b-4620-b003-11b4c1ed2c36"


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