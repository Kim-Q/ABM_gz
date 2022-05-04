import json

# 两方阵营立场分别为1和-1，各有两个Jidi（二级agent），每个Jidi各有4个Template（三级agent）
agent_dict={
    "1":[
        {
            0:4
        },
        {
            0:4
        }
    ],
    "-1":[
        {
            0:4
        },
        {
            0:4
        }
    ]
}

with open(".//input//agent_setting.json", "w") as f:
    f.write(json.dumps(agent_dict, ensure_ascii=False, indent=4, separators=(',', ':')))

# with open('.//input//agent_setting.json','r',encoding='utf8')as fp:
#     json_data = json.load(fp)
# print(json_data)