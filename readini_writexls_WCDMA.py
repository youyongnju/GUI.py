import configparser
import time
import xlwt,xlrd

def readini():
    #读ini文件
    def rem_space(value):
        for i in range(len(value)):
            value[i] = value[i].strip()     #去列表内字符串空格
            if value[i]== '':
                value.pop(i)
        return value

    config = configparser.ConfigParser() # 类实例化
    path = 'config.ini'
    config.read(path,encoding='utf-8')
    test_band = config.get('WCDMA','band').split(',')
    rem_space(test_band)
    CMW_addr=config.get('Instrument','CMW Adress').split(',')
    rem_space(CMW_addr)
    CMW_addr=CMW_addr[0]
    Agilent_66XX_addr=config.get('Instrument','Current Meter Adress').split(',')
    rem_space(Agilent_66XX_addr)
    Agilent_66XX_addr=Agilent_66XX_addr[0]
    volt=config.get('Volt','Volt').split(',')
    rem_space(volt)
    trace_loss=[]
    for i in range(len(test_band)):
        trace_loss.append(config.get('Trace loss','band'+test_band[i]))
    margin=config.get('WCDMA','margin').split(',')
    rem_space(margin)
    margin=margin[0]





    '''
    aclr = '23,-40,-35,-36,-41,600,145,455'
    aclr_1 = aclr.split(',')
    '''

    #初始化字典
    channel,data={},{}

    for k in volt:
        channel[k + 'V'] =[]
        data[k + 'V'] = []



    #生成channel字典
    for k in volt:

           for j in test_band:

                  ch=config.get('WCDMA', 'band'+str(j)).split(',')
                  channel[k+'V'].extend(ch[0:3])

                  #单个字符串用append， 字符串列表用extend
    return  test_band,  CMW_addr,Agilent_66XX_addr, volt,trace_loss,margin,channel,data



    '''
    #生成测试数据存在data字典
    for k in volt:
    
            volt_bandwidth = k + 'V'
            for j in range(len(channel[volt_bandwidth])):
              # aclr_1=dl_channel[volt_bandwidth][j]
                data[volt_bandwidth].append(aclr_1)
    '''




#写excel。。。。。。。。。。。。。。。。。
#if __name__=='__main__':
def writexls(data):

    test_band,  CMW_addr,Agilent_66XX_addr, volt,trace_loss,margin,channel,data1=readini()

    start = time.time()  # start time of program
    now = time.strftime("%Y%m%d_%H_%M_%S", time.localtime(time.time()))
    fname = 'ACLR'+'_Report_' + now + '.xls'

    header = ['Band', 'Channel', 'TX Power', 'ACLR-10', 'ACLR-5', 'ACLR+5','ACLR+10', \
             'Current(max)', 'Current(min)', 'Current(PA)']

    f = xlwt.Workbook()

    for k in volt:
            volt_bandwidth = k + 'V'
            sheet1 = f.add_sheet(volt_bandwidth, cell_overwrite_ok=True)

            #设置单元格格式
            alignment = xlwt.Alignment() # Create Alignment
            alignment.horz = xlwt.Alignment.HORZ_CENTER # May be: HORZ_GENERAL, HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED, HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
            alignment.vert = xlwt.Alignment.VERT_CENTER # May be: VERT_TOP, VERT_CENTER, VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED
            style = xlwt.XFStyle() # Create Style
            style.alignment = alignment # Add Alignment to Style
            style.num_format_str = '0'

            # 写第一行
            for j in range( len(header)):
                sheet1.write(0, j , header[j],style)
            #写band
            for j in range(len(test_band)):
                sheet1.write_merge(j*3+1, j*3+3, 0, 0, float(test_band[j]),style)
            #写channel
            for j in range(len(channel[volt_bandwidth])):
                sheet1.write(j+1, 1 , float(channel[volt_bandwidth][j]),style  )
            style.num_format_str = '0.0'
            #写data
            for j in range(len(data[volt_bandwidth])):
                for m in range(len(data[volt_bandwidth][j])):
                    sheet1.write(j+1, m+2 , float(data[volt_bandwidth][j][m]) ,style)
            #设列宽
            '''
            for j in range( len(header)):
                sheet1.col(j).width = len(header[j]) * 250
                if len(header[j])<9:
                    sheet1.col(j).width = 8*300
            '''
            for j in range( len(header)):
                sheet1.col(j).width = 8 * 340

            #margin不足标红
            pattern = xlwt.Pattern()
            pattern.pattern = xlwt.Pattern.SOLID_PATTERN
            pattern.pattern_fore_colour = xlwt.Style.colour_map['red']
            style.pattern = pattern
            for j in range(len(data[volt_bandwidth])):
                if float(data[volt_bandwidth][j][1])>-35.2-eval(margin[0]):
                    sheet1.write(j+1, 1+2 , float(data[volt_bandwidth][j][1]) ,style)
                if float(data[volt_bandwidth][j][2])>-32.2-eval(margin[0]):
                    sheet1.write(j+1, 2+2 , float(data[volt_bandwidth][j][2]) ,style)
                if float(data[volt_bandwidth][j][3])>-32.2-eval(margin[0]):
                    sheet1.write(j+1, 3+2 , float(data[volt_bandwidth][j][3]) ,style)
                if float(data[volt_bandwidth][j][4])>-35.2-eval(margin[0]):
                    sheet1.write(j+1, 4+2 , float(data[volt_bandwidth][j][4]) ,style)

    f.save(fname)

#writexls(data)
