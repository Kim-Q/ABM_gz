import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
from tkinter import font
import pandas as pd
from tkinter import scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import seaborn as sns
import plotly.graph_objects as go
import palettable
from tkwebview2.tkwebview2 import WebView2
from tkinterweb import HtmlFrame
import time
import folium
from PIL import Image, ImageTk
from folium import plugins
import urllib
import math
import threading
import random
import csv
import string
import re
import map_page as mp

#==========================View==================================#
class View(object):
    def __init__(self, al1, al2, ib): # al--Animate Line; ib--Information Board
        self.ground = tk.Tk()
        self.ground.state('zoomed')
        self.ground.title("ABM")
        self.root = tk.Frame(self.ground)
        self.root.pack(side = 'top', fill = 'both', expand = True)
        self.root.grid_rowconfigure(0, weight = 1)
        self.root.grid_columnconfigure(0, weight = 1)
        
        self.al1 = al1
        self.al2 = al2
##        self.abm = abm
##        self.abm.register(self.root)
        self.ib = ib
##        self.root.attributes('-fullscreen', True)

        self.init_GUI()
        self.controller = None

    def init_GUI(self):
        width = self.ground.winfo_screenwidth()
        height = self.ground.winfo_screenheight()
        
        width_d4 = int(width/4)
        width_d3 = int(width/3)-6
        height_d2 = int(height/2)-5

