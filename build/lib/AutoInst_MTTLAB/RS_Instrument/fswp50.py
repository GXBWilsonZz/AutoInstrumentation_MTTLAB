"""This is a Hello-World example for communicating with your FSWP-50 instrument.
The field 'Alias' defines the variable name with which 
you are going to address the instrument in your python scripts.
For the FSWP-50, the alias is 'fswp'
"""
import RsInstrument.Internal.Conversions as Conversions
# RsInstrument package is hosted on pypi.org
from RsInstrument import *


class fswp50:
    """
    实例化INST=fswp50()后，可以用INST.RsInst来访问RsInstrument库的其他方法
    """

    def __init__(self, ip_address):
        """
        ip_address: fswp50的IP地址
        """
        self.RsInst = RsInstrument('TCPIP::'+ip_address+'::hislip0', reset=False)
        idn = self.RsInst.query('*IDN?')
        print(f"\nHello, I am: '{idn}'")
        print(f'Instrument installed options: {",".join(self.RsInst.instrument_options)}')

    def wait(self):
        self.RsInst.query_opc()

    def get_trace_csv(self, trace_index: int, filename, mode: str, head_xdata:str, head_ydata:str):
        """
        获取当前窗口中traceN的数据，并导出到csv文件中
            filename:
            mode: 打开文件的模式，例如'w'、'a'
            head_xdata: csv文件head line中对x轴数据的注释，例如'frequency (Hz)'
            head_ydata: csv文件head line中对y轴数据的注释，例如'Phase Noise (dBc/Hz)'
        """
        # trace_data = self.RsInst.query('Trace:DATA? TRACe'+str(trace_index))  # Read y data of trace N
        # csv_trace_data = trace_data.split(",")  # Slice the amplitude list
        csv_trace_data = self.RsInst.query_bin_or_ascii_float_list('FORM ASC;:TRAC? TRACE'+str(trace_index))
        trace_len = len(csv_trace_data)  # Get number of elements of this list

        # Now write values into file
        file = open(filename, mode)  # Open file for writing
        file.write(head_xdata + ',' + head_ydata + '\n')  # Write the headline
        x = 0  # Set counter to 0 as list starts with 0
        while x < int(trace_len)-1:  # Perform loop until all sweep points are covered
            data1 = float(csv_trace_data[x])
            file.write(f'{data1:.5f}')  # Write adequate frequency information
            file.write(",")
            data2 = float(csv_trace_data[x + 1])
            file.write(f'{data2:.5f}')  # Write adequate phase noise information
            file.write("\n")
            x = x + 2
        file.close()  # CLose the file

    def get_PN_trace_csv(self, trace_index: int, filename):
        """
        抓取相噪曲线，并将结果输出到csv文件中
            trace_index: 所捕获的曲线序号，1-6
            filename: 数据保存文件的路径
        """
        # Get y data (amplitude for each point)

        # trace_data = self.RsInst.query('Trace:DATA? TRACe'+str(trace_index))  # Read y data of trace N
        # csv_trace_data = trace_data.split(",")  # Slice the amplitude list
        csv_trace_data = self.RsInst.query_bin_or_ascii_float_list('FORM ASC;:TRAC? TRACE'+str(trace_index))
        trace_len = len(csv_trace_data)  # Get number of elements of this list

        # Reconstruct x data (frequency for each point) as it can not be directly read from the instrument
        start_freq = self.RsInst.query_float('FREQuency:STARt?')
        stop_freq = self.RsInst.query_float('FREQuency:STOP?')
        step_size = (stop_freq-start_freq) / (trace_len-1)

        # Now write values into file
        file = open(filename, 'w')  # Open file for writing
        file.write("Offset Frequency (Hz),Phase Noise (dBc/Hz)\n")  # Write the headline
        x = 0  # Set counter to 0 as list starts with 0
        while x < int(trace_len)-1:  # Perform loop until all sweep points are covered
            file.write(f'{(start_freq + x * step_size):.1f}')  # Write adequate frequency information
            file.write(",")
            PN = float(csv_trace_data[x+1])
            file.write(f'{PN:.2f}')  # Write adequate phase noise information
            file.write("\n")
            x = x+2
        file.close()  # CLose the file
    def set_trace_mode(self, trace_index:int, mode:str):
        """
        设置trace的模式
            trace_index
            mode:
                "Clear Write"
                "Blank"
                "View"
        """
        if mode == "Clear Write":
            mode_str = 'WRIT'
        if mode == "Blank":
            mode_str = 'BLAN'
        if mode == "View":
            mode_str = 'VIEW'
        self.RsInst.write('DISP:TRAC'+str(trace_index)+':MODE '+mode_str)

    def set_auto_search(self, start_freq: float=1e9, stop_freq: float=30e9, threshold: int=-20):
        """
        Auto Search参数配置
            start_freq: (Unit:Hz)
            stop_freq: (Unit:Hz)
            threshold: (Unit:dBm)
        """
        self.RsInst.write('ADJ:CONF:FREQ:LIM:LOW ' + Conversions.decimal_value_to_str(start_freq))
        self.RsInst.write('ADJ:CONF:FREQ:LIM:HIGH ' + Conversions.decimal_value_to_str(stop_freq))
        self.RsInst.write('ADJ:CONF:LEV:THR ' + str(threshold))

    def power_config(self, channel: str, vset: float, vmin: float, vmax: float):
        """
        配置fswp50的三个电源输出端口。该函数不会使能电源输出
            channel:
                'Vtune': Vtune输出端口
                'Vaux': Vaux输出端口
                'Vsupply': Vsupply输出端口
            vset: 电源输出值 (Unit: V)
            vmin: 电源电压输出最小值 (Unit: V)
            vmax: 电源电压输出最大值 (Unit: V)
        """
        if channel == 'Vtune':
            self.RsInst.write('SOUR:VOLT:CONT:LEV:LIM:LOW ' + str(vmin))
            self.RsInst.write('SOUR:VOLT:CONT:LEV:LIM:HIGH ' + str(vmax))
            self.RsInst.write('SOUR:VOLT:CONT:LEV:AMPL ' + str(vset))

        if channel == 'Vaux':
            self.RsInst.write('SOUR:VOLT:AUX:LEV:LIM:LOW ' + str(vmin))
            self.RsInst.write('SOUR:VOLT:AUX:LEV:LIM:HIGH ' + str(vmax))
            self.RsInst.write('SOUR:VOLT:AUX:LEV:AMPL ' + str(vset))

        if channel == 'Vsupply':
            self.RsInst.write('SOUR:VOLT:POW:LEV:LIM:LOW ' + str(vmin))
            self.RsInst.write('SOUR:VOLT:POW:LEV:LIM:HIGH ' + str(vmax))
            self.RsInst.write('SOUR:VOLT:POW:LEV:AMPL ' + str(vset))

    def power_switch(self, channel: str, state: str):
        """
        改变fswp50的三个电源端口的输出状态
        如果要同时关闭一级电源和二级电源的话，推荐先关闭一级电源，然后再关闭二级电源，否则会报错。但即使报错，实际上一级电源也被关闭了。
        经测试：只要将三个二级电源全部关闭，则一级电源自动关闭，且一级电源面板不可用，所以此时对一级电源操作会报错
            channel:
                'Vtune': 配置Vtune端口
                'Vaux': 配置Vaux端口
                'Vsupply': 配置Vsupply端口
                'ALL': 同时配置Vtune、Vaux、Vsupply三个端口
                'DC': 配置一级电源（即总开关）
            state:
                'ON': 使能输出
                'OFF': 禁用输出
        """
        if channel == 'Vtune':
            self.RsInst.write('SOUR:VOLT:CONT:LEV ' + state)
        if channel == 'Vaux':
            self.RsInst.write('SOUR:VOLT:AUX:LEV ' + state)
        if channel == 'Vsupply':
            self.RsInst.write('SOUR:VOLT:POW:LEV ' + state)
        if channel == 'ALL':
            self.RsInst.write('SOUR:VOLT:CONT:LEV ' + state)
            self.RsInst.write('SOUR:VOLT:AUX:LEV ' + state)
            self.RsInst.write('SOUR:VOLT:POW:LEV ' + state)
        if channel == 'DC':
            self.RsInst.write('SOUR:VOLT ' + state)

    def set_display_update(self, mode:str):
        """
        当远程连接时，是否允许仪器面板实时更新
            mode:
                'ON'
                'OFF'
        """
        self.RsInst.write('')
    def mode_FTR_config(self, vtune_start: float, vtune_stop: float, sweep_pts: float, fix_source: str):
        """
        测试模式自动配置：频率调谐曲线扫描
        实现功能：自动配置到VCO Characteristic模式，只保留Frequency窗口，配置sweep source(Vtune)和fix source(可选)，其中fix source的参数不在该函数内配置，需要在此之前将电压配置好。该函数会自动打开二级电源开关，但不会自动打开一级电源开关。不会自动执行扫描。
            vtune_start: vtune扫描初始值 (Unit: V)
            vtune_stop: vtune扫描终止值 (Unit: V)
            sweep_pts: vtune扫描的点数
            fix_source:
                'Vaux': 选择Vaux作为fix source
                'Vsupply': 选择Vsupply作为fix source
        """
        self.RsInst.write_str_with_opc('*RST')
        self.RsInst.write('INST:SEL PNO')      #设置为PN测试界面
        self.RsInst.write('CONF:VCO:MEAS ON')  #设置为VCO Characteristic
        self.RsInst.write('LAY:WIND2:REM')  #移除窗口2
        self.RsInst.write('LAY:WIND3:REM')  #移除窗口3
        self.RsInst.write('LAY:WIND4:REM')  #移除窗口4

        self.power_config('Vtune', vtune_start, vtune_start, vtune_stop)

        self.RsInst.write('CONF:VCO:SWE:SOUR VTUN')    #选择VTUNE作为sweep source
        if fix_source == 'Vaux':   #配置fix source并开启（必须要配置fix source，否则fswp50无法进行扫参）
            self.RsInst.write('CONF:VCO:FIX:SOUR ' + 'VAUX')
            self.power_switch('Vaux', 'ON')
        if fix_source == 'Vsupply':
            self.RsInst.write('CONF:VCO:FIX:SOUR ' + 'VSUP')
            self.power_switch('Vsupply', 'ON')

        self.RsInst.write('SOUR:VOLT:POW:LEV:MODE VOLT')   #Select the type of output at the Vtune connector
        self.RsInst.write('CONF:VCO:SWE:STAR ' + str(vtune_start))
        self.RsInst.write('CONF:VCO:SWE:STOP ' + str(vtune_stop))
        self.RsInst.write('CONF:VCO:SWE:POIN ' + str(sweep_pts))

        self.RsInst.write('SOUR:VOLT:CONT:LEV ON')     #开启VTUNE电源; 要开启其他电源，只需要将CONT替换为AUX和POW即分别代表开启Vaux和Vsupply的电源
        # self.RsInst.write('SOUR:VOLT ON')  #开启总电源
        # fswp.write_str_with_opc('INIT:IMM')  #Run Single
        self.RsInst.write('INIT:CONT OFF')      #关闭Continuous Run
        self.wait()

    def get_signal_level(self):
        """
        获取Signal Level (Unit:dBm)
        """
        return self.RsInst.query_float('POW:RLEV?')

    def get_spot_PN(self, trace_index: int, offset: float):
        """
        抓取给定offset frequency的点噪值
            trace_index: 所抓取的曲线，1-6
            offset: offset frequency (Unit: Hz)。例如：1e6
        """
        start_freq = self.RsInst.query_float('FREQuency:STARt?')
        stop_freq = self.RsInst.query_float('FREQuency:STOP?')
        if offset < start_freq or offset > stop_freq:
            print("Offset is out of bound!")
            return

        self.RsInst.write('CALC:SNO:USER ON')
        self.RsInst.write('CALC:SNO1:STAT ON')     #User Defined marker 1 is used to get spot PN
        self.RsInst.write('CALC:SNO1:X ' + str(offset))
        spot_PN = self.RsInst.query('CALC:SNO1:TRAC' + str(trace_index) + ':Y?')
        self.RsInst.write('CALC:SNO:USER OFF')
        return float(spot_PN)

    def set_pow_max_current(self, max_current:float ):
        """
        设置Vsupply输出端口最大电流 (Unit: A)
        """
        self.RsInst.write('SOUR:CURR:POW:LIM:HIGH '+str(max_current))

    def get_spot_PN_dec(self, trace_index: int):
        """
        抓取整条PN曲线10^x处的spot phase noise
             trace_index: 所抓取的曲线，1-6
        """
        spot_PN = self.RsInst.query('CALC:SNO:TRAC' + str(trace_index) + ':DEC:Y?')
        spot_PN = spot_PN.split(",")
        # freq_start = fswp.query_float('FREQuency:STARt?')
        # freq_stop = fswp.query_float('FREQuency:STOP?')
        # freq = np.logspace(float(np.log10(freq_start)), float(np.log10(freq_stop)), len(spot_PN)).tolist()
        freq = self.RsInst.query('CALC:SNO:DEC:X?')
        freq = freq.split(",")

        return freq, spot_PN

    def run_single_wait(self):
        """
        执行run single，并等待完成
        """
        self.RsInst.write_str_with_opc('INIT:IMM')

    def get_freq(self):
        """
        获取当前的频率值
        """
        return float(self.RsInst.query('FREQ:CENT?'))

    def get_output_current(self):
        """
        获取fswp50三个电源输出端口的电流值 (Unit: A)
        返回值:
            [0]: Vsupply电流值
            [1]: Vtune电流值
            [2]: Vaux电流值
        """
        output_current = self.RsInst.query('SOUR:CURR:SEQ:RES?')
        output_current = output_current.split(",")
        return output_current

    def mode_PN_config(self, start_freq: float=10e3, stop_freq: float=100e6, xcorr: int=1000, rbw: int=1, att: int=-1):
        """
        将FSWP50设置为相噪测量模式，并自动配置常用参数
            start_freq: offset frequency初始值 (Unit: Hz)
            stop_freq: offset frequency终止值  (Unit: Hz)
            xcorr: XCORR Factor
            rbw: RBW (%)
            att: (Unit: dB)
                -1: 衰减设置为自动
        """
        self.RsInst.write_str_with_opc('*RST')
        self.RsInst.write('INST:SEL PNO')
        self.RsInst.write('INIT:CONT OFF')  #关闭Continuous Run
        self.RsInst.write('FREQ:STAR '+Conversions.decimal_value_to_str(start_freq))
        self.RsInst.write('FREQ:STOP '+Conversions.decimal_value_to_str(stop_freq))
        self.RsInst.write('SWE:XFAC '+str(xcorr))
        self.RsInst.write('LIST:BWID:RAT '+str(rbw))
        if att == -1:
            self.RsInst.write('INP:ATT:AUTO ON')
        else:
            self.RsInst.write('INP:ATT:AUTO OFF')
            self.RsInst.write('INP:ATT '+str(att))

    def screenshot_copy(self, inst_filename, pc_filename, format_photo: str='PNG'):
        """
        截图并传输到本地计算机上，图片不会在fswp50上保存
            inst_filename: 图片在fswp50上暂存的路径
            pc_filename: 图片在本地计算机的存储路径
            format: 图片格式
                'PNG'
                ‘JPG'
        """

        self.RsInst.write('HCOPy:DEVice:LANGuage '+format_photo)  # Select file format for screenshot (possible: PNG or JPG)
        self.RsInst.write(f'MMEMory:NAME {inst_filename}')  # Define path and name for the screenshot on the instrument
        self.RsInst.write('HCOPy:IMMediate')  # Perform screenshot and save it on the analyzer
        # Transfer file to PC
        self.RsInst.data_chunk_size = 10000
        self.RsInst.query_bin_block_to_file(f'MMEMory:DATA? {inst_filename}', f'{pc_filename}', append=False)
        self.RsInst.write(f'MMEMory:DELete {inst_filename}')  # And delete it on the instrument


