from gpiozero import Motor
from time import sleep
import time
import RPi.GPIO as GPIO
import math

# Right Motor
in1 = 19
in2 = 26
en_a = 13

# Left Motor
in3 = 16
in4 = 20
en_b = 12

# Set up the motor objects
motor1 = Motor(forward=in1, backward=in2, enable=en_a)
motor2 = Motor(forward=in3, backward=in4, enable=en_b)

def move_forward(duration=None):
    motor1.forward(0.5)
    motor2.forward(0.5)
    if duration is not None:
        sleep(duration)
        motor1.stop()
        motor2.stop()
    # motor1.close()
    # motor2.close()
##################### MAYBE NEEDS CALIBRATION OF speed or radius ########################
async def turn(angle):
    if angle > 0:
        # Turn right
        motor1.forward(0.5)
        motor2.backward(0.5)
    else:
        # Turn left
        motor1.backward(0.5)
        motor2.forward(0.5)
        angle = abs(angle)

    # Calculate the time required to turn by the given angle
    radius = 0.5  
    speed = 0.5  
    time_for_turn = (angle * math.pi / 180.0 * radius) / speed

    sleep(time_for_turn)
    # Stop the motors
    motor1.stop()
    motor2.stop()

def stop_motors():
    motor1.stop()
    motor2.stop()
    # motor2.close()
    # motor1.close()


### Sonar Measurements ###
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 4
GPIO_ECHO = 17
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
 
def distance():
    """Sonar distance"""
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34000) / 2
 
    return distance
 
if __name__ == '__main__':
    try:
        print("Waiting for sensor to settle")
        time.sleep(4)
        while True:
            dist = distance()
            print("Measured Distance = %.1f cm" % dist)
            time.sleep(1)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()

