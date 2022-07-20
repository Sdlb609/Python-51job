from tkinter import *
from tkinter import messagebox
import re
import requests    
import csv   
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from queue import Queue
import threading
from lxml import etree
import json
import pymysql
import numpy as np
import time


mpl.use("TkAgg")
plt.rcParams['font.sans-serif']=['SimHei']

csv_path = './51job{}数据.csv'
# 数据库库名，表名
dbname = 'python_51'
tabname = 'python_51_job'
#数据库配置
db = pymysql.connect(host = 'localhost',
                port = 3306,
                user = 'root',
                password = '123456',
                )

# f = plt.Figure(figsize=(15, 8), dpi=100)
# f_plot = f.add_subplot(111)

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Accept-Language': 'zh-Hans-CN, zh-Hans;q=0.5'
    }
que = Queue(2)


# f = Figure(figsize=(15,8), dpi=100)
# # f_plot = f.add_subplot(111)
# f_plot =plt.subplot(111)

# global name_list
name_list = []

def req_job_search():
    global name_list

    gangwei = entry_1.get()
    if gangwei == '':
        messagebox.showinfo('提示','请先输入搜索内容！')

    else: 
        # global name_list       
        name_list = []
        #先判定下页码的最大值
        url = f'https://search.51job.com/list/000000,000000,0000,00,9,99,{gangwei},2,1.html?lang=c&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&ord_field=0&dibiaoid=0&line=&welfare='
        req = requests.get(url, headers=headers)
        req.encoding = 'gbk' 
        req = req.text
        pages = int(re.findall('"total_page":"(.*?)",',req)[0])
        
        if pages > 2 :
            pages = 2
        for page in range(1,pages+1):
            url_put = f'https://search.51job.com/list/000000,000000,0000,00,9,99,{gangwei},2,{str(page)}.html?lang=c&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&ord_field=0&dibiaoid=0&line=&welfare='
            que.put(url_put)
        # thread_it(req_thread)
        thread_it(req_thread)
        # req_thread()
        while True:
            if que.empty():
                time.sleep(0.5)
                Label_3.configure(text='处理完成')
                lis_1.delete(0,END) #删除框内内容
                #打印到文本里
                lis_1.insert(END,'{:^15}\t{:^15}\t{:^15}\t{:^15}\t{:^15}\t{:^15}\t{:^15}\t{:^15}\t{:^15}'.format('岗位','薪水','公司名字','工作地址','公司性质','工作说明','招聘要求','公司规模','公司行业'))
                #循环打印所有条目
                for item in name_list:
                    lis_1.insert(END,'{:^15}\t{:^15}\t{:^15}\t{:^15}\t{:^15}\t{:^15}\t{:^15}\t{:^15}\t{:^15}'.format(item[0],item[1],item[2],item[3],item[4],item[5],item[6],item[7],item[8])) 
                
                #存文件
                save_csv()

                #配置数据库
                setMysql()
                #存数据库
                saveMysql()
                return

#存文件
def save_csv():
    csv_1 = csv_path.format(entry_1.get())
    with open(csv_1,'w',newline='',encoding='utf-8-sig')as f:
        
        csv_txt = csv.writer(f)        
        csv_txt.writerow(['岗位','薪水','公司名字','工作地址','公司性质','工作说明','招聘要求','公司规模','公司行业'])
        csv_txt.writerows(name_list)

#存数据库
def saveMysql():
    for item in name_list:
        ls = tuple(item)
        coures = db.cursor()
        coures.execute(f"use {dbname};")
        sql=f"insert into {tabname} values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        coures.execute(sql,ls)	
        db.commit()
#数据库配置    
def setMysql():
    coures=db.cursor()
    #创建数据库
    coures.execute(f"show databases like '{dbname}'")
    resule = coures.fetchall()
    if len(resule) == 0:
        # print(f"创建数据库 {dbname}")
        coures.execute(f"create database {dbname} charset=utf8")
        pass
    else:
        pass
    #创建表
    coures.execute(f"use {dbname};")
    coures.execute(f"show tables like '{tabname}'")
    resule=coures.fetchall()
    if len(resule)==0:
        print(f"创建表 {tabname}")
        creataberSql = f"""create table {tabname}(
                       岗位 varchar(500),
                       薪水 varchar(500), 
                       公司名字 varchar(500), 
                       工作地址 varchar(500),
                       公司性质 varchar(500),
                       工作说明 varchar(500),
                       招聘要求 varchar(500),                    
                       公司规模 varchar(500),
                       公司行业 varchar(500)  
                       );"""
        coures.execute(creataberSql)


        
