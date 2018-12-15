import sys
import gc  # for checking memory & garbage collection
import analogio
from digitalio import DigitalInOut, Direction, Pull
import time
import board
import busio
import adafruit_ina219  # current/voltage sensor
import storage
import adafruit_sdcard # sd card
import adafruit_pcf8523  # rtc
import adafruit_ssd1306  # oled

i2c_bus = busio.I2C(board.SCL, board.SDA)
rtc = adafruit_pcf8523.PCF8523(i2c_bus)

# create the SPI bus and a digital output for the microSD
SD_CS = board.D10
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = DigitalInOut(SD_CS)
# create the microSD card object and the filesystem object
sd_card = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sd_card)
storage.mount(vfs, "/sd_card")

# create an empty file for logging
t = rtc.datetime # 20181214T085713
t_str = "{}{:02}{:02}T{:02}{:02}{:02}".format(
    t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
fn = "/sd_card/solar_{}.txt".format(t_str)
with open(fn, "w") as log_file:
    log_file.write("time_stamp, "
    "V1 (V), I1 (mA), P1 (mW), "
    "V2 (V), I2 (mA), P2 (mW), "
    "V3 (V), I3 (mA), P3 (mW), "
    "Vbat (V) \n")



class oled(adafruit_ssd1306.SSD1306_I2C):
    def __init__ (self, width, height, i2c=i2c_bus):
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
        

class sensorIV(adafruit_ina219.INA219):
    def __init__ (self, add, i2c=i2c_bus):
        super().__init__(i2c, add)
        self.arrayV = []
        self.arrayI = []
        
    def read(self):
        self.arrayV.append(self.bus_voltage + self.shunt_voltage)
        self.arrayI.append(self.current)
        
    def clear(self):
        self.arrayV = []
        self.arrayI = []
    
    def report(self):
        V = sum(self.arrayV)/len(self.arrayV)
        I = sum(self.arrayI)/len(self.arrayI)
        P = V * I
        self.clear()
        return (V, I, P)
        

display = oled(128, 32)
sensorIV_0 = sensorIV(0x40)
sensorIV_1 = sensorIV(0x41)
sensorIV_2 = sensorIV(0x44)

sensorIV_array = [sensorIV_0, sensorIV_1, sensorIV_2]

lipo_volt_pin = analogio.AnalogIn(board.VOLTAGE_MONITOR)
led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT
button_c = DigitalInOut(board.D5)
button_c.direction = Direction.INPUT
button_c.pull = Pull.UP
button_c_time = time.time()

lastRead = rtc.datetime  # last readings were taken
lastStore = rtc.datetime  # last readings were taken

while True:
    thisTime = rtc.datetime
    
    if thisTime.tm_sec > lastRead.tm_sec:
        lastRead = thisTime  # reset the timer
        for s in sensorIV_array:
            s.read()
        
        lipo_voltage = (lipo_volt_pin.value * 3.3) / 65536 * 2
        display.displayText("{:02}{:02}{:02}".format(thisTime.tm_hour, thisTime.tm_min, thisTime.tm_sec),0)
        display.displayText("{:.1f} V".format(lipo_voltage),1)
        gc.collect() #  collect the garbage
        display.displayText("{} b".format(gc.mem_free()),2)
        
    elif thisTime.tm_sec < lastRead.tm_sec:
        lastRead = thisTime  # reset the timer if lastRead is 59 secs
            
    if thisTime.tm_min > lastStore.tm_min:  # every minute take the mean and store the reading
        lastStore = thisTime
        store_str = "{:04}{:02}{:02}T{:02}{:02}{:02}".format(
            t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
        
        for s in sensorIV_array:
            # "time_stamp, V0, I0, P0, V1, I1, P1, V2, I2, P2, Vbat\n"
            s_str = ", {:.2f}, {:.2f}, {:.2f}".format(*s.report())
            store_str = store_str + s_str
            s.clear()
        
        lipo_voltage = (lipo_volt_pin.value * 3.3) / 65536 * 2
        store_str = store_str + ", {:.1f}\n".format(lipo_voltage)
        
        with open(fn, "a+") as log_file:
            log_file.write(store_str)
        
            # comment out if don't want to print file
            log_file.seek(0, 0) # set positon to beining of file
            for l in log_file.readlines():
                print(l, end="")  # each line already has newline character
        