#######################################################################
#### ______________________________   ______________________________  ####
#### |                                                          |   |             |              |              |              |  ####  
#### |                                                          |   |             |              |              |              |  ####  
#### |          abm_cv: ABM Canvas           |   | button |  linep1  |  linep2  | infobd  |  ####
#### |                                                          |   |             |              |              |              |  ####  
#### |                                                          |   |             |              |              |              |  #### 
#### -------------------------------------------------   -------------------------------------------------  ####
#### |                                                          |   |                   |                   |                  |  ####
#### |                                                          |   |                   |                   |                  |  ####  
#### |       stat_cv: Statistics Canvas       |   |   pieplt1    |    barplt1   |   pieplt2   |  ####    
#### |                                                          |   |                   |                   |                  |  #### 
#### |                                                          |   |                   |                   |                  |  ####
#### -------------------------------------------------   -------------------------------------------------  ####
#######################################################################

        ### abm_cv
        self.abm_cv = tk.Canvas(self.root, height = height_d2, width = width,
                                borderwidth = 1)
        self.abm_cv.grid(row = 0, column = 0)

        ### stat_cv
        self.stat_cv = tk.Canvas(self.root, height = height_d2, width = width,
                                 borderwidth = 1)
        self.stat_cv.grid(row = 1, column = 0)

        ### button_cv
        self.button_cv = tk.Canvas(self.abm_cv,
                                   height = height_d2, width = width_d4, bg = "black")
        self.button_cv.grid(row = 0, column = 0)

        self.init_btn(height_d2, width_d4)

        ### linep1_cv
        self.linep1_cv = tk.Canvas(self.abm_cv, height = height_d2, width = width_d4,
                                   borderwidth = 1, bg = "blue")
        self.linep1_cv.grid(row = 0, column = 1)

        self.linep1_lf = tk.LabelFrame(
            self.linep1_cv,
            text = "C国观测行为体数量",
            font = ('Microsoft JhengHei', 18, "bold"),
            bg = "white",
            )
        self.linep1_lf.pack(fill = "both", expand = 'yes', anchor='center')

        self.al1.setup_canvas(self.linep1_lf) # 加载动态折线图1所在图层

        ### linep2_cv
        self.linep2_cv = tk.Canvas(self.abm_cv, height = height_d2, width = width_d4,
                                   borderwidth = 1, bg = "red")
        self.linep2_cv.grid(row = 0, column = 2)

        self.linep2_lf = tk.LabelFrame(
            self.linep2_cv,
            text = "C国观测行为体最近距离",
            font = ('Microsoft JhengHei', 18, "bold"),
            bg = "white",
            )
        self.linep2_lf.pack(fill = "both", expand = 'yes', anchor='center')

        self.al2.setup_canvas(self.linep2_lf) # 加载动态折线图2所在图层

        ### infobd_cv
        self.infobd_cv = tk.Canvas(self.abm_cv, height = height_d2, width = width_d4,
                                   borderwidth = 1, bg = "green")
        self.infobd_cv.grid(row = 0, column = 3)

        self.infobd_lf = tk.LabelFrame(
            self.infobd_cv,
            text = "仿真过程说明",
            font = ('Microsoft JhengHei', 18, "bold"),
            bg = "white",
            height = height_d2+24, width = width_d4,
            )
        self.infobd_lf.pack(fill = "both", expand = 'yes', anchor='center')
        
        self.infobd_st = scrolledtext.ScrolledText(self.infobd_lf,
                                            width = 26, # 字数量
                                            height = 14, # 字行数
                                            wrap = tk.WORD,
                                            font = ( "Microsoft JhengHei" , 13 ))
        self.infobd_st.pack()
        
        self.ib.register(self.root, self.infobd_st) # 加载文本框

        self.infobd_st.tag_config('act',  foreground='green', font = ('Microsoft JhengHei', 13, 'bold'))  
        self.infobd_st.tag_config('oppi', foreground='royalblue', font = ('Microsoft JhengHei', 13, 'bold'))
        self.infobd_st.tag_config('tgt', foreground='orange', font = ('Microsoft JhengHei', 13, 'bold'))
        self.infobd_st.tag_config('self', foreground='red', font = ('Microsoft JhengHei', 13, 'bold'))

        ### pieplt1_cv
        self.pieplt1_cv = tk.Canvas(self.stat_cv, height = height_d2, width = width_d3,
                                   borderwidth = 1, bg = "orange")
        self.pieplt1_cv.grid(row = 1, column = 0)

        ### barplot_cv
        self.barplot_cv = tk.Canvas(self.stat_cv, height = height_d2, width = width_d3,
                                   borderwidth = 1, bg = "purple")
        self.barplot_cv.grid(row = 1, column = 1)

        ### pieplt2_cv
        self.pieplt2_cv = tk.Canvas(self.stat_cv, height = height_d2, width = width_d3,
                                   borderwidth = 1, bg = "gray")
        self.pieplt2_cv.grid(row = 1, column = 2)

    def main_loop(self):
        self.root.mainloop()

    # 静态统计图加载初始化
    def register(self, controller):
        self.controller = controller
        self.controller.model.plot_pie(self.pieplt1_cv, "A国实际行为占比", self.controller.model.a_act_stat)
        self.controller.model.plot_bar(self.barplot_cv, "A国观测行为体占比", self.controller.model.a_obj_stat)
        self.controller.model.plot_pie(self.pieplt2_cv, "C国应对行为占比", self.controller.model.c_act_stat)
##        self.lp1_l1, self.lp1_l2 = self.controller.model.init_lplot(self.linep1_lf)
##        self.lp2_l1, self.lp2_l2 = self.controller.model.init_lplot(self.linep2_lf)

    # 按钮区初始化
    def init_btn(self, height, width):
        parent = tk.LabelFrame(
            self.button_cv,
            text = "仿真模拟",
            font = ('Microsoft JhengHei', 18, "bold"),
            bg = "white",
            )
