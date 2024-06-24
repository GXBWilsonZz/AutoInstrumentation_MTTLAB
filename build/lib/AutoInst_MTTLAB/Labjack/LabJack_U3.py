import u3
from time import sleep


class LabJack_U3:
    """
    实例化INST=LabJack_U3()后，可以用INST.d来访问LabJackPython库的其他方法
    """

    def __init__(self, addr_CK = 6010, addr_EN = 6009, addr_DA = 6008):
        """
        DIO States Register Base Address: 6000
        DIO pins are assigned as followed:
            0 -> 7: FIO0 -> FIO7
            8 -> 15: EIO0 -> EIO7
            16 -> 19: CIO0 -> CIO7
            通常MTT常用配置为：6010、6009、6008，即使用EIO0、EIO1、EIO2作为CK、EN、DA
        """
        self.d = u3.U3(False, True)
        self.addr_CK = addr_CK
        self.addr_EN = addr_EN
        self.addr_DA = addr_DA

        self.d.writeRegister(self.addr_EN, 1)       #将EN拉高
        sleep(0.005)

    def get_binary_digit(self, decimal_number, length, position):
        """
        将十进制数转换为二进制字符串，并移除前缀 '0b'
        """

        binary_string = bin(decimal_number)[2:]
        binary_string = binary_string.zfill(length)     #zfill用于填充前缀0
        # 检查位置是否合法（从右边开始计数）
        if position < 0 or position >= len(binary_string):
            raise ValueError("位置超出二进制字符串的范围")

        # 提取对应位置的字符
        # 注意：从右边开始计数，所以需要倒序索引
        return int(binary_string[-(position + 1)])


    def writebit(self, data):
        """
        往片内SPI写入一个bit数据
        """
        self.d.writeRegister(self.addr_CK, 0)        #EIO0 as CK
        self.d.writeRegister(self.addr_EN, 0)        #EIO1 as EN
        self.d.writeRegister(self.addr_DA, data)           #EIO2 as DA
        sleep(0.01)

        self.d.writeRegister(self.addr_CK, 1)  # EIO0 as CK
        self.d.writeRegister(self.addr_EN, 0)  # EIO1 as EN
        self.d.writeRegister(self.addr_DA, data)     # EIO2 as DA
        sleep(0.01)

        return 0

    def writeData_dec(self, data_dec, length, mode):
        """
        将给定的十进制数据写入片内SPI
        data_dec: 十进制数据。例如[1]；同时也支持批量写入，例如data_dec=[7,15,31]、length=[5,5,5]
        length: data_dec对应的二进制数串的位数
        mode:
            1: 先写data_dec对应二进制数串的高位，最后写低位
            0: 先写data_dec对应二进制数串的低位，最后写高位
        """
        if mode == 0:
            for i in range(0, len(data_dec)):
                for j in range(0, length[i], 1):
                    self.writebit(self.get_binary_digit(data_dec[i], length[i], j))
        if mode == 1:
            for i in range(0, len(data_dec)):
                for j in range(length[i] - 1, -1, -1):
                    self.writebit(self.get_binary_digit(data_dec[i], length[i], j))
        return 0

