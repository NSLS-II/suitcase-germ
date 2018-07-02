import numpy as np
from collections import OrderedDict

# These are the masks used for the current data
CHIP_BITMASK = 0xf
CHAN_BITMASK = 0x1f
TD_BITMASK = 0x1ff
TS_BITMASK = 0x1fffffff
PD_BITMASK = 0xfff


def payload2event(data):
    '''Split up the raw data coming over the socket.

    The documentation describes the data as 2 32 bit words with have
    been merged here into a single 64 bit value.

    The layout is

       "0" [[4 bit chip addr] [5 bit channel addr]] [10 bit TD] [12 bit PD]
       "1000" [28 bit time stamp]

    '''

    # TODO sort out if this can be made faster!
    word1 = data[::2]
    word2 = data[1::2]

    # chip addr
    chip = word1 >> 27 & CHIP_BITMASK
    # chan addr
    chan = word1 >> 22 & CHAN_BITMASK
    # fine ts
    td = word1 >> 12 & TD_BITMASK

    # evergy readings
    pd = word1 & PD_BITMASK

    # FPGA tick
    ts = word2 & TS_BITMASK

    return chip, chan, td, pd, ts


def event2payload(chip, chan, td, pd, ts):
    ''' Convert event data to a payload.


    This just creates words of the form:

       "0" [[4 bit chip addr] [5 bit channel addr]] [10 bit TD] [12 bit PD]
       "1000" [28 bit time stamp]

    Notes
    -----
        This does not include the header and footer.
        The data is outputted as little endian by default.
        Note that endianness matters only when this is sent to a buffer (file
        network etc)
    '''
    # insigned little-endian, default
    # 2 words of 32 bit per data
    payload = np.zeros(len(chip)*2, dtype='<u4')
    # TODO sort out if this can be made faster!
    # word1 = data[::2]
    # word2 = data[1::2]
    # for word 1
    payload[::2] = ((chip & CHIP_BITMASK) << 27) + \
        ((chan & CHAN_BITMASK) << 22) + \
        ((td & TD_BITMASK) << 12) + (pd & PD_BITMASK)

    # for word 2
    payload[1::2] = (0x1 << 31) + (ts & TS_BITMASK)

    return payload


DATA_TYPES = OrderedDict((('chip', 8),
                          ('chan', 8),
                          ('timestamp_fine', 16),
                          ('energy', 16),
                          ('timestamp_coarse', 32)))

# build a lookup table of the data types listed in zmq.py
DATA_TYPEMAP = {name: num for num, name in enumerate(list(DATA_TYPES))}
