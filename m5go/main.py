from m5stack import *
from m5ui import *
from uiflow import *
import time
import machine
import math

setScreenColor(0x222222)

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
    
    # +25 scales the RMS amplitude into a natural dB range
    db = 20 * math.log10(amp) + 25
    return db

C = {
    '0': 0x222222,
    'Y': 0xFFFF00,
    'R': 0xFF0000,
    'W': 0xFFFFFF,
    'B': 0x000000,
    'P': 0xFF8888,
    'D': 0x555555
}

f_s_o = [
    "0000000000000000",
    "0000000000000000",
    "000WWW0000WWW000",
    "00WWBW0000WWBW00",
    "00WWBW0000WWBW00",
    "000WWW0000WWW000",
    "0000000000000000",
    "0000000000000000",
    "0000000000000000",
    "YY000000000000YY",
    "0YY0000000000YY0",
    "00YY00000000YY00",
    "000YYYYYYYYYY000",
    "00000YYYYYY00000",
    "0000000000000000",
    "0000000000000000"
]

f_s_h = [
    "0000000000000000",
    "0000000000000000",
    "0000000000000000",
    "000WWW0000WWW000",
    "00WWBW0000WWBW00",
    "000WWW0000WWW000",
    "0000000000000000",
    "0000000000000000",
    "0000000000000000",
    "YY000000000000YY",
    "0YY0000000000YY0",
    "00YY00000000YY00",
    "000YYYYYYYYYY000",
    "00000YYYYYY00000",
    "0000000000000000",
    "0000000000000000"
]

f_s_c = [
    "0000000000000000",
    "0000000000000000",
    "0000000000000000",
    "0000000000000000",
    "0000000000000000",
    "00WWWW0000WWWW00",
    "0000000000000000",
    "0000000000000000",
    "0000000000000000",
    "YY000000000000YY",
    "0YY0000000000YY0",
    "00YY00000000YY00",
    "000YYYYYYYYYY000",
    "00000YYYYYY00000",
    "0000000000000000",
    "0000000000000000"
]

f_a_o = [
    "0000000000000000",
    "0DDDD000000DDDD0",
    "00DDDD0000DDDD00",
    "000DDDD00DDDD000",
    "000WWW0000WWW000",
    "00WWBB0000BBWW00",
    "000WWW0000WWW000",
    "0000000000000000",
    "0000000000000000",
    "0000000000000000",
    "000000RRRR000000",
    "0000RRRRRRRR0000",
    "00RRRR0000RRRR00",
    "0RRR00000000RRR0",
    "0000000000000000",
    "0000000000000000"
]

f_a_h = [
    "0000000000000000",
    "0DDDD000000DDDD0",
    "00DDDD0000DDDD00",
    "000DDDD00DDDD000",
    "0000000000000000",
    "000WWW0000WWW000",
    "00WWBB0000BBWW00",
    "0000000000000000",
    "0000000000000000",
    "0000000000000000",
    "000000RRRR000000",
    "0000RRRRRRRR0000",
    "00RRRR0000RRRR00",
    "0RRR00000000RRR0",
    "0000000000000000",
    "0000000000000000"
]

f_a_c = [
    "0000000000000000",
    "0DDDD000000DDDD0",
    "00DDDD0000DDDD00",
    "000DDDD00DDDD000",
    "0000000000000000",
    "0000000000000000",
    "000WW000000WW000",
    "0000000000000000",
    "0000000000000000",
    "0000000000000000",
    "000000RRRR000000",
    "0000RRRRRRRR0000",
    "00RRRR0000RRRR00",
    "0RRR00000000RRR0",
    "0000000000000000",
    "0000000000000000"
]

f_t_1 = [
    "0000000000000000",
    "0000000000000000",
    "0000000000000000",
    "0000000000000000",
    "000WWW0000WWW000",
    "00WWWW0000WWWW00",
    "000WWW0000WWW000",
    "0000000000000000",
    "0000000000000000",
    "0000000000000000",
    "0000000000000000",
    "0000000000000000",
    "000YYYYYYYYYY000",
    "0000000000000000",
    "0000000000000000",
    "0000000000000000"
]

f_t_2 = [
    "0000000000000000",
    "0000000000000000",
    "00DD00000000DD00",
    "000DD000000DD000",
    "0000000000000000",
    "000WWW0000WWW000",
    "00WWBW0000WWBW00",
    "000WWW0000WWW000",
    "0000000000000000",
    "0000000000000000",
    "0000000000000000",
    "0000RRRRRRRR0000",
    "000RR000000RR000",
    "0000000000000000",
    "0000000000000000",
    "0000000000000000"
]

def d_s(f, s_x, s_y, p_s):
    for r in range(16):
        c = 0
        while c < 16:
            s_c = c
            v = f[r][c]
            while c < 16 and f[r][c] == v:
                c += 1
            w = c - s_c
            
            x_p = s_x + (s_c * p_s)
            y_p = s_y + (r * p_s)
            
            lcd.fillRect(x_p, y_p, w * p_s, p_s, C[v])

s = 14  
x = 48     
y = 16      

a_f = 's'
b_s = 'o'
t_s = 0
c_t = 0
l_f = None
b_p = False
al_t = 0
l_db_s = ""
s_db = 30.0
l_is_angry = False

while True:
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
        lcd.fillRect(0, 4, 120, 12, 0x222222)
        lcd.print(db_s, 5, 4, i_c)
        l_db_s = db_s

    i_a = btnA.isPressed() or btnB.isPressed() or btnC.isPressed() or db >= 65
    t_f = 'a' if i_a else 's'
    
    b_n = btnB.isPressed()
    is_angry = (t_f == 'a')
    
    if b_n or is_angry:
        al_t += 1
        if al_t % 4 < 2:
            try:
                if b_n: speaker.tone(1200, 50)
                rgb.setColorAll(0xFF0000)
            except:
                pass
        else:
            try:
                if b_n: speaker.tone(800, 50)
                rgb.setColorAll(0x0000FF)
            except:
                pass
    elif b_p or l_is_angry:
        try:
            rgb.setColorAll(0x000000)
        except:
            pass
        al_t = 0
    b_p = b_n
    l_is_angry = is_angry
    
    c_t += 1
    
    if a_f != t_f and t_s == 0:
        t_s = 1
        c_t = 0
        
    if t_s > 0:
        if c_t >= 2:
            t_s += 1
            c_t = 0
            if t_s == 3:
                a_f = t_f
                t_s = 0
                b_s = 'o'
    else:
        if b_s == 'o' and c_t >= 50: 
            b_s = 'h'
            c_t = 0
        elif b_s == 'h' and c_t >= 1: 
            b_s = 'c'
            c_t = 0
        elif b_s == 'c' and c_t >= 2: 
            b_s = 'h_o'
            c_t = 0
        elif b_s == 'h_o' and c_t >= 1: 
            b_s = 'o'
            c_t = 0
            
    c_d = (a_f, b_s, t_s)
    if c_d != l_f:
        if t_s == 1:
            f = f_t_1 if a_f == 's' else f_t_2
        elif t_s == 2:
            f = f_t_2 if a_f == 's' else f_t_1
        else:
            if a_f == 'a':
                if b_s == 'o': f = f_a_o
                elif b_s in ['h', 'h_o']: f = f_a_h
                else: f = f_a_c
            else:
                if b_s == 'o': f = f_s_o
                elif b_s in ['h', 'h_o']: f = f_s_h
                else: f = f_s_c
                
        d_s(f, x, y, s)
        l_f = c_d
        
    time.sleep(0.02)