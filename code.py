import sys
import gc  # for checking memory
import analogio
from digitalio import DigitalInOut, Direction, Pull
import time
import board
import busio
# import adafruit_sdcard # sd card
import solar_ssd1306  # oled
import solar_ina219  # current sensor
import solar_pcf8523  # rtc
# print("\n{} imported {} memory used".format("solar_pcf8523", m - gc.mem_free()))
print(sys.modules.keys())
m = gc.mem_free()
print("\n{} final memory".format(m))

i2c_bus = busio.I2C(board.SCL, board.SDA)
oled = solar_ssd1306.SSD1306_I2C(128, 32, i2c_bus)
rtc = solar_pcf8523.PCF8523(i2c_bus)
sensorIV_1 = solar_ina219.INA219(i2c_bus)
lipo_volt_pin = analogio.AnalogIn(board.D9)
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


def printToOLED(text, line):
    oled.fill(0)
    oled.txt_array[line] = text
    for l in range(0,len(oled.txt_array)):
        posy = l * 12  # allow 12 rows per line of text
        oled.text(oled.txt_array[l],0,posy)
    oled.show()

while True:
    thisTime = rtc.datetime
    
    if thisTime.tm_sec > lastRead.tm_sec:
        lastRead = thisTime  # reset the timer
        busVoltage = sensorIV_1.bus_voltage  # V
        shuntVoltage = sensorIV_1.shunt_voltage  # V
        voltage = busVoltage + shuntVoltage  # V
        current = sensorIV_1.current  # mA
        # power = current * loadVoltage  #mW
        arrayV.append(voltage)
        arrayI.append(current)
        print(len(arrayV))
        printToOLED("{:02}:{:02}:{:02}".format(thisTime.tm_hour, thisTime.tm_min, thisTime.tm_sec), 0)
    elif thisTime.tm_sec < lastRead.tm_sec:
        lastRead = thisTime  # reset the timer if lastRead is 59 secs


    if thisTime.tm_min > lastStore.tm_min:  # every minute take the mean and store the reading
        lastStore = thisTime
        
        V = sum(arrayV)/len(arrayV)
        I = sum(arrayI)/len(arrayI)
        P = V * I
    
        lipo_voltage = (lipo_volt_pin.value * 3.3) / 65536 * 2

        printToOLED("{:02}:{:02}:{:02}".format(thisTime.tm_hour, thisTime.tm_min, thisTime.tm_sec), 0)
        printToOLED("{:.1f}V {:.1f}A {:.1f}W".format(V, I, P),1)
        printToOLED("bat {:.1f}V m{}b".format(lipo_voltage, gc.mem_free()),2)

        # empty the arrays
        print(len(arrayV))
        arrayV = []
        arrayI = []
        print(len(arrayV))
    if not button_c.value: # this button pulled up so false when pressed
        now = time.time()
        if now > button_c_time:  # 1 second to avoid bounce
            led.value = not led.value
            button_c_time = now