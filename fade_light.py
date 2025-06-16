import vlc
import RPi.GPIO as GPIO
import time
from threading import Thread
from mutagen.mp3 import MP3
import math

# === GPIO Setup ===
PWM_PIN = 18
FREQ = 1000

GPIO.setmode(GPIO.BCM)
GPIO.setup(PWM_PIN, GPIO.OUT)
pwm = GPIO.PWM(PWM_PIN, FREQ)
pwm.start(0)

def fade_light(start, end, duration):
    # steps = 50
    # delay = duration / steps
    # for i in range(steps + 1):
    #     val = start + (end - start) * i / steps
    #     pwm.ChangeDutyCycle(val)
    #     time.sleep(delay)
    
    # steps = 200  # smoother
    # delay = duration / steps
    # for i in range(steps + 1):
    #     # Cosine easing (0 to π) => smooth start & end
    #     t = i / steps
    #     eased = 0.5 * (1 - math.cos(t * math.pi))  # goes from 0 to 1
    #     value = start + (end - start) * eased
    #     pwm.ChangeDutyCycle(value)
    #     time.sleep(delay)
    
    steps = 300  # very smooth
    delay = duration / steps

    for i in range(steps + 1):
        t = i / steps
        eased = 0.5 * (1 - math.cos(t * math.pi))  # cosine easing
        value = start + (end - start) * eased

        # Clamp to safe range (some LEDs flicker below 5%)
        safe_value = max(5, min(100, value)) if end > start else max(0, min(95, value))

        pwm.ChangeDutyCycle(safe_value)
        time.sleep(delay)


def play_audio_with_light(file_path):
    # Get duration
    duration = MP3(file_path).info.length

    # VLC player
    player = vlc.MediaPlayer(file_path)

    # Fade in
    Thread(target=fade_light, args=(0, 100, 3), daemon=True).start()

    player.play()
    time.sleep(0.5)  # Let VLC buffer

    # Wait until near end to fade out
    fade_started = False
    while player.get_state() != vlc.State.Ended:
        pos = player.get_time() / 1000.0  # ms to s
        if not fade_started and pos >= duration - 3:
            Thread(target=fade_light, args=(100, 0, 3), daemon=True).start()
            fade_started = True
        time.sleep(0.1)

    pwm.ChangeDutyCycle(0)

try:
    play_audio_with_light("audio.mp3")
finally:
    pwm.stop()
    GPIO.cleanup()
