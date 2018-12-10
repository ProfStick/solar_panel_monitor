# from adafruit_bus_device.i2c_device import I2CDevice
from solar_i2c_device import I2CDevice
import solar_i2c_bit as i2c_bit
import solar_i2c_bits as i2c_bits
# from adafruit_register import i2c_bcd_alarm
import solar_i2c_bcd_datetime as i2c_bcd_datetime

STANDARD_BATTERY_SWITCHOVER_AND_DETECTION = 0b000
BATTERY_SWITCHOVER_OFF = 0b111

class PCF8523:
    lost_power = i2c_bit.RWBit(0x03, 7)

    power_management = i2c_bits.RWBits(3, 0x02, 5)

    datetime_register = i2c_bcd_datetime.BCDDateTimeRegister(0x03, False, 0)

    # alarm = i2c_bcd_alarm.BCDAlarmTimeRegister(0x0a, has_seconds=False, weekday_shared=False,
    #                                           weekday_start=0)
 
    alarm_interrupt = i2c_bit.RWBit(0x00, 1)

    alarm_status = i2c_bit.RWBit(0x01, 3)

    battery_low = i2c_bit.ROBit(0x02, 2)

    def __init__(self, i2c_bus):
        self.i2c_device = I2CDevice(i2c_bus, 0x68)

        buf = bytearray(2)
        buf[0] = 0x12
        with self.i2c_device as i2c:
            i2c.write(buf, end=1, stop=False)
            i2c.readinto(buf, start=1)

        if (buf[1] & 0b00000111) != 0b00000111:
            raise ValueError("Unable to find PCF8523 at i2c address 0x68.")

    @property
    def datetime(self):
        return self.datetime_register

    @datetime.setter
    def datetime(self, value):
        # Automatically sets lost_power to false.
        self.power_management = STANDARD_BATTERY_SWITCHOVER_AND_DETECTION
        self.datetime_register = value