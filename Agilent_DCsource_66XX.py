import os
import re
import sys
import sharedata
sys.path.append("../../")
import time

from Visa_Process import *


class Agilent_DCsource_66XX(Visa_Process):

    def __init__(self, inst_addr = 'GPIB0::5::0::INSTR'):
        super(Agilent_DCsource_66XX, self).__init__()
        self.instrument_connection_config(obj_instrument_link=inst_addr, timeout_ms=5000)
        #self.instr_address=inst_addr
        #self.open()
        self.DCsource_66XX = self.conn_instrument_instance
        #self.mode_preset()
        self.Max_Output_Voltage_V = 15
        self.Max_Output_Current_A = 3
        #self.Series = series

    def mode_preset(self):
        ini = ['*RST', '*CLS', 'STAT:PRES', '*SRE 0', '*ESE 0']
        for i in ini:
            self.DCsource_66XX.write(i) # initialize the pwr source

    def config_volt_current(self,volt):
        cur_max = '3'
        self.DCsource_66XX.write('VOLTage ', volt)
        self.DCsource_66XX.write('CURRent ', cur_max)
        print('the voltage configuration is ', volt)
        sharedata.content.append('the voltage configuration is '+volt+'V\n')
        self.DCsource_66XX.write('OUTPut ON')
        idn = self.DCsource_66XX.query('*IDN?')
        print('%s is existed!' %(idn[0:len(idn)-2]))
        sharedata.content.append(idn[0:len(idn)-2]+' is existed!\n')

    def meas_current(self,measure_times=30):
        curr=[]
        for i in range(measure_times):

            current_meas = self.DCsource_66XX.query('MEASure:CURRent?')
            curr.append( round(float(current_meas[0:len(current_meas)-1]), 3)*1000)
        curr_min=min(curr)#测试10次取最小的电流值
        print('the current measured is %dmA' % curr_min)
        sharedata.content.append('the current measured is '+str(curr_min)+' mA\n')
        return curr_min

    def meas_volt(self):
        volt_meas = self.DCsource_66XX.query('MEASure:VOLT?')
        volt = round(float(volt_meas[0:len(volt_meas)-1]),3)
        print('the voltage measured is %3.2fV' % volt)
        sharedata.content.append('the voltage measured is '+str(volt)+'V\n')
        return volt


    def DCsource_close(self):
        self.DCsource_66XX.write('OUTPut OFF')
        status = self.DCsource_66XX.query('OUTP?')
        status_conn = status.split()[0]
        if status_conn == '0':
            print('DC Source is closed!')
            sharedata.content.append('DC Source is closed!\n')
        else:
            print('DC Source is still on, please close DC Source!')
            sharedata.content.append('DC Source is still on, please close DC Source!\n')



if __name__ == '__main__':
    inst_addr = "192.168.105.17"
    DCsource_66XX_Instr = Agilent_DCsource_66XX(inst_addr)

    DCsource_66XX_Instr.mode_preset()

    DCsource_66XX_Instr.DCsource_close()

