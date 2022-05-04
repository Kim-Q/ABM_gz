# import numpy as np
# import pandas as pd
from mesa import Agent
import time
import random
from data_tools.cal_distance import *
from datetime import datetime

class Warship(Agent):
    def __init__(self,unique_id,model,leader,loc,standpoint):
        super().__init__(unique_id,model)
        self.model = model
        self.leader=leader
        self.activity=[]
        self.category="warship"
        self.x=self.model.graph.nodes.data()[loc]['Lon_Lat'][0]
        self.y=self.model.graph.nodes.data()[loc]['Lon_Lat'][1]
        self.standpoint=standpoint
        self.timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # print("I'm an initial Warship",str(self.unique_id),"with standpoint", str(self.standpoint), "locate in", str(self.model.graph.nodes.data()[loc]['name']))

        # 行为体特征，参数可修改
        self.speed=30000
        self.time=time.time()
        self.clock=self.time
        self.status=-1 #-1表示待命，0表示返航，1表示过航，2表示抵近干扰，3表示侦查，4表示演习，5表示训练
        self.target_loc=[]
        self.target_loc.append(loc)
        self.target_activity=[]
        self.target_activity.append("fancheng")

    #接受指令并解析行为
    def receive(self, target_loc, target_activity):
        # print("I'm a warship with standpoint",str(self.standpoint),"receive the deployment of", target_activity)
        if target_activity!='fancheng' and self.status>0:
            self.target_loc.insert(1,target_loc)
            self.target_activity.insert(1,target_activity)
            # print("agent is working")
            return

        if target_activity=='fancheng':
            self.status=0
            target_loc=self.model.graph.nodes.data()[target_loc]['Lon_Lat']
            length=cal_distance((self.x,self.y),target_loc)
            self.time=time.time()
            self.clock=self.time+length/self.speed
            self.cos, self.sin=(target_loc[0]-self.x)/length,(target_loc[1]-self.y)/length

        elif target_activity=='guohang':
            self.status=1
            self.target_loc.insert(0,target_loc)
            self.target_activity.insert(0,target_activity)
            target_loc=self.model.graph.nodes.data()[target_loc]['Lon_Lat']
            length=cal_distance((self.x,self.y),target_loc)
            self.clock=time.time()+length/self.speed
            self.cos, self.sin=(target_loc[0]-self.x)/length,(target_loc[1]-self.y)/length

        elif target_activity=='dijin':
            self.status=2
            #随机耗时10s左右
            self.wait=random.randint(1,10) 
            # print("work needs to be finished in", str(self.wait))
            self.target_loc.insert(0,target_loc)
            self.target_activity.insert(0,target_activity)
            target_loc=self.model.graph.nodes.data()[target_loc]['Lon_Lat']
            length=cal_distance((self.x,self.y),target_loc)
            self.clock=time.time()+length/self.speed
            self.cos, self.sin=(target_loc[0]-self.x)/length,(target_loc[1]-self.y)/length

        elif target_activity=='zhencha':
            self.status=3
            #随机耗时30s左右
            self.wait=random.randint(1,30) 
            # print("work needs to be finished in", str(self.wait))
            self.target_loc.insert(0,target_loc)
            self.target_activity.insert(0,target_activity)
            target_loc=self.model.graph.nodes.data()[target_loc]['Lon_Lat']
            length=cal_distance((self.x,self.y),target_loc)
            self.clock=time.time()+length/self.speed
            self.cos, self.sin=(target_loc[0]-self.x)/length,(target_loc[1]-self.y)/length

        elif target_activity=='yanxi':
            self.status=4
            #随机耗时30s左右
            self.wait=random.randint(1,30) 
            # print("work needs to be finished in", str(self.wait))
            self.target_loc.insert(0,target_loc)
            self.target_activity.insert(0,target_activity)
            target_loc=self.model.graph.nodes.data()[target_loc]['Lon_Lat']
            length=cal_distance((self.x,self.y),target_loc)
            self.clock=time.time()+length/self.speed
            self.cos, self.sin=(target_loc[0]-self.x)/length,(target_loc[1]-self.y)/length

        elif target_activity=='xunlian':
            self.status=5
            #随机耗时30s左右
            self.wait=random.randint(1,30) 
            # print("work needs to be finished in", str(self.wait))
            self.target_loc.insert(0,target_loc)
            self.target_activity.insert(0,target_activity)
            target_loc=self.model.graph.nodes.data()[target_loc]['Lon_Lat']
            length=cal_distance((self.x,self.y),target_loc)
            self.clock=time.time()+length/self.speed
            self.cos, self.sin=(target_loc[0]-self.x)/length,(target_loc[1]-self.y)/length


    # 过航+返程，抵达返回状态，未抵达更新位置
    def towards(self):
        if time.time()>self.clock:
            distance=cal_distance((self.x,self.y),self.model.graph.nodes.data()[self.target_loc[0]]['Lon_Lat'])
            # 暂时更新三类，返程/侦查、抵近干扰
            if ((self.status==0 or self.status==3) and distance<100) or (self.status==2 and distance<1000) or ((self.status==4 or self.status==5) and distance<2000):
                return -1
        else:
            t=time.time()
            self.x+=(t-self.time)*self.speed*self.cos #t*v*cos
            self.y+=(t-self.time)*self.speed*self.sin #t*v*sin
            self.time=t
            return self.status
    
    # 抵近，行为耗时约10s，内容未知
    def dijin(self):
        if self.wait>0:
            self.wait-=1
        else:
            # print(str(self.target_loc[0])+"finished!")
            self.receive(self.target_loc.pop(-1),self.target_activity.pop(-1)) #结束任务返程

    # 侦查，行为耗时约30s，内容未知
    def zhencha(self):
        if self.wait>0:
            self.wait-=1
        else:
            # print(str(self.target_loc[0])+"finished!")
            self.receive(self.target_loc.pop(-1),self.target_activity.pop(-1)) #结束任务返程

    # 演习，行为耗时约30s，内容未知
    def yanxi(self):
        if self.wait>0:
            self.wait-=1
        else:
            # print(str(self.target_loc[0])+"finished!")
            self.receive(self.target_loc.pop(-1),self.target_activity.pop(-1)) #结束任务返程

    # 训练，行为耗时约30s，内容未知
    def xunlian(self):
        if self.wait>0:
            self.wait-=1
        else:
            # print(str(self.target_loc[0])+"finished!")
            self.receive(self.target_loc.pop(-1),self.target_activity.pop(-1)) #结束任务返程

    def step(self):
        # print("I'm a warship with standpoint",str(self.standpoint),"with statue", str(self.status))
        self.timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.status==-1:
            return
        elif self.status==0: #返航
            self.status=self.towards()
            return
        elif self.status==1: #过航
            if self.towards()!=self.status:
                self.receive(self.target_loc.pop(-1),self.target_activity.pop(-1)) #过航到达最近距离后即刻返程
            return
        elif self.status==2: #干扰
            if self.towards()!=self.status:
                self.dijin()
            return
        elif self.status==3: #侦查
            if self.towards()!=self.status:
                self.zhencha()
            return
        elif self.status==4: #演习
            if self.towards()!=self.status:
                self.yanxi()
            return
        elif self.status==5: #训练
            if self.towards()!=self.status:
                self.xunlian()
            return
