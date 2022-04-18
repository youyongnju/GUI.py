#sys.path.append("../../")
import time
import datetime
import visa
import math
import xlwt
import csv
import codecs
import pandas as pd
visa_dll = 'c:/windows/system32/visa32.dll'
from Agilent_MultiMeter_3446x  import *

def data_write_csv(file_name, datas):# file_name为写入CSV文件的路径，datas为要写入数据列表 
    file_csv = codecs.open(file_name,'w+','utf-8')#追加   
    writer = csv.writer(file_csv, delimiter=' ', quotechar=' ', quoting=csv.QUOTE_MINIMAL)   
    i = 0    
    for data in datas:        
        writer.writerow(str(data))          
    print("保存文件成功，处理结束")

if __name__ == '__main__':
    inst_addr_volt = "192.168.105.31"
    Meter_3446x_Instr_volt = Agilent_MultiMeter_3446x(inst_addr_volt, addr_type="LAN", series="3446x")
    Meter_3446x_Instr_volt.mode_preset
    #Meter_3446x_Instr.mode_config(mode='VOLT')
    Meter_3446x_Instr_volt.set_config(1)
    Meter_3446x_Instr_volt.set_Measure(1,2,'V0')
    record_volt = []

    inst_addr_volt = "192.168.105.17"
    Meter_3446x_Instr_current = Agilent_MultiMeter_3446x(inst_addr_volt, addr_type="LAN", series="3446x")

     .mode_preset
    Meter_3446x_Instr_current.set_config(2)
    Meter_3446x_Instr_current.set_Measure(2, 2, 'i3')


    record_current = []
    for eachitem in range(1,60*10):
        #test voltage
        data_volt = Meter_3446x_Instr_volt.Read_DC_Volt(meas_range=10)
        record_volt.append(data_volt)
        #print('the %d th test volt is:' %eachitem, data_volt)

        #test current
        data_current = Meter_3446x_Instr_current.sample_curr(1)
        data_current_list = (data_current.split('\n')[0])

        record_current.append(float(data_current))
        print('the %s th test volt is: , current is:' %eachitem, data_volt, data_current_list)
        #print('the %s th test volt is: %s, current is:%s' %eachitem ,data_volt,data_current_list)

        time.sleep(0.1)
    time.sleep(2)
    df_v = pd.DataFrame(record_volt)
    time.sleep(2)
    df_v.to_csv(r"test_volt_ifly_1.csv")
    time.sleep(2)
    df_i = pd.DataFrame(record_current)
    time.sleep(2)
    df_i.to_csv(r"test_current_ifly_1.csv")

        
     









