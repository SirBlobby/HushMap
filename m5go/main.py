import network
import time
import machine
import json
import math
import usocket
import ubinascii
import os
import gc
from m5stack import *
from m5ui import *
from uiflow import *

C = { '0': 0x222222, 'Y': 0xFFFF00, 'R': 0xFF0000, 'W': 0xFFFFFF, 'B': 0x000000, 'D': 0x555555 }
f_s_o = "00000000000000000000000000000000000WWW0000WWW00000WWBW0000WWBW0000WWBW0000WWBW00000WWW0000WWW000000000000000000000000000000000000000000000000000YY000000000000YY0YY0000000000YY000YY00000000YY00000YYYYYYYYYY00000000YYYYYY0000000000000000000000000000000000000"
f_s_c = "0000000000000000000000000000000000000000000000000000000000000000000000000000000000WWWW0000WWWW00000000000000000000000000000000000000000000000000YY000000000000YY0YY0000000000YY000YY00000000YY00000YYYYYYYYYY00000000YYYYYY0000000000000000000000000000000000000"
f_t_1 = "0000000000000000000000000000000000000000000000000000000000000000000WWW0000WWW00000WWWW0000WWWW00000WWW0000WWW00000000000000000000000000000000000000000000000000000000000000000000000000000000000000YYYYYYYYYY000000000000000000000000000000000000000000000000000"
f_t_2 = "0000000000000000000000000000000000DD00000000DD00000DD000000DD0000000000000000000000WWW0000WWW00000WWBW0000WWBW00000WWW0000WWW0000000000000000000000000000000000000000000000000000000RRRRRRRR0000000RR000000RR000000000000000000000000000000000000000000000000000"
f_listen = "0000000000000000000000000000000000WWWW0000WWWW0000WBBW0000WBBW0000WBBW0000WBBW0000WWWW0000WWWW0000000000000000000000000000000000000000000000000000000YYYYYY000000000YY0000YY00000000YY0000YY000000000YYYYYY00000000000000000000000000000000000000000000000000000"
f_speak = "00000000000000000000000000000000000WWW0000WWW00000WWBW0000WWBW0000WWBW0000WWBW00000WWW0000WWW0000000000000000000000000000000000000000000000000000000YYYYYYYY0000000YY000000YY000000YY000000YY0000000YYYYYYYY0000000000000000000000000000000000000000000000000000"
f_angry = "00000000000000000DDDD000000DDDD000DDDD0000DDDD00000DDDD00DDDD000000WWW0000WWW00000WWBB0000BBWW00000WWW0000WWW000000000000000000000000000000000000000000000000000000000RRRR0000000000RRRRRRRR000000RRRR0000RRRR000RRR00000000RRR000000000000000000000000000000000"

def d_s(lcd, f, s_x, s_y, p_s):
    for r in range(16):
        c = 0
        i = r * 16
        while c < 16:
            s_c = c
            v = f[i + c]
            while c < 16 and f[i + c] == v:
                c += 1
            w = c - s_c
            lcd.fillRect(s_x + s_c * p_s, s_y + r * p_s, w * p_s, p_s, C[v])

setScreenColor(0x222222)





WIFI_SSID = "Blobby"
WIFI_PASS = "73556088"
WS_URL = "ws://192.168.137.1:8000/ws/voice"


CURRENT_ROOM_ID = "mckeldin"
CURRENT_LAT = 38.986021
CURRENT_LNG = -76.944949


TARGET_SAMPLE_RATE = 8000
AUDIO_CHUNK_SIZE = 2048





