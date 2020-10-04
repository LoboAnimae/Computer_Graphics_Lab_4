import struct


def char(c):
    return struct.pack('=c', c.encode('ascii'))


def word(c):
    return struct.pack('=h', c)


def dword(c):
    return struct.pack('=l', c)


def color(r, g, b):
    return bytes([b, g, r])
