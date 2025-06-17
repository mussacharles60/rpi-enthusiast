import time
import math
import vlc
import RPi.GPIO as GPIO
from threading import Thread
from mutagen.mp3 import MP3

# === GPIO Setup ===
PWM_PIN = 13
BUTTON_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(PWM_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

pwm = GPIO.PWM(PWM_PIN, 1000)
pwm.start(0)

# === VLC and Playback State ===
AUDIO_FILE = "audio.mp3"
instance = vlc.Instance('--aout=alsa', '--file-caching=1000')
player = instance.media_player_new()
media = instance.media_new(AUDIO_FILE)
player.set_media(media)
audio_duration = MP3(AUDIO_FILE).info.length

# === Playback and Light State ===
is_playing = False
fade_thread = None

def fade_light(start, end, duration):
    steps = 100
    delay = duration / steps
    for i in range(steps + 1):
        t = i / steps
        eased = 0.5 * (1 - math.cos(t * math.pi))
        value = start + (end - start) * eased
        pwm.ChangeDutyCycle(value)
        time.sleep(delay)

def start_audio_with_light():
    global is_playing, fade_thread
    print("[INFO] Starting audio with fade-in")
    fade_thread = Thread(target=fade_light, args=(0, 100, 3))
    fade_thread.start()
    fade_thread.join()

    player.play()
    is_playing = True

def stop_audio_with_fade():
    global is_playing
    print("[INFO] Stopping audio with fade-out")
    Thread(target=fade_light, args=(100, 0, 3)).start()
    player.stop()
    is_playing = False

def button_pressed(channel):
    global is_playing
    if not is_playing:
        start_audio_with_light()
    else:
        stop_audio_with_fade()

# === Attach button event ===
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_pressed, bouncetime=500)

# === Keep running ===
print("[READY] Press button to toggle audio + light.")
try:
    while True:
        time.sleep(0.1)
finally:
    pwm.stop()
    GPIO.cleanup()
    print("[CLEANUP] GPIO released.")
