import sys
print(sys.modules.keys())
import gc  # for checking memory
m = gc.mem_free()
print("{} imported {} memory".format("gc", m))
print(sys.modules.keys())
import analogio

import time
print("\n{} imported {} memory used".format("time", m - gc.mem_free()))
m = gc.mem_free()
print(sys.modules.keys())
import board
# import busio

from adafruit_featherwing import shared
print("\n{} imported {} memory used".format("shared", m - gc.mem_free()))
m = gc.mem_free()
print(sys.modules.keys())

# import adafruit_sdcard # sd card
# print("\n{} imported {} memory used".format("solar_sdcard", m - gc.mem_free()))
# m = gc.mem_free()
# print(sys.modules.keys())

import solar_ssd1306  # oled
print("\n{} imported {} memory used".format("solar_ssd1306", m - gc.mem_free()))
m = gc.mem_free()
print(sys.modules.keys())

import solar_ina219  # current sensor
print("\n{} imported {} memory used".format("solar_ina219", m - gc.mem_free()))
print(sys.modules.keys())
m = gc.mem_free()

import solar_pcf8523  # rtc
print("\n{} imported {} memory used".format("solar_pcf8523", m - gc.mem_free()))
print(sys.modules.keys())
m = gc.mem_free()
print("\n{} final memory".format(m))


i2c_bus = shared.I2C_BUS
oled = solar_ssd1306.SSD1306_I2C(128, 32, i2c_bus)
rtc = solar_pcf8523.PCF8523(i2c_bus)
sensorIV_1 = solar_ina219.INA219(i2c_bus)
oled_txt_array = ["","",""]
lipo_volt_pin = analogio.AnalogIn(board.D9)

def printToOLED(text, line):
    oled.fill(0)
    oled_txt_array[line] = text
    for l in range(0,len(oled_txt_array)):
        posy = l * 12  # allow 12 rows per line of text
        oled.text(oled_txt_array[l],0,l*12)
    oled.show()

while True:
    arrayVolt = []
    arrayCurrent = []
    while len(arrayVolt) < 10:
        busVoltage = sensorIV_1.bus_voltage  # V
        shuntVoltage = sensorIV_1.shunt_voltage  # V
        voltage = busVoltage + shuntVoltage  # V
        current = sensorIV_1.current  # mA
        # power = current * loadVoltage  #mW
        arrayVolt.append(voltage)
        arrayCurrent.append(current)
        time.sleep(0.1)
    
    V = sum(arrayVolt)/len(arrayVolt)
    I = sum(arrayCurrent)/len(arrayCurrent)
    P = V * I
    
    lipo_voltage = (lipo_volt_pin.value * 3.3) / 65536 * 2

    thisTime = rtc.datetime
    printToOLED("{}{:02}{:02}{:02}:{:02}:{:02}".format(
            thisTime.tm_year, thisTime.tm_mon, thisTime.tm_mday, thisTime.tm_hour, thisTime.tm_min, thisTime.tm_sec), 0)
    printToOLED("{:.1f}V {:.1f}A {:.1f}W".format(V, I, P),1)
    printToOLED("{:.1f}V lipo {}b mem".format(lipo_voltage, gc.mem_free()),2)