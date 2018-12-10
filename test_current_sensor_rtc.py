# test of adalogger using rtc and current sensor
import time
import board
from board import SCL, SDA
import busio
import digitalio
import analogio

#  the order these are imported seems to matter...WTF
import adafruit_ina219  # current sensor
import adafruit_pcf8523  # RTC

# create the I2C bus
i2c_bus = busio.I2C(SCL, SDA)

# initialise the RTC
rtc = adafruit_pcf8523.PCF8523(i2c_bus)

# initialise the current/voltage sensor
sensorIV_1 = adafruit_ina219.INA219(i2c_bus)

lipo_volt_pin = analogio.AnalogIn(board.D9)
ob_led = digitalio.DigitalInOut(board.D13)
ob_led.direction = digitalio.Direction.OUTPUT

while True:
    arrayVolt = []
    arrayCurrent = []
    ob_led.value = True
    while len(arrayVolt) < 10:
        busVoltage = sensorIV_1.bus_voltage  # V
        shuntVoltage = sensorIV_1.shunt_voltage  # V
        voltage = busVoltage + shuntVoltage  # V
        current = sensorIV_1.current  # mA
        # power = current * loadVoltage  #mW
        arrayVolt.append(voltage)
        arrayCurrent.append(current)
        time.sleep(0.5)
        
    ob_led.value = False

    V = sum(arrayVolt)/len(arrayVolt)
    I = sum(arrayCurrent)/len(arrayCurrent)
    P = V * I

    lipo_voltage = (lipo_volt_pin.value * 3.3) / 65536 * 2
    
    t = rtc.datetime
    print("{}{:02}{:02}, {:02}:{:02}:{:02}, ".format(
        t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec), end="")

    print("{:.2f}, {:.2f}, {:.2f}, {:.1f}\n".format(V, I, P, lipo_voltage))
    
    time.sleep(1)