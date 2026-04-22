from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

# --- SETUP FOR PI 4 ---
# Using the pigpio factory we installed for clean hardware PWM
factory = PiGPIOFactory()

# Initialize the Servos (Motor Controllers)
motor1 = Servo(18, min_pulse_width=0.0011, max_pulse_width=0.0019, pin_factory=factory)
motor2 = Servo(23, min_pulse_width=0.0011, max_pulse_width=0.0019, pin_factory=factory)

print("--------------------------------")
print("ARMING MOTORS (Wait 5 sec)...")
# Send 0.0 (Neutral 1500µs) to both to arm the controller
motor1.value = 0.0
motor2.value = 0.0
sleep(5) 

print("READY! Running aligned test...")

try:
    # --- FORWARD ---
    print(">>> Forward (30% Speed)")
    motor1.value = 1   
    motor2.value = -1 
    sleep(40)

    print(">>> Stop")
    motor1.value = 0.0
    motor2.value = 0.0
    sleep(1)

    print(">>> Stop")
    motor1.value = 0.0
    motor2.value = 0.0

except KeyboardInterrupt:
    print("\nStopped by user")

finally:
    # Safely detach the pins
    motor1.value = None
    motor2.value = None
    motor1.close()
    motor2.close()
    print("Done.")
