class RWBits:
    def __init__(self, num_bits, register_address, lowest_bit):
        self.bit_mask = 0
        for _ in range(num_bits):
            self.bit_mask = (self.bit_mask << 1) + 1
        self.bit_mask = self.bit_mask << lowest_bit
        if self.bit_mask >= (1 << 8):
            raise ValueError()
        self.buffer = bytearray(2)
        self.buffer[0] = register_address
        self.lowest_bit = lowest_bit

    def __get__(self, obj, objtype=None):
        with obj.i2c_device as i2c:
            i2c.write(self.buffer, end=1, stop=False)
            i2c.readinto(self.buffer, start=1)
        return (self.buffer[1] & self.bit_mask) >> self.lowest_bit

    def __set__(self, obj, value):
        # Shift the value to the appropriate spot and set all bits that aren't
        # ours to 1 (the negation of the bitmask.)
        value = (value << self.lowest_bit) | ~self.bit_mask
        with obj.i2c_device as i2c:
            i2c.write(self.buffer, end=1, stop=False)
            i2c.readinto(self.buffer, start=1)
            # Set all of our bits to 1.
            self.buffer[1] |= self.bit_mask
            # Set all 0 bits to 0 by anding together.
            self.buffer[1] &= value
            i2c.write(self.buffer)

class ROBits(RWBits):
    def __set__(self, obj, value):
        raise AttributeError()