class WSClient:
    def __init__(self, sock):
        self._sock = sock

    def send(self, data):
        if isinstance(data, str):
            data = data.encode()
            opcode = 0x1
        else:
            opcode = 0x2
        length = len(data)
        mask_key = os.urandom(4)
        header = bytearray()
        header.append(0x80 | opcode)
        if length < 126:
            header.append(0x80 | length)
        elif length < 65536:
            header.append(0x80 | 126)
            header.append((length >> 8) & 0xFF)
            header.append(length & 0xFF)
        else:
            header.append(0x80 | 127)
            for i in range(7, -1, -1):
                header.append((length >> (8 * i)) & 0xFF)
        header.extend(mask_key)
        masked = bytearray(data)
        for i in range(length):
            masked[i] ^= mask_key[i % 4]
        self._sock.send(header + masked)

    def recv(self):
        hdr = self._recv_exact(2)
        if not hdr or len(hdr) < 2:
            return None
        opcode = hdr[0] & 0x0F
        is_masked = (hdr[1] & 0x80) != 0
        length = hdr[1] & 0x7F
        if length == 126:
            ext = self._recv_exact(2)
            length = (ext[0] << 8) | ext[1]
        elif length == 127:
            ext = self._recv_exact(8)
            length = 0
            for b in ext:
                length = (length << 8) | b
        mask_key = self._recv_exact(4) if is_masked else None
        payload = self._recv_exact(length) if length > 0 else b""
        if is_masked and mask_key and payload:
            payload = bytearray(payload)
            for i in range(len(payload)):
                payload[i] ^= mask_key[i % 4]
            payload = bytes(payload)
        if opcode == 0x8:
            return None
        if opcode == 0x9:
            self._send_pong(payload)
            return self.recv()
        if opcode == 0x1:
            return payload.decode() if payload else ""
        return payload

    def _send_pong(self, data):
        mask_key = os.urandom(4)
        length = len(data) if data else 0
        header = bytearray([0x8A, 0x80 | length])
        header.extend(mask_key)
        if data:
            masked = bytearray(data)
            for i in range(length):
                masked[i] ^= mask_key[i % 4]
            self._sock.send(header + masked)
        else:
            self._sock.send(header)

    def _recv_exact(self, n):
        buf = bytearray(n)
        pos = 0
        while pos < n:
            chunk = self._sock.recv(n - pos)
            if not chunk:
                return None
            buf[pos:pos + len(chunk)] = chunk
            pos += len(chunk)
        return bytes(buf)

    def close(self):
        try:
            self._sock.send(bytearray([0x88, 0x80, 0, 0, 0, 0]))
        except:
            pass
        try:
            self._sock.close()
        except:
            pass

def ws_connect(url):
    if url.startswith("ws://"):
        rest = url[5:]
    else:
        raise ValueError("Only ws:// supported")
    if "/" in rest:
        host_port = rest.split("/", 1)[0]
        path = "/" + rest.split("/", 1)[1]
    else:
        host_port = rest
        path = "/"
    if ":" in host_port:
        host = host_port.split(":")[0]
        port = int(host_port.split(":")[1])
    else:
        host = host_port
        port = 80

    addr = usocket.getaddrinfo(host, port)[0][-1]
    sock = usocket.socket()
    sock.connect(addr)
    sock.settimeout(15)

    key = ubinascii.b2a_base64(os.urandom(16)).strip().decode()
    req = (
        "GET %s HTTP/1.1\r\n"
        "Host: %s\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        "Sec-WebSocket-Key: %s\r\n"
        "Sec-WebSocket-Version: 13\r\n"
        "\r\n"
    ) % (path, host_port, key)

    sock.send(req.encode())
    resp = b""
    while b"\r\n\r\n" not in resp:
        b = sock.recv(1)
        if not b:
            sock.close()
            raise Exception("Closed during handshake")
        resp += b

    status_line = resp.split(b"\r\n")[0]
    if b"101" not in status_line:
        sock.close()
        raise Exception("Upgrade failed: " + status_line.decode())

    return WSClient(sock)





_cur_face = None
def set_face(face):
    global _cur_face
    if face and face != _cur_face:
        d_s(lcd, face, 80, 25, 10)
        _cur_face = face

def draw_status(status, color, face=None):
    lcd.fillRect(0, 220, 320, 20, 0x222222)
    lcd.print(status, int((320 - len(status) * 8) / 2), 220, color)
    if face:
        set_face(face)

def connect_wifi():
    lcd.clear()
    lcd.print("Connecting to WiFi...", 0, 0, 0xFFFFFF)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASS)

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
    return wlan.isconnected()





def get_adc():
    try:
        a = machine.ADC(34)
        a.atten(machine.ADC.ATTN_11DB)
        return a
    except:
        try:
            a = machine.ADC(machine.Pin(34))
            a.atten(machine.ADC.ATTN_11DB)
            return a
        except:
            return None

def get_db(adc_obj):
    if not adc_obj: return 30
    sum_v = 0
    sum_sq = 0
    count = 0
    end_t = time.ticks_ms() + 40
    while time.ticks_ms() < end_t:
        try:
            v = adc_obj.read()
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


    return 20 * math.log10(amp) + 25