#获取数据
def req_thread():
    global name_list
    while True:
        if que.empty():
            # print(2)
            return
        else:
            url_get = que.get()
            # print('3')
            # que.task_done()
            req_1 = requests.get(url_get,headers=headers)
            req_1.encoding = 'gbk' 
            req_1 = req_1.text
            # print(req_1)
            req_1 = etree.HTML(req_1)
            json_1 = str(req_1.xpath('//script[@type = "text/javascript"]/text()')[0])
            json_1 = json_1.split('=',1)[1]
            json_1 = json.loads(json_1)
            json_list = json_1['engine_jds']
            Label_3.configure(text=f'正在处理..{url_get}')
            for i in json_list:
                name = i['job_name']
                money = i['providesalary_text']
                      
                company_name = i['company_name']
                
                workarea_text = i['workarea_text']
                companytype_text = i['companytype_text']
                # issuedate = i['issuedate']
                jobwelf = i['jobwelf']
                attribute_text = i['attribute_text']
                attribute_text = ''.join(attribute_text)
                companysize_text = i['companysize_text']
                companyind_text = i['companyind_text']
                name_list.append([name,money,company_name,workarea_text,companytype_text,jobwelf,attribute_text,companysize_text,companyind_text])
                # print(name_list)
            que.task_done()
            
      
#创建线程
def thread_it(func, *args):    

    t = threading.Thread(target=func, args=args) 
    t.start()
    
    # t.join()

