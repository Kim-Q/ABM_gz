import pandas as pd
from mesa import Agent
import random
from random import choice
import uuid
from second.Jidi import *
from data_tools.cal_distance import *
from datetime import datetime
# import datedelta
from keras import models

agent_list=[Jidi]
activity_A=['guohang','dijin','zhencha','yanxi','xunlian']
activity_C=['ignore','ganrao','quzhu']

# 行动成功所获奖励分数
activity_score={'guohang':1,'dijin':4,'zhencha':4,'yanxi':10,'xunlian':20}

class Commander(Agent):
    def __init__(self,unique_id,model,standpoint,arg:dict):
        super().__init__(unique_id,model)
        self.subordinate=[]
        self.standpoint=standpoint
        self.activity=None
        self.result=False
        self.x,self.y=0,0
        # print("I'm an initial commander",str(self.unique_id),"with standpoint", str(self.standpoint),"I have",str(len(arg)),"basements.")
        self.category="commander"
        self.timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.recording=pd.DataFrame({'aircraft_num':[],'aircraft_mindis':[],'warship_num':[],'warship_mindis':[],'carrier_num':[],'carrier_mindis':[]})
        temp_recording=[0,0,0,0,0,0]
        self.recording.loc[len(self.recording.index)]=temp_recording
        if self.standpoint==1:
            self.predict=None
            self.strategy=None
            self.score_Q=np.zeros((5,4))
            self.times_Q=np.zeros((5,4))

        self.target_loc=[]
        self.target_activity=[]
        self.urgency=None
        if self.standpoint==-1:
            ###############################
            self.activity=choice(activity_A)
            ###############################
            self.target_activity.append(self.activity)
            if self.activity=='xunlian':
                self.target_activity.append(self.activity)
                self.target_loc=[1,2]
            else:
                self.target_loc.append((choice([1,2])))
            # print(self.target_activity,self.target_loc)
            # print(str(self.target_activity[0]))
            # print(str(self.model.graph.nodes.data()[self.target_loc[0]]['name']))
            message="American plan to take the "+str(self.target_activity[0])+ " activity to "+ str(self.model.graph.nodes.data()[self.target_loc[0]]['name'])+'\n'
            self.model.text+=message
            print(self.model.text)

        for i in range(len(arg)):
            agent=Jidi(uuid.uuid1(),self.model,self,arg[i][0],self.standpoint,arg[i][1])
            self.subordinate.append(agent)
            self.model.schedule.add(agent)

        # self.score=0
        self.Q_score=pd.DataFrame({'activity':[],'Carrier':[],'Warship':[],'Aircraft':[],'score':[]})
        self.Q_times=pd.DataFrame({'activity':[],'Carrier':[],'Warship':[],'Aircraft':[],'times':[]})

        if self.standpoint==1:
            ### 下面是生成矩阵的过程，训练过后再删
            self.arrangement=[0,0,0]
            Cartesian=[activity_C[1:],range(2),range(4),range(4)]
            values=[d for d in itertools.product(*Cartesian)]
            for v in values:
                value=[i for i in v]
                # print(value,type(value))
                value.append(0)
                self.Q_score.loc[len(self.Q_score.index)]=value
                self.Q_times.loc[len(self.Q_times.index)]=value

    # def deploy(self):
    #     # 指挥
    #     for i in range(len(self.subordinate)):
    #         self.subordinate[i].receive(choice(self.target_loc))

    def warning(self, node):
        # standpoint=1阵营的功能
        if self.urgency!=node:
            self.urgency=node

    def feedback(self):
        if self.standpoint==-1:
            self.result=True
            for agent in self.subordinate:
                if agent.result!=True or len(agent.arranged_agents)!=0:
                    self.result=False
            return [self.activity,self.result]
        else:
            if self.predict!=None:
                return activity_A[self.predict]
            else:
                return 'undetected'
    
    def step(self):
        if self.standpoint==-1 and len(self.target_loc)>0:
            for i in range(len(self.subordinate)):
                if len(self.target_loc)>0 and random.random()<(1/(len(self.subordinate)-i-len(self.target_loc)+1)):
                    # print("deploy the appointment of",str(self.target_activity[0]),"to",str(self.target_loc[0]))
                    self.subordinate[i].deploy(self.target_loc.pop(),self.target_activity.pop())
            return

        if self.standpoint==1 and self.urgency!=None: 
            loc=self.model.graph.nodes.data()[self.urgency]['Lon_Lat']
            if len(self.model.graph.nodes.data()[self.urgency]['agent_list'][-1])>0:
                temp=[0,0,0,0,0,0]
                for agent in self.model.graph.nodes.data()[self.urgency]['agent_list'][-1]:
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
            # 判断当前的recording能否做预测
            i=0
            while self.recording.iloc[i][0]==0 and self.recording.iloc[i][2]==0 and self.recording.iloc[i][4]==0:
                i+=1
            if self.strategy==None and i<90-10 and len(self.recording)>=i+10 :
                X=np.zeros((10,6))
                for j in range(10):
                    X[j]=(self.recording.iloc[i+j])
                X= np.array(X, dtype = float).reshape(1,10,6,1)
                y_predict = self.model.cnn_model.predict(X)
                self.predict=np.argmax(y_predict)
                message="We have predict the oppose task is :"+str(activity_A[self.predict])+'\n'
                self.model.text+=message
                print(self.model.text)
                # print("We have predict the oppose task is :", activity_A[self.predict])
                # 'guohang','dijin','zhencha','yanxi','xunlian'/'ignore','ganrao','quzhu'
                self.strategy=0 if self.predict==0 else 1 if (self.predict==1 or self.predict==2) else 2
                message="And China takes the strategy of "+str(activity_C[self.strategy])+'\n'
                self.model.text+=message
                print(self.model.text)
                # print("C takes the strategy of ",activity_C[self.strategy])
                if self.strategy!=0:
                    self.arrangement=self.subordinate[0].deploy(self.urgency,activity_C[self.strategy])
                    print(self.arrangement)            
            self.urgency=None

        elif self.standpoint==1 and self.urgency==None:
            self.recording.loc[len(self.recording.index)]=[0,0,0,0,0,0] 


