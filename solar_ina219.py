from solar_i2c_device import I2CDevice
from micropython import const

def _to_signed(num):
    if num > 0x7FFF:
        num -= 0x10000
    return num

class INA219:
    """Driver for the INA219 current sensor"""
    def __init__(self, i2c_bus, addr=0x40):
        self.i2c_device = I2CDevice(i2c_bus, addr)

        self.i2c_addr = addr
        # Multiplier in mA used to determine current from raw reading
        self._current_lsb = 0
        # Multiplier in W used to determine power from raw reading
        self._power_lsb = 0

        # Set chip to known config values to start
        self._cal_value = 4096
        self.set_calibration_32V_2A()

    def _write_register(self, reg, value):
        seq = bytearray([reg, (value >> 8) & 0xFF, value & 0xFF])
        with self.i2c_device as i2c:
            i2c.write(seq)

    def _read_register(self, reg):
        buf = bytearray(3)
        buf[0] = reg
        with self.i2c_device as i2c:
            i2c.write(buf, end=1, stop=False)
            i2c.readinto(buf, start=1)

        value = (buf[1] << 8) | (buf[2])
        return value

    @property
    def shunt_voltage(self):
        value = _to_signed(self._read_register(0x01))
        return value * 0.00001

    @property
    def bus_voltage(self):
        raw_voltage = self._read_register(0x02)
        voltage_mv = _to_signed(raw_voltage >> 3) * 4
        return voltage_mv * 0.001

    @property
    def current(self):
        self._write_register(0x05, self._cal_value)

        raw_current = _to_signed(self._read_register(0x04))
        return raw_current * self._current_lsb

    def set_calibration_32V_2A(self): # pylint: disable=invalid-name
        self._current_lsb = .1  # Current LSB = 100uA per bit
        self._power_lsb = .002  # Power LSB = 2mW per bit
        self._write_register(0x05, self._cal_value)

        # Set Config register to take into account the settings above
        config = 0x2000 | \
                 0x1800 | \
                 0x0400 | \
                 0x0018 | \
                 0x0007
        self._write_register(0x00, config)

 