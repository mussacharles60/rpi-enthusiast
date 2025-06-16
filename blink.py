import RPi.GPIO as GPIO
import time

# === Use GPIO 4 (already configured as OUTPUT)
LED_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

# === Blink the LED ===
try:
    print("Blinking LED on GPIO", LED_PIN)
    while True:
        GPIO.output(LED_PIN, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(LED_PIN, GPIO.LOW)
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    GPIO.cleanup()
