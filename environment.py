from unicodedata import category
from click import command
from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import time
import json
from commander.Commander import *
from data_tools.cal_distance import *
import networkx as nx
from keras import models

activity_A=['guohang','dijin','zhencha','yanxi','xunlian']
activity_C=['ignore','ganrao','quzhu']
class Environment(Model):
    def __init__(self, graph, arg, cnn_model, Q_score, Q_times):
        
        self.graph=graph
        self.arg=arg
        self.cnn_model=cnn_model
        self.Q_score=Q_score
        self.Q_time=Q_times
        self.message=pd.DataFrame({'timestamp':[],'message':[]})
        self.text=""
        # self.message.loc[len(self.message.index)]=[datetime.now().strftime("%Y-%m-%d %H:%M:%S"),""]


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
                if agent.category!="basement" and agent.category!="commander" and cal_distance(self.graph.nodes.data()[i]['Lon_Lat'],(agent.x, agent.y))<42000:
                    self.graph.nodes.data()[i]['agent_list'][agent.standpoint].append(agent)
                    if agent.standpoint==-self.graph.nodes.data()[i]['standpoint']:
                        self.commander[self.graph.nodes.data()[i]['standpoint']].warning(i)
            # 当节点出现双方阵营时，判断各自的行为是否成功
            if 0<len(self.graph.nodes.data()[i]['agent_list'][-1])<=len(self.graph.nodes.data()[i]['agent_list'][1]):
                # print("have detect the situation",self.commander[1].recording)
                for agent in self.graph.nodes.data()[i]['agent_list'][-1]:
                    # print(agent.category,"has been warned")
                    agent.warning=True
                    # 这段有问题 一直不能示警 另外还要添加受干扰的标准
            elif 0>len(self.graph.nodes.data()[i]['agent_list'][-1]):
                for agent in self.graph.nodes.data()[i]['agent_list'][1]:
                    # print(agent.category,"has been unwarned")
                    agent.warning=False

    def step(self):
        time.sleep(1)
        self.schedule.step()
        self.check_nodes()
        self.datacollector.collect(self)

    def read_detect(self, model, label):
        return json.dumps(float(model.commander[1].recording.iloc[-1][label]))

    def activity(self,model):
        return model.commander[-1].activity

# 参数可改
agent_cost={'Carrier':10, 'Warship':4, 'Aircraft':1}
activity_cost={'guohang':1,'dijin':4,'zhencha':4,'yanxi':10,'xunlian':20}
def cal_Q(Q_score,Q_times,A_activity,C_predict,C_arrangement,A_result):
    agent_list=list(agent_cost.keys())
    score=-activity_cost[A_activity] if A_result else 0
    for i in range(len(C_arrangement)):
        for _ in range(C_arrangement[i]):
            score-=agent_cost[agent_list[i]]

    columns=list(Q_score.columns)
    values=[i for i in C_arrangement]
    values.insert(0,C_predict)
    # print(columns,values)
    Q=''
    Q+=columns[0]+'=='+'\"'+values[0]+'\"'+' & '
    for i in range(1,len(columns)-1):
        Q+=columns[i]+'=='+str(values[i])+' & '
    Q=Q[:-3]
    # print(Q)

    index=Q_score.query(Q).index[0]
    # print(Q_score.iloc[index]['score'],Q_times.iloc[index]['times'])
    Q_score.iat[index,4]=0 if Q_score.iat[index,4]==-float('inf') else Q_score.iat[index,4]
    Q_times.iat[index,4]=0 if Q_times.iat[index,4]==-float('inf') else Q_times.iat[index,4]
    Q_score.iat[index,4]=(Q_score.iat[index,4]*Q_times.iat[index,4]+score)/(1+Q_times.iat[index,4])
    Q_times.iat[index,4]+=1
    return Q_score,Q_times

if __name__=="__main__":
    G=nx.read_gpickle(r"./input/Dongsha_withstandpoint.gpickle")
    with open('./input/agent_setting.json','r',encoding='utf8')as fp:
        arg = json.load(fp)

    # Q_score=pd.DataFrame({'predict':[],'Carrier':[],'Warship':[],'Aircraft':[],'score':[]})
    # Q_times=pd.DataFrame({'predict':[],'Carrier':[],'Warship':[],'Aircraft':[],'times':[]})
    # predict=copy.deepcopy(activity_A)
    # predict.insert(0,'undetected')
    # Cartesian=[predict,range(3),range(5),range(5)]
    # # print(Cartesian)
    # values=[d for d in itertools.product(*Cartesian)]
    # for v in values:
    #     value=[i for i in v]
    #     # print(value,type(value))
    #     value.append(-float('inf'))
    #     Q_score.loc[len(Q_score.index)]=value
    #     Q_times.loc[len(Q_times.index)]=value
    
    cnn_model=models.load_model('ABM_model.h5')
    Q_score=pd.read_csv('Q_score.csv')
    Q_times=pd.read_csv('Q_times.csv')

    for i in range(1):
        print(i)
        test=Environment(G, arg, cnn_model, Q_score, Q_times)
        for j in range(90):
            # print("round",j)
            test.step()
            test.message.loc[len(test.message.index)]=[datetime.now().strftime("%Y-%m-%d %H:%M:%S"),test.text]
            test.text=""

        resultA=test.commander[-1].feedback()
        resultC=test.commander[1].feedback()
        # print(activity_A[test.commander[1].predict])
        # print(resultA[0])
        # print(activity_A[test.commander[1].predict])
        # print(test.commander[1].arrangement)
        # print(resultA[1])
        Q_score,Q_times=cal_Q(Q_score,Q_times,resultA[0],resultC,test.commander[1].arrangement,resultA[1])

        agent_data=test.datacollector.get_agent_vars_dataframe()
        model_data=test.datacollector.get_model_vars_dataframe()
        agent_data.to_csv('./trace{}.csv'.format(str(i)),index=False)
        model_data.to_csv('./{}{}.csv'.format(str(test.commander[-1].activity),i),index=False)
        test.message.to_csv('text.csv',index=False)
        # agent_data.to_csv('./simu_recorder/trace{}.csv'.format(str(i)),index=False)
        # model_data.to_csv('./dete_recorder/{}{}.csv'.format(str(test.commander[-1].activity),i),index=False)        

    
    Q_score.to_csv('Q_score.csv',index=False)
    Q_times.to_csv('Q_times.csv',index=False)
