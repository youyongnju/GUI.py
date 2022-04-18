import configparser
#读ini文件
def rem_space(value):
    for i in range(len(value)):
        value[i] = value[i].strip()     #去列表内字符串空格
        if value[i]== '':
            value.pop(i)
    return value

config = configparser.ConfigParser() # 类实例化
path = 'config.ini'
config.read(path,encoding='UTF-8')
mode = config.get('Mode','mode').split(',')
rem_space(mode)
for i in mode:
    if i=='WCDMA':
        import CMW500_measure_WCDMA
        CMW500_measure_WCDMA.WCDMA()

    elif i=='LTE':
        import CMW500_measure
        CMW500_measure.LTE()
