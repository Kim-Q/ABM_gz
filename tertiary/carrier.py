# import numpy as np
# import pandas as pd
from mesa import Agent
import time
import random
from data_tools.cal_distance import *
from datetime import datetime

activity=['daiming','fancheng','guohang','dijin','zhencha','yanxi','xunlian','ganrao','quzhu']
class Carrier(Agent):
    def __init__(self,unique_id,model,leader,loc,standpoint):
        super().__init__(unique_id,model)
        self.model = model
        self.leader=leader
        self.activity=[]
        self.category="carrier"
        self.x=self.model.graph.nodes.data()[loc]['Lon_Lat'][0]
        self.y=self.model.graph.nodes.data()[loc]['Lon_Lat'][1]
        self.standpoint=standpoint
        self.timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # print("I'm an initial Carrier",str(self.unique_id),"with standpoint", str(self.standpoint), "locate in", str(self.model.graph.nodes.data()[loc]['name']))

        # 行为体特征，参数可修改
        self.speed=10000
        self.time=time.time()
        self.clock=self.time
        self.wait=0
        self.status=-1 #-1表示待命，0表示返航，1表示过航，2表示抵近，3表示侦查，4表示演习，5表示训练，6表示干扰，7表示驱逐
        self.warning=False

        self.target_loc=[]
        self.target_loc.append(loc)
        self.target_activity=[]
        self.target_activity.append("fancheng")

    #接受指令并解析行为
    def receive(self, target_loc, target_activity):
        self.status=activity.index(target_activity)-1
        if self.status>0:
            self.target_loc.insert(0,target_loc)
            self.target_activity.insert(0,target_activity)
            if self.status==1:
                self.wait=0
            elif self.status==2:
                self.wait=random.randint(1,10)
            elif self.status>2 and self.status<6:
                self.wait=random.randint(1,30)
        target_loc=self.model.graph.nodes.data()[target_loc]['Lon_Lat']
        length=cal_distance((self.x,self.y),target_loc)
        self.time=time.time()
        self.clock=self.time+length/self.speed
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
    
    def work(self):
        if self.warning:
            print("task has been interrupted")
            self.leader.feedback(self,False)
            self.status=-1
            if len(self.target_loc)>1:
                self.target_loc.pop(0)
                self.target_activity.pop(0)
                self.receive(self.target_loc[0],self.target_activity[0]) #结束任务返程
            return
        if self.wait>0:
            self.wait-=1
        else:
            self.leader.feedback(self,True)
            self.status=-1
            if len(self.target_loc)>1:
                self.target_loc.pop(0)
                self.target_activity.pop(0)
                self.receive(self.target_loc[0],self.target_activity[0]) #结束任务返程

    def step(self):
        self.timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.status==-1 and self.target_activity[0]=="fancheng":
            return
        elif self.towards()!=self.status:
            # print(self.warning,self.standpoint)
            if self.standpoint==-1:
                self.work()
                return
            else:
                if self.warning:
                    return
                else:
                    self.status=-1
                    if len(self.target_loc)>1:
                        self.target_loc.pop(0)
                        self.target_activity.pop(0)
                        self.receive(self.target_loc[0],self.target_activity[0]) #结束任务返程
                    return
        elif self.status==self.towards():
            # print(self.x, self.y)
            # print(self.warning,self.standpoint)
            return