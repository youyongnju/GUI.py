from INST_CMW500_WCDMA import *
from Agilent_DCsource_66XX import *
from readini_writexls_WCDMA import *
import copy

def WCDMA():
    test_band, CMW_addr, Agilent_66XX_addr, volt, trace_loss, margin, channel, data=readini()
    print('Test band is band',test_band)
    sharedata.content.append('Test band is ')
    for i in range(len(test_band)):
        sharedata.content.extend(test_band[i]+' ')
    sharedata.content.append('\n')
    print('cmw adress is',CMW_addr)
    sharedata.content.append('cmw adress is' + CMW_addr + '\n')
    print('current meter adress is',Agilent_66XX_addr)
    sharedata.content.append('current meter adress is'+Agilent_66XX_addr+'\n')
    #volt=readini_writexls_WCDMA.volt
    #channel=readini_writexls_WCDMA.channel
    #trace_loss = readini_writexls_WCDMA.trace_loss
    #data=copy.deepcopy(readini_writexls_WCDMA.data)     #必须用深拷贝，不能用=直接复制，=是引用





    #测试流程。。。。。。。。。。。。。。。。。
    start = time.time()  # start time of program
    CMW = INST_CMW500_WCDMA(CMW_addr)
    if Agilent_66XX_addr!='0':
        DC_Source = Agilent_DCsource_66XX(Agilent_66XX_addr)
        DC_Source.config_volt_current('3.8')

    if sharedata.reset==1 :
        CMW.mode_preset()
        if Agilent_66XX_addr != '0':
            DC_Source.mode_preset()
            DC_Source.config_volt_current('3.8')
    CMW.config_DL_level(-70)
    CMW.TRX_port_config('RF1C')
    CMW.config_Band_channel(test_band[0])
    CMW.switch_on_cmw()
    CMW.setup_connection()
    CMW.CMW_MEAS_rep('CONT')
    CMW.meas_condition_on()



    # 生成测试数据存在data字典

    #初始化data
    for k in volt:
        if Agilent_66XX_addr != '0':
            DC_Source.config_volt_current(k)
        else:
            print('请设置电压' + k + 'V后按回车\n')
            win32api.MessageBox(win32con.NULL, '请设置电压' + k + 'V后按回车','', win32con.MB_OK | win32con.MB_ICONINFORMATION)
        volt_bandwidth = k + 'V'
        for j in range(len(channel[volt_bandwidth])):
            CMW.CMW_TPC('MAXP')
            CMW.TRX_ext_atten(trace_loss[j//3])
            CMW.config_Band_channel(test_band[j//3],channel[volt_bandwidth][j])
            CMW.meas_condition_on()#一定要加不然功率容易读不出来
            aclr = CMW.meas_aclr('CURR')
            aclr_1 = aclr.split(',')
            for i in range(2,6):
                aclr_1[i]= eval(aclr_1[i])-eval(aclr_1[1])#绝对值转换成相对值
            data[volt_bandwidth].append(aclr_1[1:6])
            #aclr里面的功率和ue power有偏差，所以重测
            power=CMW.meas_power()
            data[volt_bandwidth][j][0]=eval(power[2:15])
            if Agilent_66XX_addr != '0':
                #time.sleep(1)
                Curr1 = DC_Source.meas_current()
                data[volt_bandwidth][j].append(Curr1)
                CMW.CMW_TPC('MINP')
                #time.sleep(1)
                Curr2 = DC_Source.meas_current()
                data[volt_bandwidth][j].append(Curr2)
                delta_curr=Curr1-Curr2
                data[volt_bandwidth][j].append(delta_curr)


    writexls(data)






    #CMW.switch_off_cmw()  # close CMW500_WCDMA
    #DC_Source.DCsource_close()

    CMW.close()  # visa close
    if Agilent_66XX_addr != '0':
        DC_Source.close()



    end = time.time()
    print('Total test time is about %s seconds' % round((end-start),3))
    sharedata.content.append('Total test time is about '+ str(end-start)[0:4]+' seconds\n\n')
    sharedata.command=1
    #input('测试完成。。。。。。。。。。。。')