class I2CDevice:
    def __init__(self, i2c, device_address):
        """
        Try to read a byte from an address,
        if you get an OSError it means the device is not there
        """
        while not i2c.try_lock():
            pass
        try:
            i2c.writeto(device_address, b'')
        except OSError:
            # some OS's dont like writing an empty bytesting...
            # Retry by reading a byte
            try:
                result = bytearray(1)
                i2c.readfrom_into(device_address, result)
            except OSError:
                raise ValueError("No I2C device at address: %x" % device_address)
        finally:
            i2c.unlock()

        self.i2c = i2c
        self.device_address = device_address

    def readinto(self, buf, **kwargs):
        self.i2c.readfrom_into(self.device_address, buf, **kwargs)

    def write(self, buf, **kwargs):
        self.i2c.writeto(self.device_address, buf, **kwargs)

#pylint: disable-msg=too-many-arguments
    def write_then_readinto(self, out_buffer, in_buffer, *,
                            out_start=0, out_end=None, in_start=0, in_end=None, stop=True):
        if out_end is None:
            out_end = len(out_buffer)
        if in_end is None:
            in_end = len(in_buffer)
        if hasattr(self.i2c, 'writeto_then_readfrom'):
            # In linux, at least, this is a special kernel function call
            self.i2c.writeto_then_readfrom(self.device_address, out_buffer, in_buffer,
                                           out_start=out_start, out_end=out_end,
                                           in_start=in_start, in_end=in_end, stop=stop)
        else:
            # If we don't have a special implementation, we can fake it with two calls
            self.write(out_buffer, start=out_start, end=out_end, stop=stop)
            self.readinto(in_buffer, start=in_start, end=in_end)

#pylint: enable-msg=too-many-arguments

    def __enter__(self):
        while not self.i2c.try_lock():
            pass
        return self

    def __exit__(self, *exc):
        self.i2c.unlock()
        return False