"""This is a Hello-World example for communicating with your FSWP-50 instrument.
The field 'Alias' defines the variable name with which 
you are going to address the instrument in your python scripts.
For the FSWP-50, the alias is 'fswp'
"""

# RsInstrument package is hosted on pypi.org
from RsInstrument import *
from time import sleep
import numpy as np
import u3

# Initialize the session
fswp50 = RsInstrument('TCPIP::10.72.54.15::hislip0', reset=False)

recdur = 1  # Time in seconds to find max hold peaks
filename = r'E:\OneDrive - GXB\研究生阶段\项目\2024_06_15 自动化测试\Data\Data.csv'



idn = fswp50.query('*IDN?')
print(f"\nHello, I am: '{idn}'")
print(f'Instrument installed options: {",".join(fswp50.instrument_options)}')

def trace_get(filename):
    """Initialize continuous measurement, stop it after the desired time, query trace data"""
    # Get y data (amplitude for each point)
    trace_data = fswp50.query('Trace:DATA? TRACe1')  # Read y data of trace 1
    csv_trace_data = trace_data.split(",")  # Slice the amplitude list
    trace_len = len(csv_trace_data)  # Get number of elements of this list

    # Reconstruct x data (frequency for each point) as it can not be directly read from the instrument
    start_freq = fswp50.query_float('FREQuency:STARt?')
    stop_freq = fswp50.query_float('FREQuency:STOP?')
    step_size = (stop_freq-start_freq) / (trace_len-1)

    # Now write values into file
    file = open(filename, 'w')  # Open file for writing
    file.write("Frequency in Hz;Phase Noise\n")  # Write the headline
    x = 0  # Set counter to 0 as list starts with 0
    while x < int(trace_len)-1:  # Perform loop until all sweep points are covered
        file.write(f'{(start_freq + x * step_size):.1f}')  # Write adequate frequency information
        file.write(";")
        amp = float(csv_trace_data[x+1])
        file.write(f'{amp:.2f}')  # Write adequate amplitude information
        file.write("\n")
        x = x+2
    file.close()  # CLose the file
def fswp50_PWR_config(channel, vset, vmin, vmax):
    #This config does not enable any power supply output
    if channel == 'Vtune':    #VTUNE Channel
        fswp50.write('SOUR:VOLT:CONT:LEV:AMPL ' + str(vset))
        fswp50.write('SOUR:VOLT:CONT:LEV:LIM:LOW ' + str(vmin))
        fswp50.write('SOUR:VOLT:CONT:LEV:LIM:HIGH ' + str(vmax))
    if channel == 'Vaux':    #Vaux Channel
        fswp50.write('SOUR:VOLT:AUX:LEV:AMPL ' + str(vset))
        fswp50.write('SOUR:VOLT:AUX:LEV:LIM:LOW ' + str(vmin))
        fswp50.write('SOUR:VOLT:AUX:LEV:LIM:HIGH ' + str(vmax))
    if channel == 'Vsupply':    #Vsupply Channel
        fswp50.write('SOUR:VOLT:POW:LEV:AMPL ' + str(vset))
        fswp50.write('SOUR:VOLT:POW:LEV:LIM:LOW ' + str(vmin))
        fswp50.write('SOUR:VOLT:POW:LEV:LIM:HIGH ' + str(vmax))
def fswp50_PWR_switch(channel, state):
    # channel: 'Vtune', 'Vaux', 'Vsupply', 'ALL', 'DC'  ; 'ALL'表示Vtune、Vaux、Vsupply二级电源全开，'DC'表示一级电源开关（总开关）
    # state: 'ON', 'OFF'
    if channel == 'Vtune':
        fswp50.write('SOUR:VOLT:CONT:LEV ' + state)
    if channel == 'Vaux':
        fswp50.write('SOUR:VOLT:AUX:LEV ' + state)
    if channel == 'Vsupply':
        fswp50.write('SOUR:VOLT:POW:LEV ' + state)
    if channel == 'ALL':
        fswp50.write('SOUR:VOLT:CONT:LEV ' + state)
        fswp50.write('SOUR:VOLT:AUX:LEV ' + state)
        fswp50.write('SOUR:VOLT:POW:LEV ' + state)
    if channel == 'DC':
        fswp50.write('SOUR:VOLT ' + state)



