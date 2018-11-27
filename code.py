import time
import board
from board import SCL, SDA
import busio
import analogio
import digitalio

import adafruit_ina219

i2c_bus = busio.I2C(SCL, SDA)

ina219 = adafruit_ina219.INA219(i2c_bus)

vbat_voltage = analogio.AnalogIn(board.D9) # lipo battery pin

led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT

print("ina219 test")

while True:
    led.value = True 
    busVoltage = ina219.bus_voltage
    shuntVoltage = ina219.shunt_voltage / 1000
    loadVoltage = busVoltage + shuntVoltage
    current = ina219.current
    power = current * loadVoltage
    batVoltage = (vbat_voltage.value * 3.3) / 65536 * 2
    print("Bus Voltage:     {:.1f} V".format(busVoltage))
    print("Shunt Voltage:   {:.1f} mV".format(shuntVoltage))
    print("Load Voltage:    {:.1f} V".format(loadVoltage))
    print("Current:         {:.1f} mA".format(current))
    print("Power:           {:.1f} W\n".format(power))
    print("Battery voltage: {:.1f} V\n".format(batVoltage))
    led.value = False
    
    time.sleep(2)