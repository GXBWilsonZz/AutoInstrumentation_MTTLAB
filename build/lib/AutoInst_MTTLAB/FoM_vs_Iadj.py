from RS_Instrument.fswp50 import *
from Labjack.Labjack_U3 import *

'''
扫Iadj，记录PN、功耗和FoM

'''



file = open(data_path + 'data.csv', 'w')  # Open file for writing
file.write("Iadj;Fvco;PN@100kHz;PN@1MHz;PN@10MHz;FoM@100kHz;FoM@1MHz;FoM@10MHz;Idc;Iidle\n")  # Write the headline

for Iadj in [1, 4, 8, 16, 32, 64, 128, 256]:
    d.writeRegister(6009, 1)
    sleep(0.005)
    writebit_dec([3], [5], 0)  # MODE1 3;MODE2 19;MODE3 5 MODE4 12
    writebit_dec([3], [2], 0)  # gm_sw
    writebit_dec([63], [6], 0)  # sca
    writebit_dec([0], [13], 0)  # I_adj
    writebit_dec([0], [1], 0)  # Imax
    writebit_dec([0], [3], 0)  # null
    d.writeRegister(6009, 1)
    sleep(0.005)

    fswp50_run_single()
    Iidle = float(fswp50_get_output_current()[0])

    d.writeRegister(6009, 1)
    sleep(0.005)
    writebit_dec([3], [5], 0)  # MODE1 3;MODE2 19;MODE3 5 MODE4 12
    writebit_dec([3], [2], 0)  # gm_sw
    writebit_dec([63], [6], 0)  # sca
    writebit_dec([Iadj], [13], 0)  # I_adj
    writebit_dec([0], [1], 0)  # Imax
    writebit_dec([0], [3], 0)  # null
    d.writeRegister(6009, 1)
    sleep(0.005)

    fswp50_run_single()
    Fvco = fswp50_get_freq()
    PN_100k = fswp50_get_spot_PN(1, 100e3)
    PN_1M = fswp50_get_spot_PN(1, 1e6)
    PN_10M = fswp50_get_spot_PN(1, 10e6)
    Idc = float(fswp50_get_output_current()[0]) - Iidle
    FoM_100k = -PN_100k + 20*np.log10(Fvco/100e3) - 10*np.log10(Idc*0.5/1e-3)
    FoM_1M = -PN_1M + 20*np.log10(Fvco/1e6) - 10*np.log10(Idc*0.5/1e-3)
    FoM_10M = -PN_10M + 20*np.log10(Fvco/10e6) - 10*np.log10(Idc*0.5/1e-3)
    print("Iadj = %d Fvco = %f, PN@1MHz = %f, PN@10MHz = %f, FoM@1MHz = %f, FoM@10MHz = %f, Idc = %f Iidle = %f" % (Iadj, Fvco, PN_1M, PN_10M, FoM_1M, FoM_10M, Idc, Iidle))
    file.write("%d;%f;%f;%f;%f;%f;%f;%f;%f;%f" % (Iadj, Fvco, PN_100k, PN_1M, PN_10M, FoM_100k, FoM_1M, FoM_10M, Idc, Iidle))
    file.write("\n")
    screen_copy(inst_filename, data_path+'Iadj_%d.png' % Iadj)
    trace_get(data_path+'PN_Iadj_%d.csv' % Iadj)
file.close()  # CLose the file