##        parent.grid(row = 0, column = 0, ipadx = 100, )
        
        parent.pack(fill = "both", expand = 'yes', anchor='center', ipadx = 100, ipady = 50)

        
        # Dropdown Button
        lb1 = tk.Label(parent,
                       text="请选择一种敌方行为",
                       font = ('Microsoft JhengHei', 16, "bold"),
                       bg = "white",)
        lb1.pack(side = tk.TOP, pady = (45, 5))

        s = ttk.Style()
        s.configure('my.TButton',
                    width = 24, height = 5,
                    justify = tk.CENTER,
                    relief = tk.SUNKEN,
                    font = ('Microsoft JhengHei', 20, "bold"))
        s.configure('my.TMenubutton', 
                    width = 18,
                    anchor = tk.CENTER,
                    font = ('Microsoft JhengHei', 20, "bold"))
        
        self.act_var = tk.StringVar(parent)
        choices = {"过航","抵近","侦察","演习","训练"}
        self.act_var.set("过航")
        act_popup = ttk.OptionMenu(parent, self.act_var, *choices,
                                   style = "my.TMenubutton")
        act_popup.pack(side = tk.TOP, pady = (0, 15))
    
        # Button -- Start ABM
        start_btn = ttk.Button(parent,
                               text="开始\n仿真模拟",
                               style = "my.TButton",
                               command = self.start_sim)   
        start_btn.pack(side = tk.TOP, pady = 15)

        # Button -- Map Page
        map_btn = ttk.Button(parent,
                             text="查看\n仿真地图",
                             style = "my.TButton",
                             command = self.to_map)   
        map_btn.pack(side = tk.TOP, pady = (15, 54))
    
    def start_sim(self):
        
##        th1 = threading.Thread(target = self.abm.start())
##        th1.setDaemon(True)
##        th1.start()
        
        th2 = threading.Thread(target = self.al1.start)
        th2.setDaemon(True)
        th2.start()
        
        th3 = threading.Thread(target = self.al2.start)
        th3.setDaemon(True)
        th3.start()
        
        th4 = threading.Thread(target = self.ib.start)
        th4.setDaemon(True)
        th4.start()

    def to_map(self):
        self.mappage = mp.MapPage(self.root)
        self.mappage.root.tkraise()

#==========================Model==================================#
class Model:
    def __init__(self):
        ### 静态统计数据 ###
        self.a_act_stat = pd.read_csv("../data/a_act_stat.csv") 
        self.a_obj_stat = pd.read_csv("../data/a_obj_stat.csv")
        self.c_act_stat = pd.read_csv("../data/c_act_stat.csv")
        ##################

    def plot_pie(self, canvas, title, data):
        master = tk.LabelFrame(
            canvas,
            text = title,
            font = ('Microsoft JhengHei', 18, "bold"),
            bg = "white",
            )
##        parent.grid(row = 0, column = 0, ipadx = 100, )
        master.pack(fill = "both", expand = 'yes', anchor='center')
        
        fig = plt.figure(figsize = (4.2, 3.2))
        labels = data.iloc[:,0].to_list()
        values = data.iloc[:,1].to_list()
        inner_circle = plt.Circle( (0,0), 0.7, color='white')
        plt.rcParams['font.sans-serif']=['Microsoft JhengHei']

        plt.pie(values, labels = labels, autopct='%.0f%%',
                colors = eval("palettable.cartocolors.diverging.Temps_{}.mpl_colors".format(len(labels))),
                textprops = {'color':'black',
                   'fontsize': 14,#文本大小
                   'fontfamily': 'Microsoft JhengHei',},
                wedgeprops = { 'linewidth' : 5, 'edgecolor' : 'white' })
        p = plt.gcf()
        p.gca().add_artist(inner_circle)
        plt.text(0, 0, "最近\n{}起".format(int(sum(values)*100)),
                 font = 'Microsoft JhengHei', size = 14,
                 ha = "center", va = "center")
##        fig.tight_layout()
        
        pie_chart = FigureCanvasTkAgg(fig, master = master)
        pie_chart.draw()
        pie_chart.get_tk_widget().pack()

    def plot_bar(self, canvas, title, data):
        master = tk.LabelFrame(
            canvas,
            text = title,
            font = ('Microsoft JhengHei', 18, "bold"),
            bg = "white",
            )
##        parent.grid(row = 0, column = 0, ipadx = 100, )
        master.pack(fill = "both", expand = 'yes', anchor='center')

        fig,ax = plt.subplots(figsize = (4.2, 3.2))
        sns.set_theme(style="whitegrid")
        
        sns.barplot(x = data.columns[0], y = data.columns[1], data=data,
                    palette = "RdYlBu", ax = ax)
        for i,row in data.iterrows():
            x,y = i,row[1]
            if y >= 20:
                y /= 2
            else:
                y += 5
            plt.text(x, y, row[1], size = 10,
                     ha = "center", va = "center",
                     bbox = dict(facecolor = 'white', alpha=0.5, boxstyle = "round", edgecolor = "lightgray"))
        plt.xlabel('', font = 'Microsoft JhengHei', size = 14)
        plt.ylabel('占比', font = 'Microsoft JhengHei', size = 14)
        