def fswp50_test_FTR(SCA_code, vtune_start, vtune_stop, sweep_pts, fix_source):   #vtune Unit: V
    #fix_source: 'Vaux', 'Vsupply'
    #使用该函数之前要保证有一路fixed source的二级开关打开了

    fswp50.write('INST:SEL PNO')      #设置为PN测试界面
    fswp50.write('CONF:VCO:MEAS ON')  #设置为VCO Characteristic
    fswp50.write('LAY:WIND2:REM')
    fswp50.write('LAY:WIND3:REM')
    fswp50.write('LAY:WIND4:REM')

    fswp50_PWR_config('Vtune',vtune_start,vtune_start,vtune_stop)

    fswp50.write('CONF:VCO:SWE:SOUR VTUN')    #选择VTUNE作为sweep source
    if fix_source == 'Vaux':   #配置fix source并开启（必须项，否则无法进行扫参）
        fswp50.write('CONF:VCO:FIX:SOUR ' + 'VAUX')
        fswp50_PWR_switch('Vaux', 'ON')
    if fix_source == 'Vsupply':
        fswp50.write('CONF:VCO:FIX:SOUR ' + 'VSUP')
        fswp50_PWR_switch('Vsupply', 'ON')

    fswp50.write('SOUR:VOLT:POW:LEV:MODE VOLT')   #Select the type of output at the Vtune connector
    fswp50.write('CONF:VCO:SWE:STAR ' + str(vtune_start))
    fswp50.write('CONF:VCO:SWE:STOP ' + str(vtune_stop))
    fswp50.write('CONF:VCO:SWE:POIN ' + str(sweep_pts))

    fswp50.write('SOUR:VOLT:CONT:LEV ON')     #开启VTUNE电源; 要开启其他电源，只需要将CONT替换为AUX和POW即分别代表开启Vaux和Vsupply的电源
    fswp50.write('SOUR:VOLT ON')  #开启总电源
    # fswp.write_str_with_opc('INIT:IMM')  #Run Single

def fswp50_get_spot_PN(trace_index, offset):
    #offset: e.g. 1000000
    start_freq = fswp50.query_float('FREQuency:STARt?')
    stop_freq = fswp50.query_float('FREQuency:STOP?')
    if offset < start_freq or offset > stop_freq:
        print("Offset is out of bound!")
        return

    fswp50.write('CALC:SNO:USER ON')
    fswp50.write('CALC:SNO1:STAT ON')     #User Defined marker 1 is used to get spot PN
    fswp50.write('CALC:SNO1:X ' + str(offset))
    spot_PN = fswp50.query('CALC:SNO1:TRAC' + str(trace_index) + ':Y?')
    fswp50.write('CALC:SNO:USER OFF')
    return float(spot_PN)

def fswp50_get_spot_PN_DEC(trace_index):
    #获取整条PN曲线10^x处的spot phase noise
    #trace_index: 1-6
    spot_PN = fswp50.query('CALC:SNO:TRAC' + str(trace_index) + ':DEC:Y?')
    spot_PN = spot_PN.split(",")
    # freq_start = fswp.query_float('FREQuency:STARt?')
    # freq_stop = fswp.query_float('FREQuency:STOP?')
    # freq = np.logspace(float(np.log10(freq_start)), float(np.log10(freq_stop)), len(spot_PN)).tolist()
    freq = fswp50.query('CALC:SNO:DEC:X?')
    freq = freq.split(",")

    return freq, spot_PN
def fswp50_run_single():
    # fswp.write_str_with_opc('INIT:IMM')
    fswp50.write_str_with_opc('INIT:IMM')
def fswp50_get_freq():
    return float(fswp50.query('FREQ:CENT?'))
def fswp50_get_output_current():
    output_current = fswp50.query('SOUR:CURR:SEQ:RES?')
    output_current = output_current.split(",")
    return output_current


def fswp50_PN_init():
    '''
    将FSWP50设置为相噪测量模式，并自动配置常用参数
    '''
    fswp50.write_str_with_opc('*RST')
    fswp50.write('INST:SEL PNO')
    fswp50.write('FREQ:STAR 10KHZ')
    fswp50.write('FREQ:STOP 100MHZ')
    fswp50.write('INST:SEL PNO')
    fswp50.write('SWE:XFAC 1000')
    fswp50.write('LIST:BWID:RAT 1')
    # fswp.write('INP:ATT 0')
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
def screen_copy(inst_filename, pc_filename):
    """Prepare and perform screenshot, transfer data to local PC"""
    fswp50.write('HCOPy:DEVice:LANGuage PNG')  # Select file format for screenshot (possible: PNG or JPG)
    fswp50.write(f'MMEMory:NAME {inst_filename}')  # Define path and name for the screenshot on the instrument
    fswp50.write('HCOPy:IMMediate')  # Perform screenshot and save it on the analyzer
    # Transfer file to PC
    fswp50.data_chunk_size = 10000
    fswp50.query_bin_block_to_file(f'MMEMory:DATA? {inst_filename}', f'{pc_filename}', append=False)
    fswp50.write(f'MMEMory:DELete {inst_filename}')  # And delete it on the instrument

# Enter your code here...

#FSWP50 Initialization
# fswp50_init()


#
# trace_get()
# PWR_switch('Vaux', 'ON')
# fswp50_test_FTR(0, 0, 3, 10, 'Vsupply')

# PWR_config('Vaux', 1.5, 0, 2)
# fswp.write('INIT:IMM')      #Run Single
# Close the session

inst_filename = '"\Public\Screen Shots\screenshot.png"'
data_path = r'E:\OneDrive - GXB\研究生阶段\项目\2024_06_15 自动化测试\Data\\'

