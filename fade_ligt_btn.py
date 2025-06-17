import time
import math
import vlc
import RPi.GPIO as GPIO
from threading import Thread
from mutagen.mp3 import MP3

# === GPIO Setup ===
PWM_PIN = 13
BUTTON_PIN = 17

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PWM_PIN, GPIO.OUT)
# GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

last_state = GPIO.input(BUTTON_PIN)
debounce_delay = 0.05  # 50ms

pwm = GPIO.PWM(PWM_PIN, 1000)
pwm.start(0)

# === VLC and Playback State ===
AUDIO_FILE = "/home/projects/light-control/audio.mp3"
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

def button_pressed():
    print("Button pressed!")
    global is_playing
    if not is_playing:
        start_audio_with_light()
    else:
        stop_audio_with_fade()

# === Attach button event ===
# GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_pressed, bouncetime=300)

# === Keep running ===
print("[READY] Press button to toggle audio + light.")
try:
    while True:
        current_state = GPIO.input(BUTTON_PIN)
        
        # Detect falling edge manually (HIGH → LOW)
        if last_state == GPIO.HIGH and current_state == GPIO.LOW:
            button_pressed()

        last_state = current_state
        time.sleep(debounce_delay)
        
except KeyboardInterrupt:
    print("Exiting...")
finally:
    pwm.stop()
    GPIO.remove_event_detect(BUTTON_PIN)
    GPIO.cleanup()
    print("[CLEANUP] GPIO released.")
