# 医疗导诊对话系统
### 项目介绍：
本系统是应用于医院导诊的线上对话系统，通过与病人对话收集其基本信息和症状信息，通过导诊决策算法对病人做出科室推荐，并辅以初步的疾病诊断。



### 项目后端启动命令:
```
python -m rasa run --port 5005 --endpoints endpoints.yml --credentials credentials.yml --model models/20200525-195841.tar.gz --debug
python -m rasa run actions --actions actions --debug
python server.py
```