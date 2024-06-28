import u3
from time import sleep

d = u3.U3(False, True)
d.writeRegister(6009, 1)
sleep(0.005)

def get_binary_digit(decimal_number, length, position):
    # 将十进制数转换为二进制字符串，并移除前缀 '0b'
    binary_string = bin(decimal_number)[2:]
    binary_string = binary_string.zfill(length)
    # 检查位置是否合法（从右边开始计数）
    if position < 0 or position >= len(binary_string):
        raise ValueError("位置超出二进制字符串的范围")

    # 提取对应位置的字符
    # 注意：从右边开始计数，所以需要倒序索引
    return int(binary_string[-(position + 1)])


def writebit(data):
# DIO pins are assigned as followed:
# 0 -> 7: FIO0 -> FIO7
# 8 -> 15: EIO0 -> EIO7
# 16 -> 19: CIO0 -> CIO7
    d.writeRegister(6010, 0)        #EIO0 as CK
    d.writeRegister(6009, 0)        #EIO1 as EN
    d.writeRegister(6008, data)           #EIO2 as DA
    sleep(0.01)

    d.writeRegister(6010, 1)  # EIO0 as CK
    d.writeRegister(6009, 0)  # EIO1 as EN
    d.writeRegister(6008, data)     # EIO2 as DA
    sleep(0.01)

    return 0

def writebit_dec(data_dec, length, mode):
    # for i in range(0, length, 1):
    #     writebit(get_binary_digit(data_dec, length, i))

    if mode == 0:   # 先写二进制数串的低位，最后写高位
        for i in range(0, len(data_dec)):
            for j in range(0, length[i], 1):
                writebit(get_binary_digit(data_dec[i], length[i], j))
    if mode == 1:   # 先写二进制数串的高位，最后写低位
        for i in range(0, len(data_dec)):
            for j in range(length[i] - 1, -1, -1):
                writebit(get_binary_digit(data_dec[i], length[i], j))
    return 0


