import time
import board
from board import SCL, SDA
import busio
import analogio
import digitalio

import adafruit_ina219

i2c_bus = busio.I2C(SCL, SDA)

ina219 = adafruit_ina219.INA219(i2c_bus)

vbat_voltage = analogio.AnalogIn(board.D9)  # lipo battery pin

led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT

print("V, I, P, Vbat")

while True:
    arrayVolt = []
    arrayCurrent = []
    while len(arrayVolt) < 10:
        led.value = True 
        busVoltage = ina219.bus_voltage  # V
        shuntVoltage = ina219.shunt_voltage  # V
        voltage = busVoltage + shuntVoltage  # V
        current = ina219.current  # mA
        # power = current * loadVoltage  #mW
        arrayVolt.append(voltage)
        arrayCurrent.append(current)
        time.sleep(0.5)
        # led.value = False
    
    led.value = False
    
    V = sum(arrayVolt)/len(arrayVolt)
    I = sum(arrayCurrent)/len(arrayCurrent)
    P = V * I

    batVoltage = (vbat_voltage.value * 3.3) / 65536 * 2

    print("{:.2f}, {:.2f}, {:.2f}, {:.1f}".format(V, I, P, batVoltage))
        
    time.sleep(5)