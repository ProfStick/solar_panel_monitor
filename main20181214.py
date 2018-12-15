import sys
import gc  # for checking memory
m = gc.mem_free()
print("\n{} memory".format(m))
import analogio
from digitalio import DigitalInOut, Direction, Pull
import time
import board
import busio
# from adafruit_featherwing import shared
m = gc.mem_free()
print("\n{} memory".format(m))

import adafruit_ina219  # current/voltage sensor
# from adafruit_featherwing import ina219_featherwing
m = gc.mem_free()
print("\n{} imported {} memory".format('adafruit_ina219', m))

import adafruit_sdcard # sd card
m = gc.mem_free()
print("\n{} imported {} memory".format('adafruit_sdcard', m))

import adafruit_pcf8523  # rtc
m = gc.mem_free()
print("\n{} imported {} memory".format('adafruit_pcf8523', m))

import adafruit_ssd1306  # oled
m = gc.mem_free()
print("\n{} imported {} memory".format('adafruit_ssd1306', m))

class oled(adafruit_ssd1306.SSD1306_I2C):
    def __init__ (self, width, height, i2c):
        super().__init__(width, height, i2c)
        self.txt_array = ["","",""]
        
    def clear(self):
        self.txt_array = ["","",""]
        self.fill(0)
        self.show()
        
    def refresh(self):
        self.fill(0)
        for i in range(0, len(self.txt_array)):
            posy = i * 12  # 12 rows per line
            self.text(self.txt_array[i], 0, posy)
        self.show()
        
    def displayText(self, text, line):
        self.txt_array[line] = text
        self.refresh()
        

i2c_bus = busio.I2C(board.SCL, board.SDA)
rtc = adafruit_pcf8523.PCF8523(i2c_bus)
display = oled(128, 32, i2c_bus)
sensorIV_1 = adafruit_ina219.INA219(i2c_bus, 0x40)
sensorIV_2 = adafruit_ina219.INA219(i2c_bus, 0x41)
sensorIV_1 = adafruit_ina219.INA219(i2c_bus, 0x44)

led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT
button_c = DigitalInOut(board.D5)
button_c.direction = Direction.INPUT
button_c.pull = Pull.UP
button_c_time = time.time()

lastRead = rtc.datetime  # last readings were taken
lastStore = rtc.datetime  # last readings were taken
arrayV = []
arrayI = []

while True:
    display.displayText("{} final mem".format(m), 1)
    time.sleep(1)
    display.clear()
    time.sleep(1)