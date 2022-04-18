import tkinter as tk  # 使用Tkinter前需要先导入
import sharedata
import _thread


if __name__=='__main__':
    # 第1步，实例化object，建立窗口window
    window = tk.Tk()

    # 第2步，给窗口的可视化起名字
    window.title('自动测试系统_____________SmarterMicro:YouYong')

    # 第3步，设定窗口的大小(长 * 宽)
    window.geometry('800x550+400+100')  # 这里的乘是小x+500 +400 定义窗口弹出时的默认展示位置

    # 第7步，创建并放置一个多行文本框text用以显示，指定height=3为文本框是三个字符高度
    t = tk.Text(window, width=500,height=30)
    t.pack()
    t.insert('end', '开始测试前请先修改config配置文件\n')



    def reset():
        if var1.get()==1:
            sharedata.reset=1
        elif var1.get()==0:
            sharedata.reset=0
    var1 = tk.IntVar()  # 定义var1和var2整型变量用来存放选择行为返回值
    c1 = tk.Checkbutton(window, text='RESET', variable=var1, onvalue=1, offvalue=0,command=reset)
    c1.select()
    # 传值原理类似于radiobutton部件
    c1.pack()




    def  b1():
        def LTE():
            sharedata.command=0

            import CMW500_measure
            CMW500_measure.LTE()

        _thread.start_new_thread(LTE,())
    def b2():
        def WCDMA():
            sharedata.command=0

            import CMW500_measure_WCDMA
            CMW500_measure_WCDMA.WCDMA()

        _thread.start_new_thread(WCDMA, ())

    b1 = tk.Button(window, text='LTE', width=20, height=4, command=b1)
    b1.place(x=180, y=420)

    b2 = tk.Button(window, text='WCDMA', width=20, height=4, command=b2)
    b2.place(x=460, y=420)












    a2=0
    def refreshText():
        global a2
        a1=len(sharedata.content)
        for i in range(a2,a1):
            t.insert('end', sharedata.content[i])
            t.see('end')
        a2=len(sharedata.content)
        if sharedata.command==1:#开关是否暗掉
            b1.config(state='normal')
            b2.config(state='normal')

        elif sharedata.command==0:
            b1.config(state='disabled')
            b2.config(state='disabled')

        window.after(100, refreshText)#100ms嵌套刷新text一次


    #refreshText()
    _thread.start_new_thread(refreshText,())







    # 第8步，主窗口循环显示
    window.mainloop()