def init_manual_spk():
    try:


        if hasattr(machine.I2S, "MODE_DAC_BUILT_IN"):
            mode = getattr(machine.I2S, "MODE_MASTER", 1) | getattr(machine.I2S, "MODE_TX", 2) | getattr(machine.I2S, "MODE_DAC_BUILT_IN", 0)
            cfmt = getattr(machine.I2S, "CHANNEL_FMT_RIGHT_LEFT", 1)
            dfmt = getattr(machine.I2S, "FORMAT_I2S_MSB", 1)

            i2s_id = getattr(machine.I2S, "NUM0", 0)


            try_sigs = [
                ([i2s_id], {"mode": mode, "rate": 16000, "bits": 16, "format": cfmt, "ibuf": 2048}),
                ([i2s_id, mode, 16000, 16, cfmt, dfmt], {}),
                ([i2s_id, mode, 16000, 16], {}),
                ([i2s_id], {"mode": mode, "sample_rate": 16000, "bits": 16, "channel_format": cfmt, "data_format": dfmt}),
                ([i2s_id], {"mode": mode, "sample_rate": 16000, "bits": 16}),
                ([], {"mode": mode, "sample_rate": 16000, "bits": 16}),
                ([i2s_id], {"mode": mode, "rate": 16000, "bits": 16})
            ]

            last_err = None
            for args, kwargs in try_sigs:
                try:
                    return machine.I2S(*args, **kwargs)
                except Exception as e:
                    last_err = e

            print("I2S Fallback err (exhausted):", last_err)
            return None
        else:
            print("ERR: DAC_BUILT_IN missing on this firmware")
            return None
    except Exception as e:
        print("I2S Init err:", e)
        return None

def stream_http_audio(url):
    print("Streaming I2S direct from HTTP...")
    audio_out = init_manual_spk()
    if not audio_out:
        print("Speaker init failed, cannot play audio via DAC")
        return False

    if url.startswith("http://"):
        rest = url[7:]
    else:
        raise ValueError("Only http:// supported")

    if "/" in rest:
        host_port = rest.split("/", 1)[0]
        path = "/" + rest.split("/", 1)[1]
    else:
        host_port = rest
        path = "/"

    if ":" in host_port:
        host = host_port.split(":")[0]
        port = int(host_port.split(":")[1])
    else:
        host = host_port
        port = 80

    addr = usocket.getaddrinfo(host, port)[0][-1]
    sock = usocket.socket()
    sock.connect(addr)
    sock.settimeout(30)

    req = "GET %s HTTP/1.0\r\nHost: %s\r\n\r\n" % (path, host_port)
    sock.send(req.encode())

    hdr = b""
    while b"\r\n\r\n" not in hdr:
        b = sock.recv(1)
        if not b:
            sock.close()
            return False
        hdr += b


    header_left = 44
    while header_left > 0:
        chunk = sock.recv(header_left)
        if not chunk: break
        header_left -= len(chunk)

    in_buf = bytearray(1024)
    out_buf = bytearray(2048)

    while True:
        n = 0
        while n < 1024:
            chunk = sock.recv(1024 - n)
            if not chunk: break
            in_buf[n:n+len(chunk)] = chunk
            n += len(chunk)

        if n == 0: break

        samples = n // 2
        for j in range(samples):
            idx = j * 2

            s = in_buf[idx] | (in_buf[idx + 1] << 8)
            if s >= 32768: s -= 65536


            u = (s + 32768) & 0xFFFF
            u_lo = u & 0xFF
            u_hi = u >> 8


            o_idx = j * 4
            out_buf[o_idx]     = u_lo
            out_buf[o_idx + 1] = u_hi
            out_buf[o_idx + 2] = u_lo
            out_buf[o_idx + 3] = u_hi

        try:
            audio_out.write(out_buf[:samples * 4])
        except Exception as e:
            print("Write err:", e)
            break

    sock.close()
    if hasattr(audio_out, 'deinit'): audio_out.deinit()
    return True





