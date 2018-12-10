# test of sd card and rtc

import time
import board
from board import SCL, SDA
import busio
import digitalio
import analogio
import storage

import adafruit_pcf8523  
import adafruit_sdcard

i2c_bus = busio.I2C(SCL, SDA)
# initialise the RTC
rtc = adafruit_pcf8523.PCF8523(i2c_bus)


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
    log_file.write("date, time\n")


while True:
    t = rtc.datetime

    with open("/sd_card/solar_log.txt", "a+") as log_file:
        log_file.write("{}{:02}{:02}, {:02}:{:02}:{:02}\n".format(
            t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec))
        
        # comment out if don't want to print file
        log_file.seek(0, 0) # set positon to beining of file
        for l in log_file.readlines():
            print(l, end="")  # each line already has newline character
    
        
    time.sleep(2)