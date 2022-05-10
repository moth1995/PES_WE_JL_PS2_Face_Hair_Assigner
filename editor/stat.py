from .utils import zero_fill_right_shift

class Stat:
    def __init__(self, data:bytearray, offset:int, shift:int, mask:int, name:str):
        self.data = data
        self.offset = offset
        self.shift = shift
        self.mask = mask
        self.name = name

    def get_value(self):
        j = (self.data[self.offset]) << 8 | (self.data[(self.offset - 1)])
        j = zero_fill_right_shift(j,self.shift)
        j &= self.mask
        return j

    def set_value(self, new_value):
        j = (self.data[self.offset]) << 8 | (self.data[(self.offset - 1)])
        k = 0xFFFF & (self.mask << self.shift ^ 0xFFFFFFFF)
        j &= k
        new_value &= self.mask
        new_value <<= self.shift
        new_value = j | new_value
        self.data[(self.offset - 1)] = (new_value & 0xFF)
        self.data[self.offset] = (zero_fill_right_shift(new_value,8))
