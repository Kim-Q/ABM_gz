import numpy as np
import pandas as pd

data=pd.read_csv(r'./simu_recorder/trace1.csv')
agents=list(set(list(data['id'])))
output=[]
for i in agents:
    temp=[]
    for j in range(len(data)):
        if data.iloc[j]['id']==i:
            temp.append(data.iloc[j])
    output.append(temp)
for i in range(len(output)):
    temp=pd.DataFrame(output[i])
    temp.to_csv('.//agentstrace//agent{}.csv'.format(i),index=False)