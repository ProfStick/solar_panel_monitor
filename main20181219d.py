import gc  # for checking memory & garbage collection
import analogio
from digitalio import DigitalInOut, Direction, Pull
import time
import board
import busio
import adafruit_ina219  # current/voltage sensor
import storage
import adafruit_sdcard  # sd card
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

#lipo_volt_pin = analogio.AnalogIn(board.VOLTAGE_MONITOR)
led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT
button_c = DigitalInOut(board.D5)
button_c.direction = Direction.INPUT
button_c.pull = Pull.UP
button_c_time = time.time()

class lipoBat():
    def __init__(self, pinNum = board.VOLTAGE_MONITOR, vref = 3.3):
        self.pin = analogio.AnalogIn(pinNum)
        self.vref = vref
        
    def getV(self):
        ''' gets the voltage of the lipo battery.
        '''
        return (self.pin.value * self.vref) / 65536 * 2
        
class oled(adafruit_ssd1306.SSD1306_I2C):
    def __init__(self, width, height, i2c=i2c_bus):
        super().__init__(width, height, i2c)
        self.txt_array = ["", "", ""]
        
    def clear(self):
        self.txt_array = ["", "", ""]
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
    def __init__(self, add, i2c=i2c_bus):
        super().__init__(i2c, add)
        self.V = 0
        self.I = 0
        self.P = 0
        self.arrayV = []
        self.arrayI = []
        self.logArrayV = []
        self.logArrayI = []
        
    def read(self):
        ''' takes readings and adds them to an array.
        
        returns [V, I, P] in V, mA and mW
        '''
        self.V = self.bus_voltage + self.shunt_voltage
        self.I = self.current
        self.P = self.V * self.I
        self.arrayV.append(self.V)
        self.arrayI.append(self.I)
        return (self.V, self.I, self.P)
        
    def log(self):
        '''logs the average of the V and I arrays.
        
        Finds the mean value of the arrays and appends them
        to the log arrays. then clears the arrays.
        
        returns the average values
        '''
        V = sum(self.arrayV)/len(self.arrayV)
        I = sum(self.arrayI)/len(self.arrayI)
        self.logArrayV.append(V)
        self.logArrayI.append(I)
        P = I * V
        # print("the array lengths are V: {} I: {}".format(len(self.arrayV), len(self.arrayV)))
        self.clear()
        return (V, I, P)
        
        
    def clear(self):
        '''clears the V and I arrays.
        '''
        self.arrayV = []
        self.arrayI = []

    def clearLogs(self):
        '''clears the logArrays.
        '''
        self.logArrayV = []
        self.logArrayI = []
    
    def report(self):
        '''returns the mean values from the log arrays
        '''
        V = sum(self.logArrayV)/len(self.logArrayV)
        I = sum(self.logArrayI)/len(self.logArrayI)
        P = V * I
        self.clearLogs()
        return (V, I, P)
        

def timeStr(dt):
    '''Create a time string from a datetime structure
    
    arguments:
      dt: the datetime to determine the string from
    
    returns:
      t_str: the time string formated as HHMMSS
    '''
    
    t_str = "{:02}{:02}{:02}".format(dt.tm_hour, 
        dt.tm_min, dt.tm_sec)
    return t_str
    
def dateStr(dt):
    '''Create a date string from a datetime structure
    
    arguments:
      dt: the datetime to determine the string from
    
    returns:
      d_str: the date string formated as YYYYMMDD
    '''
    
    d_str = "{:04}{:02}{:02}".format(dt.tm_year, dt.tm_mon, dt.tm_mday)
    return d_str
    
def dateTimeStr(dt):
    '''Create a datetime string from a datetime structure
    
    arguments:
      dt: the datetime to determine the string from
    
    returns:
      dt_str: the datetime string formated as YYYYMMDDTHHMMSS
    '''
    
    dt_str = "{:04}{:02}{:02}T{:02}{:02}{:02}".format(
        dt.tm_year, dt.tm_mon, dt.tm_mday, 
        dt.tm_hour, dt.tm_min, dt.tm_sec)
    return dt_str
    
    
# create a new file for logging with column headers
dt_str = dateTimeStr(rtc.datetime)
fn = "/sd_card/solar_{}.txt".format(dt_str)
with open(fn, "w") as log_file:
    log_file.write("time_stamp, "
        "V1 (V), I1 (mA), P1 (mW), "
        "V2 (V), I2 (mA), P2 (mW), "
        "V3 (V), I3 (mA), P3 (mW), "
        "Vbat (V), mem (b) \n")



display = oled(128, 32)
sensorIV_2 = sensorIV(0x40)
sensorIV_1 = sensorIV(0x41)
sensorIV_0 = sensorIV(0x44)

sensorIV_array = [sensorIV_0, sensorIV_1, sensorIV_2]

lipo = lipoBat()

lastLog = rtc.datetime  # last readings were taken
lastStore = rtc.datetime  # last readings were taken

mpp = False

while True:
    thisTime = rtc.datetime
    for s in sensorIV_array:
        s_readings = s.read()  #read every cycle
    
    # log then clear readings every minute
    if thisTime.tm_sec != lastLog.tm_sec:
        lastLog = thisTime  # reset the timer
        for s in sensorIV_array:
            s_log = s.log()
            if mpp:
                i = sensorIV_array.index(s)
                display.displayText("{:.1f} {:.1f} {:.1f}".format(
                    *s_log), i)

        if not mpp:
            display.displayText(dateTimeStr(thisTime), 0)
            display.displayText("{:.1f} {:.1f} {:.1f}".format(
                sensorIV_0.I, sensorIV_1.I, sensorIV_2.I), 1)
            display.displayText("b:{:.1f}V m:{}b".format(
                lipo.getV(), gc.mem_free()), 2)
        
    # every minute store the mean readings then clear
    if thisTime.tm_min != lastStore.tm_min:
        lastStore = thisTime
        store_str = dateTimeStr(thisTime)
        
        for s in sensorIV_array:
            s_str = ", {:.2f}, {:.2f}, {:.2f}".format(*s.report())
            store_str = store_str + s_str
            # s.clear()
        
        # lipo_voltage = (lipo_volt_pin.value * 3.3) / 65536 * 2
        store_str = store_str + ", {:.1f}, {}\n".format(
            lipo.getV(), gc.mem_free())
        
        print(store_str)
        with open(fn, "a") as log_file:
            try:
                log_file.write(store_str)
            except:
                print('bugger')

    if not button_c.value: # this button pulled up so false when pressed
        now = time.time()
        if now > button_c_time:  # 1 second to avoid bounce
            mpp = not mpp
            button_c_time = now

    gc.collect()  # collect the garbage
    time.sleep(0.05)