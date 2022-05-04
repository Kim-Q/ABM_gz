from mesa.visualization.ModularVisualization import ModularServer
# from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import CanvasGrid, ChartModule, PieChartModule, TextElement, NetworkModule, BarChartModule
# import matplotlib.pyplot as plt
import networkx as nx
from environment import *
import json
# from tensorflow.keras import models
from keras import models
import h5py
import os
import sys

# path = sys.argv[0]  # 获取本文件路径
# filename = os.path.basename(path)  # 获取本文件名
# path = os.path.dirname(os.path.realpath(sys.argv[0]))  # 获取本文件所在目录

# filelist = os.listdir(path)  # 获取文件名列表
# filelist.remove(filename)  # 从目录的文件里面去除本文件的文件名

def app_path():
    """Returns the base application path."""
    if hasattr(sys, 'frozen'):
        # Handles PyInstaller
        return os.path.dirname(sys.executable)  #使用pyinstaller打包后的exe目录
    return os.path.dirname(__file__)                 #没打包前的py目录
    # return os.path.split(os.path.realpath(__file__))[0]

activity_key={'guohang':'过航','dijin':'抵近','zhencha':'侦查','yanxi':'演习','xunlian':'训练'}

class StatusElement(TextElement):
    def __init__(self):
        self.round=0
        self.label=None
        if not os.path.exists(app_path()+'/simu_recorder'):
            os.makedirs(app_path()+'/simu_recorder')
        if not os.path.exists(app_path()+'/dete_recorder'):
            os.makedirs(app_path()+'/dete_recorder')

    def render(self, model):        
        model_data=model.datacollector.get_model_vars_dataframe()
        if len(model_data)==1:
            self.label=activity_key[model_data.iloc[-1]['activity'][0]]
            self.round+=1
        if len(model_data)==91:
            agent_data=model.datacollector.get_agent_vars_dataframe()
            agent_data.to_csv(app_path()+'/simu_recorder/show_trace{}.csv'.format(self.round),index=False)
            model_data.iloc[:,:6].to_csv(app_path()+'/dete_recorder/{}{}.csv'.format(str(model_data.iloc[-1]['activity'][0]),self.round),index=False)
            
        return "这是第", str(self.round), "个仿真预警训练；美国采取的行动是：",str(self.label),"。\n 下面两个折线图分别是东沙群岛侦查到的各类行为体数量和最近距离："

class PredictElement(TextElement):
    def __init__(self):
        self.label=None
        self.round=0
        self.correct=0
        if not os.path.exists(app_path()+'/dete_recorder'):
            os.makedirs(app_path()+'/dete_recorder')
        self.names=os.listdir(app_path()+'/dete_recorder')
        self.activity_key={0:'过航',1:'抵近',2:'侦查',3:'演习',4:'训练'}

    def render(self, model):
        model_data=model.datacollector.get_model_vars_dataframe()
        if len(model_data)==92:
            self.round+=1
            names = os.listdir(app_path()+'/dete_recorder')
            self.model = models.load_model('ABM_model.h5')
            dir=list(set(names)-set(self.names))[0]
            data=pd.read_csv(app_path()+'/dete_recorder/'+dir)
            X= np.array(data.values[1:], dtype = float).reshape(1,90,6,1)
            y_predict = self.model.predict(X)
            self.label=self.activity_key[np.argmax(y_predict)]
            self.names=names
            if self.label==activity_key[model_data.iloc[-1]['activity'][0]]:
                self.correct=(self.correct*(self.round-1)+1)/self.round
            else:
                self.correct=(self.correct*(self.round-1))/self.round
        elif len(model_data)==1:
            self.label=None
        return "预警模型对本次行为的判断结果为：", str(self.label),"。\n 截止目前，预警模型的判断正确率为：", str(round(self.correct,4))
        
COLORS1 = {
    'aircraft_num':"#C59435",
    'warship_num':"#9DCC5F",
    'carrier_num':"#9DFD0A",
}

COLORS2 = {
    'aircraft_min_distance':"#C59435",
    'warship_min_distance':"#9DCC5F",
    'carrier_min_distance':"#9DFD0A",
}

G=nx.read_gpickle(app_path()+r"/input/Dongsha_withstandpoint.gpickle")
with open(app_path()+'/input/agent_setting.json','r',encoding='utf8')as fp:
    agent_setting = json.load(fp)

statusElement = StatusElement()
predictElement=PredictElement()
# 展示探测到的各类agent数量
chart1 =ChartModule([{"Label": label, "Color": color} for (label, color) in COLORS1.items()],canvas_height=100, canvas_width=300, data_collector_name='datacollector')
# 展示探测到各类agent的最近距离
chart2 =ChartModule([{"Label": label, "Color": color} for (label, color) in COLORS2.items()],canvas_height=100, canvas_width=300, data_collector_name='datacollector')


server = ModularServer(Environment,
                        [statusElement,chart1,chart2,predictElement],
                       "ABM1.0 Demo",
                       {"graph":G,"arg":agent_setting})
# server.port = 8521
server.launch()