def run_main():
    if not connect_wifi():
        return

    adc = get_adc()
    ws = None
    l_db_s = ""
    s_db = 30.0
    last_db_post_time = time.ticks_ms()

    draw_status("Hold Button A to Talk", 0xFFFFFF, f_s_o)

    def maintain_ws():
        nonlocal ws
        if not ws:
            draw_status("Connecting...", 0xFFFF00, f_t_2)
            try:
                ws = ws_connect(WS_URL)
                draw_status("Hold Button A to Talk", 0xFFFFFF, f_s_o)
            except Exception as e:
                print("WS Err:", e)
                ws = None
        return ws is not None

    while True:
        gc.collect()

        if btnA.isPressed():
            if maintain_ws():
                draw_status("Listening...", 0x0000FF, f_listen)

                send_buf = bytearray(AUDIO_CHUNK_SIZE)
                buf_pos = 0
                total_samples = 0

                rec_start_us = time.ticks_us()


                while btnA.isPressed():
                    try:
                        raw = adc.read() if adc else 2048
                        sample = (raw - 2048) * 16

                        if sample > 32767: sample = 32767
                        elif sample < -32768: sample = -32768

                        send_buf[buf_pos] = sample & 0xFF
                        send_buf[buf_pos + 1] = (sample >> 8) & 0xFF
                        buf_pos += 2
                        total_samples += 1

                        if buf_pos >= AUDIO_CHUNK_SIZE:
                            if ws: ws.send(bytes(send_buf))
                            buf_pos = 0
                    except Exception as e:
                        print("Rec Err:", e)
                        break

                if buf_pos > 0 and ws:
                    try:
                        ws.send(bytes(send_buf[:buf_pos]))
                    except:
                        pass

                draw_status("Thinking...", 0xFFFF00, f_t_1)
                actual_rate = (total_samples * 1000000) // time.ticks_diff(time.ticks_us(), rec_start_us)
                print("Captured at", actual_rate, "Hz")

                try:
                    ws.send(json.dumps({"event": "stop_listening", "sample_rate": actual_rate}))


                    resp = ws.recv()
                    if resp and isinstance(resp, str):
                        msg = json.loads(resp)
                        if msg.get("event") == "tts_ready":

                            draw_status("Speaking...", 0x00FF00, f_speak)
                            http_base = WS_URL.replace("ws://", "http://").replace("/ws/voice", "")
                            audio_url = http_base + "/api/tts-audio"

                            try:
                                stream_http_audio(audio_url)
                            except Exception as e:
                                print("Stream Err:", e)
                                draw_status("Play Failed", 0xFF0000, f_s_c)
                                time.sleep(1)

                        elif msg.get("event") == "error":
                            draw_status("Error: " + msg.get("msg", "")[:10], 0xFF0000, f_s_c)
                            time.sleep(2)
                except Exception as e:
                    print("Comm Err:", e)
                    try: ws.close()
                    except: pass
                    ws = None

                draw_status("Hold Button A to Talk", 0xFFFFFF, f_s_o)


        r_db = get_db(adc)
        s_db = (s_db * 0.8) + (r_db * 0.2)
        db_val = int(s_db)

        i_c = 0x89b4fa if db_val < 40 else (0x94e2d5 if db_val < 55 else (0xf9e2af if db_val < 65 else (0xfab387 if db_val < 80 else 0xf38ba8)))
        lcd.fillRect(0, 0, 320, 4, i_c)
        db_s = "Noise: %d dB" % db_val
        if db_s != l_db_s:
            lcd.fillRect(0, 4, 150, 15, 0x222222)
            lcd.print(db_s, 5, 4, i_c)
            l_db_s = db_s


        try:
            now_ms = time.ticks_ms()
            if time.ticks_diff(now_ms, last_db_post_time) > 15000:
                last_db_post_time = now_ms
                payload_str = '{"room_id":"%s","location":{"type":"Point","coordinates":[%s,%s]},"db":%s}' % (CURRENT_ROOM_ID, CURRENT_LNG, CURRENT_LAT, db_val)
                http_url = WS_URL.replace("ws://", "http://").replace("/ws/voice", "/api/study-rooms")


                h_p = http_url.split("://")[1].split("/")[0]
                p_th = "/" + http_url.split("://")[1].split("/", 1)[1] if "/" in http_url.split("://")[1] else "/"
                h_b = h_p.split(":")[0]
                p_r = int(h_p.split(":")[1]) if ":" in h_p else 80
                addr = usocket.getaddrinfo(h_b, p_r)[0][-1]
                s = usocket.socket()
                s.settimeout(5)
                s.connect(addr)
                req = "POST %s HTTP/1.0\r\nHost: %s\r\nContent-Type: application/json\r\nContent-Length: %d\r\n\r\n%s" % (p_th, h_p, len(payload_str), payload_str)
                s.send(req.encode())
                s.close()
                del s, req, payload_str
        except:
            pass


        if db_val > 67:
            set_face(f_angry)
        else:
            t = time.ticks_ms() % 5000
            if t < 200:
                set_face(f_s_c)
            else:
                set_face(f_s_o)

        time.sleep(0.02)

if __name__ == "__main__":
    try:
        run_main()
    except Exception as e:
        print("Fatal error:", e)
        lcd.print("Error: " + str(e), 0, 100, 0xFF0000)