#pandas 月薪解构
def pandas_yuexin(arrLike):
        
    money = arrLike['薪水'].split('/')
    money_1 = money[0]
    money_2 = money[1]
    if money_1.find('-') == -1:
        # money_3 =0
        # money_4 =0
        if money_1[-1] == '万':
            if money_2 =='月':
                money_mid = int(int(money_1[:-1])*10000)
            else:
                money_mid = int(int(money_1[:-1])*10000//12)
        else:
            if money_2 == '月':
                money_mid = int(int(money_1[:-1])*1000)
            else:
                money_mid = int(int(money_1[:-1])*10000//12)
        
    else:
        money_3 = money_1.split('-')[0]
        money_4 = money_1.split('-')[1]
        if money_4[-1] =='万':
            if money_2 == '月':
                money_3 = int(float(money_3)*10000)
                money_4 = int(float(money_4[:-1])*10000)
                money_mid = int((money_3+money_4)/2)
                
            else:
                money_3 = int(float(money_3)*10000//12)
                money_4 = int(float(money_4[:-1])*10000//12)
                money_mid = int((money_3+money_4)/2)
        else:
            if money_2 == '月':
                money_3 = int(float(money_3)*1000)
                money_4 = int(float(money_4[:-1])*1000)
                money_mid = int((money_3+money_4)/2)
            else:
                money_3 = int(float(money_3)*1000//12)
                money_4 = int(float(money_4[:-1])*1000//12)
                money_mid = int((money_3+money_4)/2)
    return money_mid


def pandas_fenxi():
    t1 = pd.DataFrame(name_list,columns=['岗位','薪水','公司名字','工作地址','公司性质','工作说明','招聘要求','公司规模','公司行业'])
    # print(t1['薪水'])
    t1 = t1.replace(to_replace='',value=np.NaN)
    t1 = t1.dropna(axis=0,subset = ['薪水'])
    # print(t1.loc[t1.index[80:90],['薪水']])    
    t1['具体薪水'] = t1.apply(pandas_yuexin,axis = 1)
    # print(t1['具体薪水'])
    # print(t1.loc[t1.index[80:90],['薪水']])
    bins = [0,5000,8000,10000,12000,15000,18000,20000,25000,30000,50000]
    t2 = pd.cut(t1['具体薪水'],bins)
    # print(t21)
    t3 = pd.value_counts(t2,sort=False)
    return t3

def pandas_fenxi_2():
    t1 = pd.DataFrame(name_list,columns=['岗位','薪水','公司名字','工作地址','公司性质','工作说明','招聘要求','公司规模','公司行业'])
    # print(t1['薪水'])
    t1 = t1.replace(to_replace='',value=np.NaN)
    t1 = t1.dropna(axis=0,subset = ['公司性质'])  
    
    t3 = pd.value_counts(t1['公司性质'],sort=False)
    # print(t3)
    return t3

canvs = None 
#画图
def draw_pic():
    global canvs, f   
    
    if canvs:
        for child in canvas.winfo_children():
            child.destroy()
        # or just use canvas.winfo_children()[0].destroy()  
  
    canvs = None

    f = plt.Figure(figsize=(15, 8), dpi=100)
    f_plot = f.add_subplot(111)

    # f_plot.clear()    
    canvs = FigureCanvasTkAgg(f,master = canvas)
    
    t3 =  pandas_fenxi()

    f_plot.set_title('招聘薪水分布图')
    f_plot.set_xlabel('薪水')   
    f_plot.bar(t3.index.astype(str),t3)  
    # return f_plot
    canvs.draw()  
    canvs.get_tk_widget().grid()

def draw_pic_2():    
    
    global canvs, f   
    if canvs:
        for child in canvas.winfo_children():
            child.destroy()
        # or just use canvas.winfo_children()[0].destroy()  
  
    canvs = None

    f = plt.Figure(figsize=(15, 8), dpi=100)
    f_plot = f.add_subplot(111)

    # f_plot.clear()    
    canvs = FigureCanvasTkAgg(f,master = canvas)
    
    t3 =  pandas_fenxi_2()

    f_plot.set_title('公司性质饼图')
     
    f_plot.pie(t3,labels=t3.index.astype(str),autopct='%1.1f%%',shadow=False) 

    canvs.draw() 
    canvs.get_tk_widget().grid() 

#查询界面
def get_pic():      
    if entry_1.get() == '':
        messagebox.showinfo('提示','请先输入搜索内容！')
        return
    else:
        root=Tk()
        root.title("分析图")
        # root.geometry('700x500+50+40')
        # entry=Entry(root,font=('微软雅黑',20)) 
        # canvs = FigureCanvasTkAgg(f,root)
        # canvs.get_tk_widget().grid(row=0,columnspan=3) 
        # canvs.draw()  
        #     
        # lis=Listbox(root,font=('微软雅黑',15),width=55,height=15)
        # lis.grid(row=0,columnspan=3)
        global canvas
        canvas = Canvas(root, width=1500, height=800, bg='white') 
        canvas.grid(row=0,columnspan=3) 
        button5=Button(root,text='退出',width=20,command=quit,height=3)
        button5.grid(row=1,column=2)
        button6=Button(root,text='查询薪水分布',width=20,height=3,command=draw_pic)
        button6.grid(row=1,column=0)
        button7=Button(root,text='查询公司性质',width=20,height=3,command=draw_pic_2)
        button7.grid(row=1,column=1)

root=Tk()
#窗口的标题
root.title("招聘信息查询")
#标签
lable_1=Label(root,text='输入要查询的工作职位：')
#定位默认0，0
lable_1.grid(row=0,column=0,sticky=W)
#输入所查询职位
entry_1=Entry(root,font=('微软雅黑',20),width=50)
#所输入内容的一个定位
entry_1.grid(row=0,column=1,sticky=W)
Label_3 = Label(root,height = 3,text='未执行下载任务',width=205)
Label_3.grid(row=2,column=0,columnspan=3)
#列表框：查询内容所显示的位置
sb = Scrollbar(root)
sb.grid(row = 3,column=2)
# li = tkinter.Listbox(root,yscrollcommand=sb.set)


lis_1=Listbox(root,width=205,height=35,yscrollcommand=sb.set)
#跨列整合span
lis_1.grid(row=3,column = 0,columnspan=2)
sb.config(command=lis_1.yview)
#按钮
#command命令
button_3=Button(root,text='查询',width=10,command=lambda:thread_it(req_job_search))
button_3.grid(row=1,column=0,sticky=W)

button1=Button(root,text='退出',width=10,command=quit)
button1.grid(row=1,column=1,sticky=E)
button2=Button(root,text='进行数据分析',width=20,command=get_pic)
# command=lambda:thread_it(pandas_fenxi)
button2.grid(row=1,columnspan=2)
root.mainloop()