##        fig.tight_layout()
        
        pie_chart = FigureCanvasTkAgg(fig, master = master)
        pie_chart.draw()
        pie_chart.get_tk_widget().pack()
            
#==========================Controller==================================#
class Controller(object):
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.register(self)

#==========================Animation==================================#
class AnimateLine(object):
    def __init__(self, data_path, colnames):
        self.colnames = colnames
        data = pd.read_csv(data_path)
        self.y1 = data[self.colnames[0]].to_list() # 修改y1列名
        self.y2 = data[self.colnames[1]].to_list() # 修改y2列名
        self.y3 = data[self.colnames[2]].to_list() # 修改y3列名
        self.x = [*range(1, len(self.y1)+1)]
        self.fig, self.ax = plt.subplots(figsize = (3.15, 3.1))
        self.click_count = 0

    def setup_canvas(self, root):
        self.root = root
        self.canvas = FigureCanvasTkAgg(self.fig, master = self.root)
        self.canvas.get_tk_widget().pack(expand = 1, fill = "both")
    
    def init_p(self):
        plt.rcParams['font.family'] = ['sans-serif']
        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.title("Graph", color = "black", size = 16, family = "Arial")
        self.line1, = self.ax.plot([], [], color = "royalblue", marker = "o",
                                   label = "Aircraft",
                                   linestyle = "dashed", linewidth = 1, markersize = 5,
                                   markeredgecolor = "lightgray")
        self.line2, = self.ax.plot([], [], color = "brown", marker = "*",
                                   label = "Warship",
                                   linestyle = "solid", linewidth = 1, markersize = 5,
                                   markeredgecolor = "lightgray")
        self.line3, = self.ax.plot([], [], color = "orange", marker = "^",
                                   label = "Carrier", 
                                   linestyle = "dotted", linewidth = 1, markersize = 3,
                                   markeredgecolor = "lightgray")
        
        self.ax.legend([self.line1, self.line2, self.line3], ["Aircraft", "Warship", "Carrier"],
                       loc = "upper center", ncol = 3, fontsize = 8, bbox_to_anchor = (0.5, 1.12))
        return  [self.line1, self.line2, self.line3]
    
    def animate(self, i):
        
        #####################################
        ##########    注意修改列名称    ##########
        #####################################

        self.line1.set_xdata(self.x[:i])
        self.line1.set_ydata(self.y1[:i])
        self.line2.set_xdata(self.x[:i])
        self.line2.set_ydata(self.y2[:i])
        self.line3.set_xdata(self.x[:i])
        self.line3.set_ydata(self.y3[:i])
        if len(self.x) > 1:
            self.ax.set_xlim([0, self.x[i]+1])
            y_lim = max(max(self.y1), max(self.y2), max(self.y3))
            self.ax.set_ylim([0, y_lim*1.2])
            yticks = self.ax.get_yticks()
            new_yt = [str(round(i,1)).replace(".0","") if i < 1000 else str(round((i/1000),1)).replace(".0","")+"K" for i in yticks]
            self.ax.set_yticks(yticks, new_yt)
        
        return [self.line1, self.line2, self.line3]

    def start(self):
        # interval 更新频率ms
        # frames总共多少帧。频率5次/s，24次数为120秒等于2分钟。
        self.ani = animation.FuncAnimation(self.fig, self.animate,
                                           interval = 2000, 
                                           init_func = self.init_p,
                                           frames = len(self.x),) 
        self.canvas.draw()
        self.canvas.flush_events()

    def stop(self):
        self.ani.event_source.stop()

    def cont(self):
        self.ani.event_source.start()