d = u3.U3(False, True)
d.writeRegister(6009, 1)
sleep(0.005)

# fswp.write('SOUR:CURR:POW:LIM:HIGH 0.06')
# fswp50_PWR_config('Vsupply', 5, 0, 5)
# fswp50_PWR_config('Vaux', 1.2, 0, 1.5)
# fswp50_PWR_switch('DC', 'ON')
#
# # print("Iadj;Fvco;PN@100kHz;PN@1MHz;PN@10MHz;FoM@100kHz;FoM@1MHz;FoM@10MHz;Idc;Iidle")
#
# file = open(data_path + 'data.csv', 'w')  # Open file for writing
# file.write("Iadj;Fvco;PN@100kHz;PN@1MHz;PN@10MHz;FoM@100kHz;FoM@1MHz;FoM@10MHz;Idc;Iidle\n")  # Write the headline
#
# for Iadj in [1, 4, 8, 16, 32, 64, 128, 256]:
#
#
#     d.writeRegister(6009, 1)
#     sleep(0.005)
#     writebit_dec([3], [5], 0)  # MODE1 3;MODE2 19;MODE3 5 MODE4 12
#     writebit_dec([3], [2], 0)  # gm_sw
#     writebit_dec([63], [6], 0)  # sca
#     writebit_dec([0], [13], 0)  # I_adj
#     writebit_dec([0], [1], 0)  # Imax
#     writebit_dec([0], [3], 0)  # null
#     d.writeRegister(6009, 1)
#     sleep(0.005)
#
#     fswp50_run_single()
#     Iidle = float(fswp50_get_output_current()[0])
#
#     d.writeRegister(6009, 1)
#     sleep(0.005)
#     writebit_dec([3], [5], 0)  # MODE1 3;MODE2 19;MODE3 5 MODE4 12
#     writebit_dec([3], [2], 0)  # gm_sw
#     writebit_dec([63], [6], 0)  # sca
#     writebit_dec([Iadj], [13], 0)  # I_adj
#     writebit_dec([0], [1], 0)  # Imax
#     writebit_dec([0], [3], 0)  # null
#     d.writeRegister(6009, 1)
#     sleep(0.005)
#
#     fswp50_run_single()
#     Fvco = fswp50_get_freq()
#     PN_100k = fswp50_get_spot_PN(1, 100e3)
#     PN_1M = fswp50_get_spot_PN(1, 1e6)
#     PN_10M = fswp50_get_spot_PN(1, 10e6)
#     Idc = float(fswp50_get_output_current()[0]) - Iidle
#     FoM_100k = -PN_100k + 20*np.log10(Fvco/100e3) - 10*np.log10(Idc*0.5/1e-3)
#     FoM_1M = -PN_1M + 20*np.log10(Fvco/1e6) - 10*np.log10(Idc*0.5/1e-3)
#     FoM_10M = -PN_10M + 20*np.log10(Fvco/10e6) - 10*np.log10(Idc*0.5/1e-3)
#     print("Iadj = %d Fvco = %f, PN@1MHz = %f, PN@10MHz = %f, FoM@1MHz = %f, FoM@10MHz = %f, Idc = %f Iidle = %f" % (Iadj, Fvco, PN_1M, PN_10M, FoM_1M, FoM_10M, Idc, Iidle))
#     file.write("%d;%f;%f;%f;%f;%f;%f;%f;%f;%f" % (Iadj, Fvco, PN_100k, PN_1M, PN_10M, FoM_100k, FoM_1M, FoM_10M, Idc, Iidle))
#     file.write("\n")
#     screen_copy(inst_filename, data_path+'Iadj_%d.png' % Iadj)
#     trace_get(data_path+'PN_Iadj_%d.csv' % Iadj)
# file.close()  # CLose the file

fswp50_PN_init()
fswp50_test_FTR(0,0, 2.5,12,'Vsupply')
for SCA in range(0, 1):
    d.writeRegister(6009, 1)
    sleep(0.005)
    writebit_dec([3], [5], 0)  # MODE1
    writebit_dec([3], [2], 0)  # gm_sw
    writebit_dec([SCA], [6], 0)  # sca
    writebit_dec([8], [13], 0)  # I_ad
    writebit_dec([0], [1], 0)  # Imax
    writebit_dec([0], [3], 0)  # null
    d.writeRegister(6009, 1)
    sleep(0.005)

    fswp50_run_single()
    screen_copy(inst_filename, data_path+'freq_SCA_%d.png' % SCA)
    # trace_get(data_path + 'freq_SCA_%d.csv' % SCA)


# d.writeRegister(6009, 1)
# sleep(0.005)
# writebit_dec([3], [5], 0)  # MODE1
# writebit_dec([3], [2], 0)  # gm_sw
# writebit_dec([63], [6], 0)  # sca
# writebit_dec([1], [13], 0)  # I_ad
# writebit_dec([0], [1], 0)  # Imax
# writebit_dec([0], [3], 0)  # null
# d.writeRegister(6009, 1)
# sleep(0.005)

fswp50.close()
