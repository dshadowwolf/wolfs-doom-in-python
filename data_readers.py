import struct

def read_4(file):
    z = []
    for i in range(0,4):
        z.append(file.read(1))
    return z

def read_8(file):
    z = []
    for i in range(0,8):
        p = file.read(1)
        if ord(p) != 0:          
            z.append(p)
    return z

def read_int(file):
    try:
        d = file.read(4)
    except Exception as e:
        print(f'Error Reading Data {e}')
        quit()
    finally:
        return struct.unpack('i', d)[0]
    
def read_short(file):
    try:
        d = file.read(2)
    except Exception as e:
        print(f'Error Reading Data {e}')
        quit()
    finally:
        return struct.unpack('h', d)[0]

def read_unsigned_byte(file):
    try:
        d = file.read(1)
    except Exception as e:
        print(f'Error Reading Data {e}')
        quit()
    finally:
        return struct.unpack('B', d)[0]

def read_unsigned_short(file):
    try:
        d = file.read(2)
    except Exception as e:
        print(f'Error Reading Data {e}')
        quit()
    finally:
        return struct.unpack('H', d)[0]
