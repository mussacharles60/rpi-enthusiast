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
fade_out_triggered = False

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
    global is_playing, fade_thread, fade_out_triggered
    print("[INFO] Starting audio with fade-in")
    fade_thread = Thread(target=fade_light, args=(0, 100, 3))
    fade_thread.start()
    fade_thread.join()

    player.play()
    is_playing = True
    fade_out_triggered = False

def stop_audio_with_fade():
    global is_playing
    print("[INFO] Stopping audio with fade-out")
    Thread(target=fade_light, args=(100, 0, 3)).start()
    player.stop()
    is_playing = False

def button_pressed():
    global is_playing
    print("[BTN] Button pressed.")
    if not is_playing:
        start_audio_with_light()
    else:
        stop_audio_with_fade()

# === Main Loop ===
print("[READY] Press button to toggle audio + light.")
try:
    while True:
        current_state = GPIO.input(BUTTON_PIN)

        # Detect falling edge (button press)
        if last_state == GPIO.HIGH and current_state == GPIO.LOW:
            button_pressed()

        last_state = current_state

        # Auto fade-out if audio is near end
        if is_playing and player.get_state() == vlc.State.Playing:
            pos = player.get_time() / 1000.0  # ms → sec
            if not fade_out_triggered and pos >= audio_duration - 3:
                print("[AUTO] Audio ending soon — fading light.")
                Thread(target=fade_light, args=(100, 0, 3)).start()
                player.stop()
                fade_out_triggered = True
                is_playing = False

        time.sleep(debounce_delay)

except KeyboardInterrupt:
    print("\n[EXIT] Ctrl+C pressed.")
finally:
    pwm.stop()
    GPIO.cleanup()
    print("[CLEANUP] GPIO released.")
