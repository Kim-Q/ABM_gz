import numpy as np
import pandas as pd
from mesa import Agent
from random import choice
import random
import uuid
from tertiary.carrier import *
from tertiary.warship import *
from tertiary.aircraft import *
from datetime import datetime
import itertools


agent_list=[Carrier, Warship, Aircraft]
activity_A=['guohang','dijin','zhencha','yanxi','xunlian']
activity_C=['ignore','dijin','ganrao','quzhu']

class Jidi(Agent):
    def __init__(self,unique_id,model,leader,loc,standpoint,arg:dict):
        super().__init__(unique_id,model)
        self.subordinate=[]
        self.leader=leader
        self.x=self.model.graph.nodes.data()[loc]['Lon_Lat'][0]
        self.y=self.model.graph.nodes.data()[loc]['Lon_Lat'][1]
        self.standpoint=standpoint
        self.category="basement"
        self.time=time.time()
        self.activity=[]
        self.timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # self.zhencha=[]
        self.target_loc=[]
        self.target_activity=[]

        # print("I'm an secondary agent",str(self.unique_id),"with standpoint", str(self.standpoint), "and locate in", str(self.model.graph.nodes.data()[loc]['name']),". I have",str(sum(arg.values())),"subordinates.")
        for key, value in arg.items(): # {0:1,1:2} key代表agent的类型如agent_list, value代表该类型的数量
            for _ in range(value):
                agent= agent_list[int(key)](uuid.uuid1(), model, self, loc, self.standpoint)
                self.subordinate.append(agent)
                self.model.schedule.add(agent)

        # ### 训练过后用赋值的矩阵，不用再重新生成了
        # self.Q_score=pd.DataFrame({'activity':[],'Carrier':[],'Warship':[],'Aircraft':[],'score':[]})
        # self.Q_times=pd.DataFrame({'activity':[],'Carrier':[],'Warship':[],'Aircraft':[],'times':[]})

        # if self.standpoint==1:
        #     ### 下面是生成矩阵的过程，训练过后再删
        #     Cartesian=[activity_C[1:],range(3),range(5),range(5)]
        #     values=[d for d in itertools.product(*Cartesian)]
        #     for v in values:
        #         value=[i for i in v]
        #         # print(value,type(value))
        #         value.append(0)
        #         self.Q_score.loc[len(self.Q_score.index)]=value
        #         self.Q_times.loc[len(self.Q_times.index)]=value
        #     ###

    # def receive(self, target, order):
    #     self.target_loc.insert(0,target)
    #     self.target_activity.insert(0,order)
    #     self.deploy()

    def deploy(self,target_loc,target_activity):
        if self.standpoint==-1:
            self.activity.append(target_activity)
            if target_activity=='guohang':
                p = np.array([0.2, 0.3, 0.5])
            elif target_activity=='dijin':
                p = np.array([0.1, 0.2, 0.7])
            elif target_activity=='zhencha':
                p = np.array([0.0, 0.1, 0.9])

            if target_activity=='yanxi' or target_activity=='xunlian':
                for agent in self.subordinate:
                    if random.random()<0.3:
                        agent.receive(target_loc,target_activity)
                        print("an",agent.category,"has taken the task",target_activity,"to",target_loc)
                return
            
            category=np.random.choice([0, 1, 2], p = p.ravel())
            agent=choice(self.subordinate)
            while type(agent)!=agent_list[category]:
                agent=choice(self.subordinate) #只选择一个agent抵近
            if target_activity=='guohang':
                agent.receive(random.randint(3,10),target_activity)
            else:
                agent.receive(target_loc,target_activity)
            return

        else:#standpoint==1
            # 正式决策的时候选择Q值最小的行
            # temp=self.Q_score[self.Q_score['activity']==target_activity].sample(1)
            # arrangement=temp.iloc[0].values.tolist()[1:4]
            # 训练过程中用随机数生成
            temp=arrangement=[random.randint(0,2),random.randint(0,4),random.randint(0,4)]
            for agent in self.subordinate:
                if arrangement[agent_list.index(type(agent))]>0:
                    arrangement[agent_list.index(type(agent))]-=1
                    agent.receive(target_loc,target_activity)
            return temp
        
    def feedback(self, result):
        if result:
            self.leader.feedback(True)

    def step(self):
        pass
