import time

def _bcd2bin(value):
     return value - 6 * (value >> 4)


def _bin2bcd(value):
    return value + 6 * (value // 10)

class BCDDateTimeRegister:
    def __init__(self, register_address, weekday_first=True, weekday_start=1):
        self.buffer = bytearray(8)
        self.buffer[0] = register_address
        if weekday_first:
            self.weekday_offset = 0
        else:
            self.weekday_offset = 1
        self.weekday_start = weekday_start

    def __get__(self, obj, objtype=None):
        # Read and return the date and time.
        with obj.i2c_device:
            obj.i2c_device.write(self.buffer, end=1, stop=False)
            obj.i2c_device.readinto(self.buffer, start=1)
        return time.struct_time((_bcd2bin(self.buffer[7]) + 2000,
                                 _bcd2bin(self.buffer[6]),
                                 _bcd2bin(self.buffer[5 - self.weekday_offset]),
                                 _bcd2bin(self.buffer[3]),
                                 _bcd2bin(self.buffer[2]),
                                 _bcd2bin(self.buffer[1] & 0x7F),
                                 _bcd2bin(self.buffer[4 + self.weekday_offset] -
                                          self.weekday_start),
                                 -1,
                                 -1))

    def __set__(self, obj, value):
        self.buffer[1] = _bin2bcd(value.tm_sec) & 0x7F   # format conversions
        self.buffer[2] = _bin2bcd(value.tm_min)
        self.buffer[3] = _bin2bcd(value.tm_hour)
        self.buffer[4 + self.weekday_offset] = _bin2bcd(value.tm_wday + self.weekday_start)
        self.buffer[5 - self.weekday_offset] = _bin2bcd(value.tm_mday)
        self.buffer[6] = _bin2bcd(value.tm_mon)
        self.buffer[7] = _bin2bcd(value.tm_year - 2000)
        with obj.i2c_device:
            obj.i2c_device.write(self.buffer)
