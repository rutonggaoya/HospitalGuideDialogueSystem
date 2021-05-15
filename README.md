# 医疗导诊对话系统
### 项目介绍：
本系统是应用于医院导诊的线上对话系统，通过与病人对话收集其基本信息和症状信息，通过导诊决策算法对病人做出科室推荐，并辅以初步的疾病诊断。

### 运行环境：
python==3.6
tensorflow==1.15.2
rasa==1.6.1 
rasa-nlu-gao==1.0.3
py2neo==4.3.0
keras==2.3.1

### 项目启动命令:
```
python -m rasa run --port 5005 --endpoints endpoints.yml --credentials credentials.yml --model models/20200525-195841.tar.gz --debug
python -m rasa run actions --actions actions --debug
python server.py
```

### API调用：
请求格式 GET http://127.0.0.1:8088/ai?content=用户语句
```
响应数据格式
{
    type:["text"|"sex"|"age"], // 代表消息内容的类型
    text:"xxxx"              // 导诊系统返回的信息
}
```

### 提示：
该系统的决策算法依赖于neo4j构建的医疗知识图谱，由于该知识图谱为实验室内部数据，暂无法公开。