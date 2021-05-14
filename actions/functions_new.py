import datetime

from py2neo import Graph, Node, Relationship


# 查询测试样例
def query_example():
    graph = Graph("bolt://localhost:7686", auth=("", ""))
    cphyer = "MATCH p=(d:Disease)-[r:`疾病相关科室`]-(lev2:Level2) where d.name='感冒' RETURN count(r)"
    result = graph.run(cphyer).data()
    print(type(result), len(result))
    print(result[0])


def getQueryRecord(cypher):
    """
    input:查询语句cypher(String)
    output:查询结果(Json)
    """
    graph = Graph("bolt://localhost:7686", auth=("", ""))
    results = graph.run(cypher).data()
    return results
# time1 = datetime.datetime.now()
# print(getQueryRecord("MATCH p=(d:Disease)-[r:疾病相关症状]-(s:Symptom) where s.name='失眠' return count(d)"))
# time2 = datetime.datetime.now()
# print((time2-time1).microseconds / 1000000)


def getdiseaseSymptomSum(diseaseName):
    """
    input: 疾病名(String)
    output: 疾病所有相关症状边上的权重之和(Int)
    """
    cypher = "MATCH p=(d:Disease)-[r:疾病相关症状]-(s:Symptom) where d.name='{0}' return sum(r.count)".format(diseaseName)
    result = getQueryRecord(cypher)
    sum = 0
    if result:
        sum = result[0]['sum(r.count)']
    return sum


def getAllDiseaseInfo(symptomDiseases):
    """
    input: 症状-相关疾病对照表(List(map(key:症状(String),value:相关疾病列表(List)))
    output: 疾病信息表(map(key:疾病(String),value:疾病信息(String,String)))
    """
    diseaseNames = {}
    for symptomName, diseaseInfoList in symptomDiseases.items():
        for disease in diseaseInfoList:
            name = disease['d.name']
            if name not in diseaseNames.keys():
                age = disease['d.age']
                sex = disease['d.sex']
                diseaseNames[name] = age, sex
    return diseaseNames


def getAllDiseaseName(symptomDiseases):
    """
    input: 症状-相关疾病对照表(List(map(key:症状(String),value:相关疾病列表(List)))
    output: 所有相关疾病列表(list(String))
    """
    diseaseNames = []
    for symptomName, diseaseInfoList in symptomDiseases.items():
        for disease in diseaseInfoList:
            name = disease['d.name']
            if name not in diseaseNames:
                diseaseNames.append(name)
    return diseaseNames


def getEdgeValue(symptomDiseases, symptomName, diseaseName):
    """
    这里是diseaseName和symptomName之间的权重，即为公式中TF项的分子
    """
    diseaseInfoList = symptomDiseases[symptomName]
    for disease in diseaseInfoList:
        name = disease['d.name']
        if name == diseaseName:
            return disease['r.count']
    return 0


def getRanking (list, rankingName):
    results = sorted(list.items(), key=lambda x: x[1], reverse=True)
    i = 1
    for k, v in results:
        if k == rankingName:
            return i
        i += 1
    return False
