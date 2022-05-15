from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import time
import json
from commander.Commander import *
from data_tools.cal_distance import *
import networkx as nx
from keras import models

class Environment(Model):
    def __init__(self, graph, arg):
        
        self.graph=graph
        self.arg=arg
        self.cnn_model=models.load_model('ABM_model.h5')

        self.commander=dict()
        self.description="This is a ABM1.0 demo with 100 training dataset."

        self.schedule=RandomActivation(self)
        commander_setting=list(self.arg.keys())
        for i in range(len(commander_setting)):
            commander=Commander(uuid.uuid1(),self,int(commander_setting[i]),self.arg[commander_setting[i]])
            self.commander[int(commander_setting[i])]=commander
            self.schedule.add(commander)

        # print("here is the initial setting")
        self.datacollector=DataCollector(
            model_reporters={
                # 侦查到的敌军行为体类型、数量、最近距离和接近时间
                'aircraft_num':lambda m: self.read_detect(m,'aircraft_num'),
                'aircraft_min_distance':lambda m: self.read_detect(m,'aircraft_mindis'),
                'warship_num':lambda m: self.read_detect(m,'warship_num'),
                'warship_min_distance':lambda m: self.read_detect(m,'warship_mindis'),
                'carrier_num':lambda m: self.read_detect(m,'carrier_num'),
                'carrier_min_distance':lambda m: self.read_detect(m,'carrier_mindis'),
                
                'activity': lambda m: self.activity(m),
            },
            agent_reporters={
                'id':"unique_id",
                'category':"category",
                'time':'timestamp',
                'standpoint':"standpoint",
                'x':"x",
                'y':"y"
            }
        )
        
        self.running = True
        self.datacollector.collect(self)
    
    def check_nodes(self):
        for i in [1,2]:
            self.graph.nodes.data()[i]['agent_list']={1:[],-1:[]}
            for agent in self.schedule.agents:
                if cal_distance(self.graph.nodes.data()[i]['Lon_Lat'],(agent.x, agent.y))<22000:
                    self.graph.nodes.data()[i]['agent_list'][agent.standpoint].append(agent)
                    if agent.standpoint==-self.graph.nodes.data()[i]['standpoint']:
                        self.commander[self.graph.nodes.data()[i]['standpoint']].warning(i)
            if len(self.graph.nodes.data()[i]['agent_list'][-1])<len(self.graph.nodes.data()[i]['agent_list'][1]):
                for agent in self.graph.nodes.data()[i]['agent_list'][-1]:
                    agent.warning=True

    def step(self):
        time.sleep(1)
        self.schedule.step()
        self.check_nodes()
        self.datacollector.collect(self)

    def read_detect(self, model, label):
        return json.dumps(float(model.commander[1].recording.iloc[-1][label]))

    def activity(self,model):
        return model.commander[-1].activity


if __name__=="__main__":
    G=nx.read_gpickle(r"./input/Dongsha_withstandpoint.gpickle")
    with open('./input/agent_setting.json','r',encoding='utf8')as fp:
        arg = json.load(fp)
    for i in range(1):
        test=Environment(G, arg)
        for j in range(60):
            # print("round",j)
            test.step()
        # 结束后通过score_1-score_-1得到我方行动的结果
        print(test.commander[1].recording)
        # agent_data=test.datacollector.get_agent_vars_dataframe()
        # print(agent_data)
        # agent_data.to_csv('./simu_recorder/trace{}.csv'.format(str(i)),index=False)
        # test.commander[1].recording.to_csv('./dete_recorder/{}{}.csv'.format(str(test.commander[-1].activity[0]),i),index=False)
