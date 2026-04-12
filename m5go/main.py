import network
import time
import machine
import json
from m5stack import *
from m5ui import *
from uiflow import *

# Attempt to import websocket client (standard on some micropython builds like M5Stack)
try:
    import uwebsockets.client as websockets
except ImportError:
    websockets = None
    lcd.print("websockets module missing", 0, 0, 0xFF0000)

setScreenColor(0x222222)

# --- CONFIGURATION ---
WIFI_SSID = "YOUR_SSID"
WIFI_PASS = "YOUR_PASSWORD"
# Update this to the IP address of your backend server
WS_URL = "ws://192.168.1.100:8000/ws/voice" 
# ---------------------

def draw_status(status, color):
    lcd.fillRect(0, 50, 320, 50, 0x222222)
    lcd.print(status, int((320 - len(status) * 12) / 2), 65, color)

lcd.print("Connecting to WiFi...", 0, 0, 0xFFFFFF)
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASS)

# Simple connection loop
attempts = 0
while not wlan.isconnected() and attempts < 20:
    time.sleep(0.5)
    attempts += 1

if wlan.isconnected():
    lcd.clear()
    lcd.print("WiFi Connected!", 0, 0, 0x00FF00)
    lcd.print(wlan.ifconfig()[0], 0, 20, 0x00FF00)
else:
    lcd.clear()
    lcd.print("WiFi Failed", 0, 0, 0xFF0000)

# Initialize I2S for Microphone (PDM on M5GO/Fire)
try:
    audio_in = machine.I2S(
        0,
        sck=machine.Pin(12),
        ws=machine.Pin(0),
        sd=machine.Pin(34),
        mode=machine.I2S.RX,
        bits=16,
        format=machine.I2S.MONO,
        rate=16000,
        ibuf=4096
    )
except Exception as e:
    lcd.print("Mic I2S Error", 0, 40, 0xFF0000)

# Initialize I2S for Speaker
try:
    audio_out = machine.I2S(
        1,
        sck=machine.Pin(12),
        ws=machine.Pin(0),
        sd=machine.Pin(2),
        mode=machine.I2S.TX,
        bits=16,
        format=machine.I2S.MONO,
        rate=16000,
        ibuf=8192
    )
except Exception as e:
    lcd.print("Speaker I2S Error", 0, 60, 0xFF0000)

ws = None
def connect_ws():
    global ws
    if not websockets:
        draw_status("WS Lib Missing", 0xFF0000)
        return False
    try:
        if ws:
            ws.close()
        ws = websockets.connect(WS_URL)
        return True
    except Exception as e:
        draw_status("WS Connection Error", 0xFF0000)
        return False

draw_status("Hold Button A to Talk", 0xFFFFFF)

buf = bytearray(1024)

while True:
    # m5stack core button check
    if btnA.isPressed():
        if not ws:
            draw_status("Connecting...", 0xFFFF00)
            if not connect_ws():
                time.sleep(1)
                continue
        
        draw_status("Listening...", 0x0000FF)
        
        # Read and send audio while button is held
        while btnA.isPressed():
            try:
                num_read = audio_in.readinto(buf)
                if num_read and num_read > 0 and ws:
                    ws.send(buf[:num_read])
            except Exception as e:
                pass
                
        # Button released
        draw_status("Thinking...", 0xFFFF00)
        try:
            if ws:
                ws.send(json.dumps({"event": "stop_listening"}))
                
                # Wait for response audio
                draw_status("Speaking...", 0x00FF00)
                while True:
                    resp = ws.recv()
                    if resp and isinstance(resp, bytes):
                        if len(resp) == 0:
                            break  # End of audio transmission
                        audio_out.write(resp)
                    else:
                        break # Empty or non-bytes response means end
        except Exception as e:
            draw_status("Error during playback", 0xFF0000)
            ws = None # force reconnect next time
            
        draw_status("Hold Button A to Talk", 0xFFFFFF)
    
    time.sleep(0.05)
