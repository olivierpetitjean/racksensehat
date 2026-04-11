import time 
from datetime import datetime
from threading import  Thread
import paho.mqtt.client as mqtt
import json  
from datetime import datetime 
import time 
import json   
import pigpio
import RPi.GPIO as GPIO
from utils import read_settings

#global const
DELAY = 15 #delay between two save
SCREEN_DELAY = 30 #screen standby delay 
FAN_MODES = {True:"Auto", False:"Manual"}
SOUND_MODE = {True:"On", False:"Off"}
PULSE = 2 #Fan pusle

#global vars
maxTimeDelay = 10
forceFp1 = 15
forceFp2 = 15
auto = True
fp1 = 0
fp2 = 0
fpm1 = 0
fpm2 = 0
s1temp = 0
s2temp = 0
rpm1 = 0
rpm2 = 0
sys_cur = 0
sys_sens = 0
sys_fan = False
sound = True
globalSettings = None

fan1_timer = None
fan2_timer = None
 
#Get shared settings
def ReadSettings():
    return read_settings()

#get fan RPM #1
def GetFan1Rpm(): 
   global fan1_timer

   if(fan1_callback is None):
       return 0

   fan1elapsed = time.time() - fan1_timer
   fan1_timer = time.time()

   fan1falls = fan1_callback.tally() 
   fan1_callback.reset_tally()
    
   rpm1 = ((fan1falls / PULSE) / fan1elapsed) * 60
  
   return rpm1
 
def GetFan2Rpm():
   global fan2_timer

   if(fan2_callback is None):
       return 0

   fan2elapsed = time.time() - fan2_timer
   fan2_timer = time.time()

   fan2falls = fan2_callback.tally()
   fan2_callback.reset_tally()
    
   rpm2 = ((fan2falls / PULSE) / fan2elapsed) * 60
  
   return rpm2

settings = ReadSettings()
 
frequency = int(settings['fanFrequency'])
resolution = int(settings['fanPWMResolution'])
fan1 = int(settings['fan1Pin'])
fan2 = int(settings['fan2Pin'])
fan1Sensor = int(settings['fan1Sensor'])
fan2Sensor = int(settings['fan2Sensor'])
outputEnabled = settings['outputEnabled']
red_led = settings['redLed']
green_led = settings['greenLed']
initialDutyCycle = 50

#pigpio
gpio = pigpio.pi()
 
#OE
#gpio.set_mode(outputEnabled, pigpio.OUTPUT)
#gpio.write(outputEnabled, 1)

##fan outputs (hardware PWM)
#gpio.set_mode(fan1, pigpio.OUTPUT)
#gpio.set_mode(fan2, pigpio.OUTPUT)

#gpio.hardware_PWM(fan1, frequency, resolution)
#gpio.hardware_PWM(fan2, frequency, resolution)
 
#gpio.set_PWM_dutycycle(fan1, initialDutyCycle)
#gpio.set_PWM_dutycycle(fan2, initialDutyCycle)

##fan inputs
gpio.set_mode(fan1Sensor, pigpio.INPUT)
gpio.set_mode(fan2Sensor, pigpio.INPUT)
 
gpio.set_pull_up_down(fan1Sensor, pigpio.PUD_UP)
gpio.set_pull_up_down(fan2Sensor, pigpio.PUD_UP)

fan1_timer = time.time()
fan1_callback = gpio.callback(fan1Sensor, pigpio.EITHER_EDGE)
fan2_timer = time.time()
fan2_callback = gpio.callback(fan2Sensor, pigpio.EITHER_EDGE)

gpio.set_mode(red_led, pigpio.OUTPUT)
gpio.write(red_led, True) 
gpio.set_mode(green_led, pigpio.OUTPUT)
gpio.write(green_led, True)

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(red_led, GPIO.OUT)
#GPIO.setup(green_led, GPIO.OUT)
#GPIO.output(red_led, GPIO.HIGH)
#GPIO.output(green_led, GPIO.HIGH)

while True:
    
    rpm1 = GetFan1Rpm()
    rpm2 = GetFan2Rpm()

    print("RPM1: " + str(rpm1))
    print("RPM2: " + str(rpm2))

    time.sleep(10)
