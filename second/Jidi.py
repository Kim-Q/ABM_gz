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


agent_list=[Carrier, Warship, Aircraft]
activity=['guohang','dijin','zhencha','yanxi','xunlian']


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

    def receive(self, target, order):
        self.target_loc.insert(0,target)
        self.target_activity.insert(0,order)
        self.deploy()

    def deploy(self,target_loc,target_activity):
        self.activity.append(target_activity)
        if target_activity=='guohang':
            p = np.array([0.2, 0.3, 0.5]) #选择过航的agent类型的概率不同
            category=np.random.choice([0, 1, 2], p = p.ravel())
            agent=choice(self.subordinate)
            while type(agent)!=agent_list[category]:
                agent=choice(self.subordinate) #只选择一个agent抵近
            agent.receive(random.randint(3,10),target_activity)
            # print(str(agent.category),"receive the deployment of", target_activity)
        elif target_activity=='dijin':
            p = np.array([0.1, 0.2, 0.7]) #选择抵近的agent类型的概率不同
            category=np.random.choice([0, 1, 2], p = p.ravel())
            agent=choice(self.subordinate)
            while type(agent)!=agent_list[category]:
                agent=choice(self.subordinate) #只选择一个agent抵近
            agent.receive(target_loc,target_activity)
            # print(str(agent.category),"receive the deployment of", target_activity)
            # return
        elif target_activity=='zhencha':
            p = np.array([0.0, 0.1, 0.9]) #选择抵近的agent类型的概率不同
            category=np.random.choice([0, 1, 2], p = p.ravel())
            agent=choice(self.subordinate)
            while type(agent)!=agent_list[category]:
                agent=choice(self.subordinate) #只选择一个agent抵近
            agent.receive(target_loc,target_activity)
            print(str(agent.category),"receive the deployment of", target_activity)
            # return
        elif target_activity=='yanxi':
            for agent in self.subordinate:
                if random.random()<0.3:
                    agent.receive(target_loc,target_activity)
                    # print(str(agent.category),"receive the deployment of", target_activity)
        elif target_activity=='xunlian':
            for agent in self.subordinate:
                if random.random()<0.3:
                    agent.receive(target_loc,target_activity)
                    # print(str(agent.category),"receive the deployment of", target_activity)
        
    def feedback(self, loc):
        # print("Jidi receive the rescue requirement and did nothing.")
        pass

    def step(self):
        pass