#==========================Board==================================#
class InformBoard:
    def register(self, root, labelframe):
        self.root = root
        self.labelframe = labelframe
        self.data = pd.read_csv("../data/text_ch.csv", encoding = "gb18030") 

    def start(self):
        def add_hash(matched):
            new = "#"+matched.group("value")+"#"
            return new
        tag_dict = {"美方":"oppi","我方":"self",
                    "演习":"act","东沙群岛":"tgt",
                    "抵近":"act","干扰":"act",
                    "中止":"act"}
        for i,row in self.data.iterrows():
            ts = str(row["timestamp"])
            message = row["msg_ch"]
##            print(ts, message)
            if message != message:
                pass
            else:
                message = re.sub(r"(?P<value>[美方|我方|演习|东沙群岛|抵近|干扰|中止]+)", add_hash, message)
                message = (ts + "    " + message + "\n").split("#")
                
                tags = [""if w not in tag_dict else tag_dict[w] for w in message]
                for j,k in zip(message, tags):
                    self.labelframe.insert(tk.END, j, k)
                
            self.root.after(2000) # 等待2秒
            self.labelframe.update()
##        old = []
##        for i in range(25):
##            df = pd.read_csv("../data/text.csv") # 信息板数据源
##            texts = df["info"].to_list()
##            if len(old) == 0:
##                renew = texts
##            else:
##                renew = texts[len(old):]
##            for row in renew:
##                self.labelframe.insert(tk.END, row)
##                self.labelframe.insert(tk.END, "\n")
####            time.sleep(5)
####            self.root.update()
##            self.root.after(5000) # 等待5秒
##            self.labelframe.update()
##            old = texts

#==========================Threading==================================#
##class ThreadAll:
##    def __init__(fun1, fun2, fun3, fun4):
##        # fun1--生成数据；fun2--动态图1；fun3--动态图2；fun4--信息板
##        self.fun1 = fun1
##        self.fun2 = fun2
##        self.fun3 = fun3
##        self.fun4 = fun4
##
##    def start(self):
##        for fun in [fun1, fun2, fun3, fun4]:
##            th = threading.Thread(target = fun)
##            th.setDaemon(True)
##            th.start()

#========================== ABM ==================================#
class ABM(object):
    def register(self, root):
        self.root = root
        
    def append_csv(self, row):
        with open("../data/abm_data.csv", "a+", newline = "") as f:
            write = csv.writer(f)
            write.writerow(row)
            
    def create_csv(self):
        with open("../data/abm_data.csv", "w", newline = "") as f:
            write = csv.writer(f)
            write.writerow(["idx", "x", "y1", "y2", "info"])

    def start(self):
        self.create_csv()
        for i in range(20):
            words = list(string.ascii_lowercase)[random.randint(0,25)] + list(
                string.ascii_uppercase)[random.randint(0,25)] + list(
                string.ascii_uppercase)[random.randint(0,25)] + list(
                string.ascii_uppercase)[random.randint(0,25)] + list(
                string.ascii_uppercase)[random.randint(0,25)] + list(
                string.ascii_uppercase)[random.randint(0,25)] + list(
                string.ascii_uppercase)[random.randint(0,25)]
            row = [i+1, i, random.randint(i, i**2), random.randint(i, i*2), words]
            self.append_csv(row)
            time.sleep(random.randint(1,8))
##            self.root.after(random.randint(1,8)*1000)        

##    def stop(self):
##        break # 设置暂停
        
if __name__ == "__main__":
##    abm = ABM()
    
    al1 = AnimateLine( "../data/yanxi0.csv",
                       ["aircraft_num", "warship_num", "carrier_num"])
    al2 = AnimateLine( "../data/yanxi0.csv",
                       ["aircraft_min_distance", "warship_min_distance", "carrier_min_distance"])
    ib = InformBoard()
    view = View(al1, al2, ib)
    model = Model()
    controller = Controller(model, view)
##    th1 = threading.Thread(target = abm.start)
##    th1.setDaemon(True)
##    th1.start()
    view.main_loop()
