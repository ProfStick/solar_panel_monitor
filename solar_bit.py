class RWBit:
    def __init__(self, register_address, bit):
        self.bit_mask = 1 << bit
        self.buffer = bytearray(2)
        self.buffer[0] = register_address

    def __get__(self, obj, objtype=None):
        with obj.i2c_device as i2c:
            i2c.write(self.buffer, end=1, stop=False)
            i2c.readinto(self.buffer, start=1)
        return bool(self.buffer[1] & self.bit_mask)

    def __set__(self, obj, value):
        with obj.i2c_device as i2c:
            i2c.write(self.buffer, end=1, stop=False)
            i2c.readinto(self.buffer, start=1)
            if value:
                self.buffer[1] |= self.bit_mask
            else:
                self.buffer[1] &= ~self.bit_mask
            i2c.write(self.buffer)

class ROBit(RWBit):
    def __set__(self, obj, value):
        raise AttributeError()
