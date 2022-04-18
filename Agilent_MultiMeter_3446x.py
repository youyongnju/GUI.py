import os
import re
import sys

sys.path.append("../../")
import time
import visa
import math
#import Lib.Utils.Module_Error_Code as m_err
from csv import writer
import matplotlib.pyplot as plt
import numpy as np
#import Lib.Utils.Module_Exception_Trigger as m_execption
from Visa_Process import *


class Agilent_MultiMeter_3446x(Visa_Process):

    def __init__(self, inst_addr = '169.254.4.61', addr_type="LAN", series="3446x"):
        super(Agilent_MultiMeter_3446x, self).__init__()
        self.instrument_connection_config(obj_instrument_link=inst_addr, link_type=addr_type, timeout_ms=5000)

        self.Meter_3446x = self.conn_instrument_instance
        self.mode_preset()
        self.Max_Output_Voltage_V = 15
        self.Max_Output_Current_A = 3
        self.Series = series
        self.OCP = 2
        self.OVP = 15


    def mode_preset(self):
        ini = ['*RST', '*CLS', 'STAT:PRES', '*SRE 0', '*ESE 0']
        for i in ini:
            self.Meter_3446x.write(i)#initialize the pwr source

    def set_config(self, config_sel, *config_form_range): #config_sel:  1: Volt, 2: Curr, 3: resistance, 4: diode, 5: capacitance, 6: temperature
        config_dict = {1: 'CONFigure:VOLTage', 2: 'CONFigure:CURRent', 3: 'CONFigure:RESistance',
                       4: 'CONFigure:DIODe', 5: 'CONFigure:CAPacitance', 6: 'CONFigure:TEMPerature'}
        if len(config_form_range) >= 1:
            self.Meter_3446x.write(config_dict[config_sel] + config_form_range[0])
        else:
            self.Meter_3446x.write(config_dict[config_sel])

    def mode_config(self,mode='VOLT'):
        if mode.upper() == 'VOLT':
           self.set_config(1)
        elif mode.upper() =='CURR':    
           self.set_config(2)
        else:
           self.set_config(1)
        return

    def set_Measure(self, config_sel, form=2, range='V0'):
        form_dict = {1: 'AC? ', 2: 'DC? ', 3: '? '}
        Meas_dict = {1: 'MEASure:VOLTage:', 2: 'MEASure:CURRent:', 3: 'MEASure:RESistance',
                     4: 'MEASure:DIODe', 5: 'MEASure:CAPacitance', 6: 'MEASure:TEMPerature'}
        range_dict = {'V0': '10', 'V1': '10','V2': '10',
                      'i0': 'AUTO', 'i1': '100mA', 'i2': '1A', 'i3': '3A',
                      'r0': 'AUTO', 'r1': '100', 'r2': '1k', 'r3': '10k', 'r4': '100k', 'r5': '1M',
                      'r6': '10M', 'r7': '100M', 'r8': '1G',
                      'c0': 'AUTO', 'c1': '1nf', 'c2': '10nf', 'c3': '100nf', 'c4': '1uf',
                      'c5': '10uf', 'c6': '100uf',
                      'd0': '',
                      't0': ''}
        meas_str = self.Meter_3446x.query(Meas_dict[config_sel] + form_dict[form] + range_dict[range])
        meas_data = float(meas_str)
        return(meas_data)


    def Measure_DC_Volt(self,range='V0'):
        form=2
        config_sel =1
        return self.set_Measure(config_sel, form, range)

    def Read_DC_Volt(self,meas_range=1,resolution =1e-6, auto_impedance='off'):
        self.Meter_3446x.write("CONF:VOLT:DC %d, %f"%(meas_range,resolution))
        if auto_impedance.lower()=='off':
            self.Meter_3446x.write("INP:IMP:AUTO OFF")
        else:    
            self.Meter_3446x.write("INP:IMP:AUTO ON")
        
        self.Meter_3446x.write("ZERO:AUTO ON")
        #self.Meter_3446x.write("PER:APER 0.1")
        self.Meter_3446x.write("VOLT:DC:NPLC 10")

        self.Meter_3446x.write("TRIG:SOUR IMM")
        #meas_str = self.Meter_3446x.query("Read?")
        meas_str = self.Meter_3446x.query("Read?")
        meas_data = float(meas_str)
        return(meas_data)

    def Measure_DC_Curr(self,range='i0'):
        form=2
        config_sel = 2
        return self.set_Measure(config_sel, form, range)

    def sample_curr(self, sample_num_arg):
        retval = []
        self.Meter_3446x.write("CONF:CURR:DC 0.1,3E-7")# make certain accuracy of config, otherwise the sampling will be so lagging
        # self.Meter_3446x.write("SAMP:SOUR TIM")
        self.Meter_3446x.write("TRIG:SOUR BUS")
        # self.Meter_3446x.write("TRIG:COUNT 1")
        # self.Meter_3446x.write("TRIG:DEL 0.1")
        # self.Meter_3446x.write("SAMP:TIM 11")
        self.Meter_3446x.write('TRIG:DEL:AUTO OFF')  # turn trigger delay off
        # self.Meter_3446x.write("TRIG:DEL 0.00014")
        self.Meter_3446x.write("SAMP:SOUR TIM")# set the sampling source as TIMER
        self.Meter_3446x.write("SAMP:TIM 0.0003") # set the internal sample time(the time between two sample points) as 0.0003 seconds
        self.Meter_3446x.write('ZERO:AUTO OFF')
        self.Meter_3446x.write("SAMP:COUN " + str(sample_num_arg))

        self.Meter_3446x.write("INIT")
        # time.sleep(10)
        # self.Meter_3446x.write("SAMP:TIM?")
        self.Meter_3446x.write("*TRG")
        # time.sleep(4)
        # self.Meter_3446x.write("INIT")
        # ret_time = self.Meter_3446x.query('SAMPle:TIMer?')
        # print(ret_time)
        # time.sleep(3)
        retval = self.Meter_3446x.query("FETC?", delay = 0.1)
        # print(type(retval))
        # print(retval)
        return(retval)

        # self.Meter_3446x.write("SAMP:COUN:PRET 5000")
        # self.Meter_3446x.write("TRIG:SOUR INT")
        # self.Meter_3446x.write("TRIG:LEV 0.0005")

        # self.Meter_3446x.write("TRIG:SOUR INT")
        # self.Meter_3446x.write("TRIG:LEV 0.005")
        # self.Meter_3446x.write("TRIG:SLOP POS")


