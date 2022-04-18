import os
import re
import sys
import win32api   #winapi库
import win32con   #windows常数定义
sys.path.append("../../")
from Visa_Process import *
import sharedata


class INST_CMW500_WCDMA(Visa_Process):
    def __init__(self, inst_addr = 'GPIB0::20::0::INSTR'):
        super(INST_CMW500_WCDMA, self).__init__()
        self.instrument_connection_config(obj_instrument_link=inst_addr,timeout_ms=5000)
        #self.instr_address=inst_addr
        #self.open()
        self.CMW500_WCDMA = self.conn_instrument_instance
        idn = self.CMW500_WCDMA.query('*IDN?')
        print('%s is existed!' %(idn[0:len(idn)-2]))
        sharedata.content.append(idn[0:len(idn)-2]+' is existed!\n')

    def mode_preset(self):
        ini = ['*RST', '*CLS']
        for i in ini:
            self.CMW500_WCDMA.write(i)  # initialize the pwr source

    def TRX_port_config(self, trport = 'RF1C'):
        self.CMW500_WCDMA.write('ROUTe:WCDMa:SIGN:SCENario:SCELl %s,RX1,%s,TX1' % (trport, trport))

    def TRX_ext_atten(self, atten = 1):
        ini = ['CONFigure:FDCorrection:DEACtivate RF1C','CONFigure:FDCorrection:ACTivate RF1C, \'Const_0p00dB\', RX','CONFigure:FDCorrection:ACTivate RF1C, \'Const_0p00dB\', TX']
        for i in ini:
            self.CMW500_WCDMA.write(i)
        self.CMW500_WCDMA.write('CONFigure:WCDMa:SIGN:RFSettings:CARRier:EATTenuation:INPut ', str(atten))
        self.CMW500_WCDMA.write('CONFigure:WCDMa:SIGN:RFSettings:CARRier:EATTenuation:OUTPut ', str(atten))

    def switch_on_cmw(self):
        self.CMW500_WCDMA.write('SOURce:WCDMa:SIGN:CELL:STATe ON')
        while True:
            status = self.CMW500_WCDMA.query('SOURce:WCDMa:SIGN:CELL:STATe:ALL?')
            if(status == "ON,ADJ\n"):
                print('CMW500_WCDMA signaling is ON!')
                sharedata.content.append('CMW500 LTE signaling is ON!\n')
                break

    def switch_off_cmw(self):
        self.CMW500_WCDMA.write('SOURce:WCDMa:SIGN:CELL:STATe OFF')
        status = self.CMW500_WCDMA.query('SOURce:WCDMA:SIGN:CELL:STATe?')
        if status[0:3] == 'OFF':
            print('CMW500_WCDMA signaling is OFF!')
            sharedata.content.append('CMW500 LTE signaling is OFF!\n')

        else:
            print('CMW500_WCDMA signaling is still ON, please switch off!')
            sharedata.content.append('CMW500 LTE signaling is still ON, please switch off!\n')


    def setup_connection(self):
        time.sleep(0.5)
        print('请开机')
        sharedata.content.append('请开机\n')

        while True:
            conn_status = self.CMW500_WCDMA.query('FETCh:WCDMa:SIGN:CSWitched:STATe?')
            if(conn_status == 'REG\n') or (conn_status == 'CEST\n'):
                break
        print('UE is connected to CMW500_WCDMA')
        sharedata.content.append('UE is connected to CMW500\n')
        self.CMW500_WCDMA.write('CALL:WCDMa:SIGN:CSWitched:ACTion CONNect')
        while True:
            conn_estability_status = self.CMW500_WCDMA.query('FETCh:WCDMa:SIGN:CSWitched:STATe?')
            if(conn_estability_status == 'CEST\n'):
                print('Connection Establish is OK!')
                sharedata.content.append('Connection Establish is OK!\n')
                break

    def config_DL_level(self, dl_level = -50):
        self.CMW500_WCDMA.write('CONFigure:WCDMa:SIGN:RFSettings:CARRier1:COPower ', str(dl_level))


    def config_Band_channel(self,band = '1', channel = '9750'):
        print('band '+band+'   channel '+channel)
        sharedata.content.append('band '+band+'   channel '+channel+'\n')
        self.CMW500_WCDMA.write('CONFigure:WCDMa:SIGN:CARRier:BAND OB', str(band))
        self.CMW500_WCDMA.write('CONFigure:WCDMa:SIGN:RFSettings:CARRier1:CHANnel:UL ', str(channel))
        time.sleep(2)






    def meas_condition_on(self):
        self.CMW500_WCDMA.write('ROUTe:WCDMa:MEAS:SCENario:CSPath '+ '\'WCDMA Sig1\' ' )
        self.CMW500_WCDMA.write('INIT:WCDMA:MEAS:MEValuation')


        while True:
            status = self.CMW500_WCDMA.query('FETCh:WCDMA:MEAS:MEValuation:STATe?')
            if status in ['RDY\n','RUN\n','ATT/n']:
                print('WCDMA Meas is ready!')
                sharedata.content.append('WCDMA Meas is ready!\n')
                break

    def CMW_trig_source(self, *args):
        if args[0] == 'FrameTrigger':
            self.CMW500.write('TRIG:LTE:MEAS:MEV:SOUR "WCDMA Sig1: FrameTrigger"')
        elif args[0] == 'TPC Trigger':
            self.CMW500.write('TRIG:LTE:MEAS:MEV:SOUR "WCDMA Sig1: TPC Trigger"')
        elif args[0] == 'Fast Sync':
            self.CMW500.write('TRIG:LTE:MEAS:MEV:SOUR "Free Run (Fast Sync)"')
        elif args[0] == 'No Sync':
            self.CMW500.write('TRIG:LTE:MEAS:MEV:SOUR "Free Run (No Sync)"')
        elif args[0] == 'IF Power':
            self.CMW500.write('TRIG:LTE:MEAS:MEV:SOUR "IF Power"')


    def CMW_MEAS_rep(self, *args):
        if args[0] == 'CONT':
            self.CMW500_WCDMA.write('CONF:WCDMA:MEAS:MEV:REP CONT')
        elif args[0] == 'SING':
            self.CMW500_WCDMA.write('CONF:WCDMA:MEAS:MEV:REP SING')


    def CMW_TPC(self,*args):
        if(len(args) == 1 and args[0]== 'MAXP'):
            self.CMW500_WCDMA.write('CONFigure:WCDMa:SIGN:UL:TPC:MODE A1S1; SET ALL1; SET ALL1')
        if(len(args) == 1 and args[0]== 'MINP'):
            self.CMW500_WCDMA.write('CONFigure:WCDMa:SIGN:UL:TPC:MODE A1S1; SET ALL0; SET ALL0')
        elif len(args) == 2 and args[0] == 'CLO':
            self.CMW500_WCDMA.write('CONFigure:WCDMa:SIGN:UL:TPC:MODE A1S1; SET CLOop; TPOWer  ', args[1])

    def meas_aclr(self, mode = 'AVER'):

        status = self.CMW500_WCDMA.query('FETCh:WCDMA:MEAS:MEValuation:STATe?')
        if status == 'RDY\n':
            pass
        if mode == 'AVER':
            aclr_meas = self.CMW500_WCDMA.query('FETCh:WCDMa:MEAS:MEValuation:SPECtrum:AVERage?')
        elif mode == 'CURR':
            aclr_meas = self.CMW500_WCDMA.query('FETCh:WCDMa:MEAS:MEValuation:SPECtrum:CURR?')

        # if ACLR test data can't get, will retest 50 times
        n = 0
        while aclr_meas.split(',')[1] == 'INV' and n < 30:
            if n>6:
                win32api.MessageBox(win32con.NULL, 'please restart the phone', '',
                                    win32con.MB_OK | win32con.MB_ICONINFORMATION)
            aclr_meas = self.CMW500_WCDMA.query('FETCh:WCDMa:MEAS:MEValuation:SPECtrum:AVERage?')
            time.sleep(2)
            n = n + 1
            print('ACLR retest the %dth time!' % n)
            sharedata.content.append('ACLR retest the'+str(n)+'th time!\n')

        if n >= 30:
            print('ACLR test fail, please double check!')
            sharedata.content.append('ACLR test fail, please double check!\n')
            return 0
        else:
            return aclr_meas

    def meas_evm(self):
        time.sleep(1)

    def meas_power(self):
        power=self.CMW500_WCDMA.query('FETCh:WCDMa:MEAS:MEValuation:TRACe:UEPower:AVERage?')
        return power

if __name__ == '__main__':
    inst_addr = "192.168.105.17"
    cmw = INST_CMW500_WCDMA(inst_addr)

    cmw.mode_preset()



