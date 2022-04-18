from INST_CMW500 import *
from Agilent_DCsource_66XX import *
from readini_writexls import *
import sharedata
import win32api   #winapi库
import win32con   #windows常数定义
import copy

def LTE():
    #读readini_writexls里的参数
    test_band, test_bandwidth, CMW_addr,Agilent_66XX_addr, volt,trace_loss,RB,margin,channel,dl_channel,data=readini()
    #test_band=readini_writexls.test_band
    print('Test band is band',test_band)
    sharedata.content.append('Test band is ')
    for i in range(len(test_band)):
        sharedata.content.extend(test_band[i]+' ')
    sharedata.content.append('\n')
    #test_bandwidth = list(set([int(test_bandwidth_info[i]) for i in range(len(test_bandwidth_info))]))  # [5,10,15,20]
    #test_bandwidth=readini_writexls.test_bandwidth
    print('Test bandwidth is ',test_bandwidth,'MHz')
    sharedata.content.append('Test bandwidth is ')
    for i in range(len(test_bandwidth)):
        sharedata.content.extend(test_bandwidth[i]+' ')
    sharedata.content.append('\n')   
    print('cmw adress is ',CMW_addr)
    sharedata.content.append('cmw adress is '+CMW_addr+'\n')
    print('current meter adress is',Agilent_66XX_addr)
    sharedata.content.append('current meter adress is '+Agilent_66XX_addr+'\n')
    #volt=readini_writexls.volt
    #dl_channel=readini_writexls.dl_channel
    #trace_loss = readini_writexls.trace_loss
    #data=copy.deepcopy(readini_writexls.data)     #必须用深拷贝，不能用=直接复制，=是引用

    def exchange_ACLR(aclr_1):   #修改aclr1里power和aclr顺序
        aclr_2 = []
        aclr_2.append(aclr_1[4])
        aclr_2.extend(aclr_1[1:])
        aclr_2.pop(4)
        return (aclr_2)


    #测试流程。。。。。。。。。。。。。。。。。
    start = time.time()  # start time of program
    CMW = INST_CMW500(CMW_addr)

    if Agilent_66XX_addr!='0':
        DC_Source = Agilent_DCsource_66XX(Agilent_66XX_addr)
        #DC_Source.mode_preset()
        DC_Source.config_volt_current('3.8')

    if sharedata.reset==1 :
        CMW.mode_preset()
        '''
        if Agilent_66XX_addr != '0':
            DC_Source.mode_preset()
            DC_Source.config_volt_current('3.8')
        '''

    CMW.config_DL_level(-70)
    CMW.TRX_port_config('RF1C')
    CMW.DL_mode(test_band[0])
    CMW.config_Band_channel(test_band[0])
    CMW.switch_on_cmw()
    CMW.setup_connection()
    CMW.meas_condition_on()
    CMW.CMW_trig_source('FrameTrigger')
    CMW.CMW_MEAS_rep('CONT')

    # 生成测试数据存在data字典
    for k in volt:
        if Agilent_66XX_addr != '0':
            DC_Source.config_volt_current(k)
        else:
            win32api.MessageBox(win32con.NULL, '请设置电压' + k + 'V后按回车','', win32con.MB_OK | win32con.MB_ICONINFORMATION)

        for i in test_bandwidth:
            volt_bandwidth = k + 'V_' + i + 'M'
            for j in range(len(dl_channel[volt_bandwidth])):
                if  eval(dl_channel[volt_bandwidth][j]) <=0:  #处理band8没有20M
                    data[volt_bandwidth].append([])
                    continue

                CMW.CMW_TPC('MAXP')
                CMW.TRX_ext_atten(trace_loss[j//3])
                CMW.intra_handover(test_band[j//3],dl_channel[volt_bandwidth][j],i)

                if RB=='fullRB':
                    CMW.config_RB(i, RB, 'LOW')  # 测试fullRB
                    CMW.meas_condition_on()
                    aclr = CMW.meas_aclr('CURR')
                    aclr_1 = aclr.split(',')
                    aclr_1=exchange_ACLR(aclr_1)
                    data[volt_bandwidth].append(aclr_1)
                else:
                    CMW.config_RB(i, RB, 'LOW')   #测试partialRB
                    CMW.meas_condition_on()
                    aclr = CMW.meas_aclr('CURR')
                    aclr_1 = aclr.split(',')
                    aclr_1 = exchange_ACLR(aclr_1)
                    data[volt_bandwidth].append(aclr_1)#列表开始是空列表所以不能用data[volt_bandwidth][j]

                    CMW.config_RB(i, RB, 'HIGH')
                    aclr = CMW.meas_aclr('CURR')
                    aclr_1 = aclr.split(',')
                    aclr_1 = exchange_ACLR(aclr_1)
                    data[volt_bandwidth][j].extend(aclr_1)



                #测电流
                if Agilent_66XX_addr != '0':
                    if RB == 'fullRB':
                        CMW.config_RB(i, RB, 'LOW')
                        #time.sleep(1)
                        Curr1 = DC_Source.meas_current()
                        data[volt_bandwidth][j].append(Curr1)
                        CMW.CMW_TPC('CLO','-40')
                        #time.sleep(1)
                        Curr2 = DC_Source.meas_current()
                        data[volt_bandwidth][j].append(Curr2)
                        delta_curr=Curr1-Curr2
                        data[volt_bandwidth][j].append(delta_curr)

                    if RB != 'fullRB':
                        CMW.config_RB(i, RB, 'LOW')
                        #time.sleep(1)
                        Curr1 = DC_Source.meas_current()
                        data[volt_bandwidth][j].append(Curr1)
                        CMW.CMW_TPC('CLO','-40')
                        #time.sleep(1)
                        Curr2 = DC_Source.meas_current()
                        data[volt_bandwidth][j].append(Curr2)
                        delta_curr=Curr1-Curr2
                        data[volt_bandwidth][j].append(delta_curr)

                        CMW.config_RB(i, RB, 'HIGH')
                        CMW.CMW_TPC('MAXP')
                        time.sleep(1)
                        Curr1 = DC_Source.meas_current()
                        data[volt_bandwidth][j].append(Curr1)
                        CMW.CMW_TPC('CLO','-40')
                        #time.sleep(1)
                        Curr2 = DC_Source.meas_current()
                        data[volt_bandwidth][j].append(Curr2)
                        delta_curr=Curr1-Curr2
                        data[volt_bandwidth][j].append(delta_curr)



    writexls(data)






    #CMW.switch_off_cmw()  # close CMW500
    #DC_Source.DCsource_close()

    CMW.close()  # visa close
    if Agilent_66XX_addr != '0':
        DC_Source.close()



    end = time.time()
    print('Total test time is about %s seconds' % round((end-start),3))
    sharedata.content.append('Total test time is about '+ str(end-start)[0:4]+' seconds\n\n')
    sharedata.command=1
    #input('测试完成。。。。。。。。。。。。')