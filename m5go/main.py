import network
import time
import machine
import json
import math
import _thread
import websocket
from m5stack import *
from m5ui import *
from uiflow import *

setScreenColor(0x222222)

# --- CONFIGURATION ---
WIFI_SSID = "Blobby"
WIFI_PASS = "73556088"
# Update this to the IP address of your backend server
WS_URL = "ws://192.168.137.1:8000/ws/voice" 
# ---------------------

def draw_status(status, color):
    lcd.fillRect(0, 220, 320, 20, 0x222222)
    lcd.print(status, int((320 - len(status) * 8) / 2), 220, color)

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
    time.sleep(1)
    lcd.clear()
else:
    lcd.clear()
    lcd.print("WiFi Failed", 0, 0, 0xFF0000)
    time.sleep(2)
    lcd.clear()

try:
    adc = machine.ADC(34)
    adc.atten(machine.ADC.ATTN_11DB)
except:
    try:
        adc = machine.ADC(machine.Pin(34))
        adc.atten(machine.ADC.ATTN_11DB)
    except:
        adc = None

def get_db():
    if not adc: return 30
    sum_v = 0
    sum_sq = 0
    count = 0
    end_t = time.ticks_ms() + 40 
    while time.ticks_ms() < end_t:
        try:
            v = adc.read()
            sum_v += v
            sum_sq += v * v
            count += 1
        except:
            pass
    
    if count == 0: return 30
    
    mean = sum_v / count
    variance = (sum_sq / count) - (mean * mean)
    
    if variance <= 1: return 30
    amp = math.sqrt(variance)
    if amp <= 1: return 30
    
    # Use your specific calculation formula to properly scale to human DB
    db = 20 * math.log10(amp) + 25
    return db

def init_mic():
    try:
        if hasattr(machine.I2S, "RX"):
            audio_in = machine.I2S(
                0,
                sck=machine.Pin(0),
                ws=machine.Pin(0),
                sd=machine.Pin(34),
                mode=machine.I2S.RX,
                bits=16,
                format=machine.I2S.MONO,
                rate=16000,
                ibuf=4096
            )
            return audio_in
        else:
            # Fallback for old Micropython (e.g. M5Stack UIFlow)
            mode = getattr(machine.I2S, "MODE_MASTER", 1) | getattr(machine.I2S, "MODE_RX", 2)
            if hasattr(machine.I2S, "MODE_PDM"):
                mode |= getattr(machine.I2S, "MODE_PDM", 0)
            
            cfmt = getattr(machine.I2S, "CHANNEL_FMT_ALL_LEFT", 1)
            dfmt = getattr(machine.I2S, "FORMAT_I2S", 1)
            
            try_args = [
                ([getattr(machine.I2S, "NUM0", 0), mode, 16000, 16, cfmt, dfmt], {}),
                ([getattr(machine.I2S, "NUM0", 0), mode, 16000, 16], {}),
                ([getattr(machine.I2S, "NUM0", 0)], {"mode": mode, "sample_rate": 16000, "bits": 16, "channel_format": cfmt, "data_format": dfmt}),
                ([getattr(machine.I2S, "NUM0", 0)], {"mode": mode, "sample_rate": 16000, "bits": 16}),
                ([getattr(machine.I2S, "NUM0", 0)], {"mode": mode, "bck": 0, "ws": 0, "sd": 34, "sample_rate": 16000, "bits": 16}),
                ([], {"mode": mode, "sample_rate": 16000, "bits": 16}),
                ([getattr(machine.I2S, "NUM0", 0)], {"mode": mode}),
                ([], {"mode": mode}),
            ]
            
            audio_in = None
            last_e = None
            for args, kwargs in try_args:
                try:
                    audio_in = machine.I2S(*args, **kwargs)
                    break
                except Exception as e:
                    last_e = e
            if audio_in is None:
                raise Exception("Mic fallback failed: " + str(last_e))
            return audio_in
    except Exception as e:
        print("Mic I2S Error:", repr(e))
        lcd.print("Mic Err: " + str(e)[:20], 0, 40, 0xFF0000)
        return None