if __name__ == '__main__':
    inst_addr = "192.168.105.17"
    Meter_3446x_Instr = Agilent_MultiMeter_3446x(inst_addr, addr_type="LAN", series="3446x")
    for i in range(4):
        plt.figure(i)
        # config_sel_arg = 6 #configure the form of measurment
        # form_arg = 3 # AC or DC
        # range_arg = 't0' #sel the range of measurement
        Meter_3446x_Instr.mode_preset()
        sample_count = 50000
        sample_val = Meter_3446x_Instr.sample_curr(sample_count)
        sample_val_list = sample_val.split(",")
        sample_val_len = len(sample_val_list)
        print(sample_val_len)
        sample_val_float_list = []
        for eachitem in sample_val_list:
            eachitem_float = abs(round(float(eachitem)*1000, 5))
            sample_val_float_list.append(eachitem_float)

        x = np.linspace(0, sample_count*0.0003, sample_count)
        y = sample_val_float_list
        print(y[10])
        plt.plot(x, y)
        plt.grid()
        time.sleep(1)


    plt.show()
    Meter_3446x_Instr.close()
    # print(read_val)
    # Meter_3446x_Instr.sample_curr_trig()
    # Meter_3446x_Instr.mode_preset()
    # Meter_3446x_Instr.set_config(config_sel_arg)
    # Meter_3446x_Instr.set_Measure(config_sel_arg, form_arg, range_arg)
    # Meter_3446x_Instr.close()
