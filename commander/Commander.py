import pandas as pd
from mesa import Agent
import random
from random import choice
import uuid
from second.Jidi import *
from data_tools.cal_distance import *
from datetime import datetime

agent_list=[Jidi]
activity=['guohang','dijin','zhencha','yanxi','xunlian']


class Commander(Agent):
    def __init__(self,unique_id,model,standpoint,arg:dict):
        super().__init__(unique_id,model)
        self.subordinate=[]
        self.standpoint=standpoint
        self.activity=[]
        self.x,self.y=0,0
        # print("I'm an initial commander",str(self.unique_id),"with standpoint", str(self.standpoint),"I have",str(len(arg)),"basements.")
        self.category="commander"
        self.timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.recording=pd.DataFrame({'aircraft_num':[],'aircraft_mindis':[],'warship_num':[],'warship_mindis':[],'carrier_num':[],'carrier_mindis':[]})
        temp_recording=[0,0,0,0,0,0]
        self.recording.loc[len(self.recording.index)]=temp_recording

        self.target_loc=[]
        self.target_activity=[]
        self.urgency=[]
        if self.standpoint==-1:
            appointment=choice(activity)
            self.activity.append(appointment)
            self.target_activity.append(appointment)
            if appointment=='xunlian':
                self.target_activity.append(appointment)
                self.target_loc=[1,2]
            else:
                self.target_loc.append((choice([1,2])))
            # print(self.target_activity,self.target_loc)

        for i in range(len(arg)):
            agent=Jidi(uuid.uuid1(),self.model,self,arg[i][0],self.standpoint,arg[i][1])
            self.subordinate.append(agent)
            self.model.schedule.add(agent)


        # self.urgency=False

    def deploy(self):
        # 指挥
        for i in range(len(self.subordinate)):
            self.subordinate[i].receive(choice(self.target_loc))

    def warning(self, node):
        # standpoint=1阵营的功能
        if node not in self.urgency:
            self.urgency.append(node)     
    
    def step(self):
        if self.standpoint==-1 and len(self.target_loc)>0:
            for i in range(len(self.subordinate)):
                if len(self.target_loc)>0 and random.random()<(1/(len(self.subordinate)-i-len(self.target_loc)+1)):
                    # print("deploy the appointment of",str(self.target_activity[0]),"to",str(self.target_loc[0]))
                    self.subordinate[i].deploy(self.target_loc.pop(),self.target_activity.pop())
            return

        if self.standpoint==1 and len(self.urgency)>0:
            temp=[0,0,0,0,0,0] 
            for node in self.urgency:
                loc=self.model.graph.nodes.data()[node]['Lon_Lat']
                print(len(self.model.graph.nodes.data()[node]['agent_list']))
                for agent in self.model.graph.nodes.data()[node]['agent_list']:
                    if agent.standpoint==-self.standpoint and agent.category=='aircraft':
                        temp[0]+=1
                        temp[1]=float('inf') if temp[1]==0 else temp[1]
                        temp[1]=cal_distance((agent.x,agent.y),loc) if cal_distance((agent.x,agent.y),loc)<temp[1] else temp[1]
                    elif agent.standpoint==-self.standpoint and agent.category=='warship':
                        temp[2]+=1
                        temp[3]=float('inf') if temp[3]==0 else temp[3]
                        temp[3]=cal_distance((agent.x,agent.y),loc) if cal_distance((agent.x,agent.y),loc)<temp[3] else temp[3]
                    elif agent.standpoint==-self.standpoint and agent.category=='carrier':
                        temp[4]+=1
                        temp[5]=float('inf') if temp[5]==0 else temp[5]
                        temp[5]=cal_distance((agent.x,agent.y),loc) if cal_distance((agent.x,agent.y),loc)<temp[5] else temp[5]
            self.recording.loc[len(self.recording.index)]=temp
            self.urgency=[]

        elif self.standpoint==1:
            self.recording.loc[len(self.recording.index)]=[0,0,0,0,0,0] 