def init_spk():
    try:
        if hasattr(machine.I2S, "TX"):
            audio_out = machine.I2S(
                1,
                sck=machine.Pin(12),
                ws=machine.Pin(0),
                sd=machine.Pin(25), # M5Stack Core/GO speaker is typically on Pin 25
                mode=machine.I2S.TX,
                bits=16,
                format=machine.I2S.MONO,
                rate=16000,
                ibuf=8192
            )
            return audio_out
        else:
            mode = getattr(machine.I2S, "MODE_MASTER", 1) | getattr(machine.I2S, "MODE_TX", 2)
            if hasattr(machine.I2S, "MODE_DAC_BUILT_IN"):
                mode |= machine.I2S.MODE_DAC_BUILT_IN
                
            cfmt = getattr(machine.I2S, "CHANNEL_FMT_RIGHT_LEFT", 1)
            dfmt = getattr(machine.I2S, "FORMAT_I2S_MSB", 1)
            
            try_args = [
                ([getattr(machine.I2S, "NUM1", 1), mode, 16000, 16, cfmt, dfmt], {}),
                ([getattr(machine.I2S, "NUM1", 1), mode, 16000, 16], {}),
                ([getattr(machine.I2S, "NUM1", 1)], {"mode": mode, "sample_rate": 16000, "bits": 16, "channel_format": cfmt, "data_format": dfmt}),
                ([getattr(machine.I2S, "NUM1", 1)], {"mode": mode, "sample_rate": 16000, "bits": 16}),
                ([getattr(machine.I2S, "NUM1", 1)], {"mode": mode, "bck": 12, "ws": 0, "sd": 25, "sample_rate": 16000, "bits": 16}),
                ([], {"mode": mode, "sample_rate": 16000, "bits": 16}),
                ([getattr(machine.I2S, "NUM1", 1)], {"mode": mode}),
                ([], {"mode": mode}),
            ]
            
            audio_out = None
            last_e = None
            for args, kwargs in try_args:
                try:
                    audio_out = machine.I2S(*args, **kwargs)
                    break
                except Exception as e:
                    last_e = e
            if audio_out is None:
                raise Exception("Spk fallback failed: " + str(last_e))
            return audio_out
    except Exception as e:
        print("Spk I2S Error:", repr(e))
        lcd.print("Spk Err: " + str(e)[:20], 0, 60, 0xFF0000)
        return None

def deinit_i2s(i2s_obj):
    if i2s_obj:
        try:
            if hasattr(i2s_obj, 'deinit'):
                i2s_obj.deinit()
        except Exception as e:
            print("I2S Deinit Error:", e)

ws = None

def connect_ws():
    global ws
    try:
        ws = websocket.WebSocket()
        ws.connect(WS_URL)
        return True
    except Exception as e:
        draw_status("WS Connection Error", 0xFF0000)
        return False

draw_status("Hold Button A to Talk", 0xFFFFFF)

buf = bytearray(1024)

# Noise monitoring variables
l_db_s = ""
s_db = 30.0

# Location settings - change this depending on where the M5GO is placed
CURRENT_ROOM_ID = "mckeldin"
CURRENT_LAT = 38.986021
CURRENT_LNG = -76.944949

last_db_post_time = 0

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
        audio_in = init_mic()
        while btnA.isPressed():
            try:
                if audio_in:
                    num_read = audio_in.readinto(buf)
                    if num_read and num_read > 0 and ws:
                        ws.send(buf[:num_read])
            except Exception as e:
                pass
        deinit_i2s(audio_in)
        audio_in = None
                
        # Button released
        draw_status("Thinking...", 0xFFFF00)
        try:
            if ws:
                ws.send(json.dumps({"event": "stop_listening"}))
                
                # Wait for response audio
                draw_status("Speaking...", 0x00FF00)
                audio_out = init_spk()
                while True:
                    resp = ws.recv()
                    if resp and isinstance(resp, bytes):
                        if len(resp) == 0:
                            break  # End of audio transmission
                        
                        # Briefly pause face animation updates while speaker is playing
                        # to prevent dropping packets or stuttering
                        if audio_out:
                            audio_out.write(resp)
                    else:
                        break # Empty or non-bytes response means end
                deinit_i2s(audio_out)
                audio_out = None
        except Exception as e:
            draw_status("Error during playback", 0xFF0000)
            ws = None # force reconnect next time
            
        draw_status("Hold Button A to Talk", 0xFFFFFF)
        
    # ---------------------------------------------
    # NOISE MONITORING LOOP
    # ---------------------------------------------
    
    r_db = get_db()
    s_db = (s_db * 0.8) + (r_db * 0.2)
    db = int(s_db)
    
    if db < 40:
        i_c = 0x89b4fa
    elif db < 55:
        i_c = 0x94e2d5
    elif db < 65:
        i_c = 0xf9e2af
    elif db < 80:
        i_c = 0xfab387
    else:
        i_c = 0xf38ba8
        
    lcd.fillRect(0, 0, 320, 4, i_c)
    db_s = "Noise: %d dB" % db
    if db_s != l_db_s:
        lcd.fillRect(0, 4, 150, 15, 0x222222)
        lcd.print(db_s, 5, 4, i_c)
        l_db_s = db_s
    
    # ---------------------------------------------
    # POST DB DATA PERIODICALLY
    # ---------------------------------------------
    try:
        now_ms = time.ticks_ms()
        if time.ticks_diff(now_ms, last_db_post_time) > 15000: # Every 15 seconds
            last_db_post_time = now_ms
            try:
                payload = {
                    "room_id": CURRENT_ROOM_ID,
                    "location": {
                        "type": "Point",
                        "coordinates": [CURRENT_LNG, CURRENT_LAT]
                    },
                    "db": float(db)
                }
                # Convert ws url from ws://ip:port/ws/voice to http://ip:port/api/study-rooms
                http_url = WS_URL.replace("ws://", "http://").replace("/ws/voice", "/api/study-rooms")
                import urequests
                res = urequests.post(http_url, json=payload)
                res.close()
            except Exception as e:
                print("Failed to post db data:", e)
    except Exception as main_e:
        pass
        
    time.sleep(0.02)
