#!/usr/bin/env python

import pyvisa as visa
import time
import Module_Error_Code as m_err
import Module_Exception_Trigger as m_excep_trigger


class Visa_Process():

    def __init__(self):
        self.resources_list = []
        self.rm_handler = None
        self.conn_instrument_instance = None
        self.instr_name =""
        self.instr_address=""
        self.timeout_ms = 5000

    @m_excep_trigger.try_except
    def instrument_available_list(self):
        obj_rm = visa.ResourceManager()
        self.resources_list = obj_rm.list_resources()

        return self.resources_list
    
    

 #   @m_excep_trigger.try_except
    def instrument_connection_config(self, obj_instrument_link, timeout_ms=5000):
        if obj_instrument_link !='0':
            self.rm_handler = visa.ResourceManager()
            self.resources_list = self.rm_handler.list_resources()
            self.timeout_ms = timeout_ms
            self.instr_address = obj_instrument_link
            self.timeout_ms = timeout_ms
            res = self.open()



        else:
            res = m_err.Err_fail

        return res

    @m_excep_trigger.try_except
    def open(self):
        #get instrument handler, test if link is ok with cmd *IDN? 
        self.conn_instrument_instance = self.rm_handler.open_resource(self.instr_address)
        self.conn_instrument_instance.timeout = self.timeout_ms
        self.instr_name = self.conn_instrument_instance.query('*IDN?')
        '''    
        #reset status
        init_cmd_lst = ['*RST', '*CLS', 'STAT:PRES', '*SRE 0', '*ESE 0']
        for cmd in init_cmd_lst:
            self.conn_instrument_instance.write(cmd)
            return m_err.Err_ok
        else:
            return m_err.Err_fail
        '''
    @m_excep_trigger.try_except
    def close(self):
        self.conn_instrument_instance.close()
        self.conn_instrument_instance = None
    
    @m_excep_trigger.try_except
    def visa_write(self, obj_visa_write_info):
        self.conn_instrument_instance.write(obj_visa_write_info)

        return m_err.Err_ok

    @m_excep_trigger.try_except
    def wait(self):
        while 1:
           result = self.conn_instrument_instance.query("*OPC?")   
           if int(result)== 1:
              break
           else:
              time.sleep(0.1)
        return 

if __name__ == '__main__':
    pass
