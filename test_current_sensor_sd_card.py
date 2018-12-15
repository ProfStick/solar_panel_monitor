#test of sd card and current sensor

import time
import board
from board import SCL, SDA
import busio
import analogio
import digitalio
import storage

# import adafruit_pcf8523  
import adafruit_ina219  # current sensor
import adafruit_sdcard

i2c_bus = busio.I2C(SCL, SDA)

sensorIV_1 = adafruit_ina219.INA219(i2c_bus)

vbat_voltage = analogio.AnalogIn(board.D9)  # lipo battery pin

# create the SPI bus and a digital output for the microSD
SD_CS = board.D10
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(SD_CS)
# create the microSD card object and the filesystem object
sd_card = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sd_card)
storage.mount(vfs, "/sd_card")

# create an empty file for logging
# this ensures that any previously create log in emptied
with open("/sd_card/solar_log.txt", "w") as log_file:
    log_file.write("V, I, P, Vbat\n")

led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT

while True:
    arrayVolt = []
    arrayCurrent = []
    while len(arrayVolt) < 10:
        led.value = True 
        busVoltage = sensorIV_1.bus_voltage  # V
        shuntVoltage = sensorIV_1.shunt_voltage  # V
        voltage = busVoltage + shuntVoltage  # V
        current = sensorIV_1.current  # mA
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

    with open("/sd_card/solar_log.txt", "a+") as log_file:
        log_file.write("{:.2f}, {:.2f}, {:.2f}, {:.1f}\n".format(V, I, P, batVoltage))
        
        # comment out if don't want to print file
        log_file.seek(0, 0) # set positon to beining of file
        for l in log_file.readlines():
            print(l, end="")  # each line already has newline character
    
        
    time.sleep(1)