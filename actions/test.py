# from py2neo import Graph, Node, Relationship
from actions.diagnose_new import qiulei_get_new_symptoms
#
#
# def get_new_symptoms(departmentName, symptomList):
#     """
#         得知科室列表，要加高第一名科室的权重
#         input:  str            第一名科室
#                 List[str]      症状列表
#         output: List[str]      问询症状列表
#     """
#     newSymptomRateList = {}
#     getNewSymptomCypher = "match (l:Level2) - [r2:疾病相关科室] - (d:Disease) - [r1:疾病相关症状] - (s:Symptom) where l.name='{0}' return s.name, r1.count*r2.count as weight order by weight desc".format(departmentName)
#     results = getQueryRecord(getNewSymptomCypher)
#     for item in results:
#         symptomName = item['s.name']
#         weight = item['weight']
#         newSymptomRateList[symptomName] = weight
#
#     DL = sorted(newSymptomRateList.items(), key=lambda item: item[1], reverse=True)
#     symptomResult = {}
#     for L in DL:
#         symptomResult[L[0]] = L[1]
#
#     for excluded_symptom in symptomList:
#         symptomResult.pop(excluded_symptom, '404')
#
#     n = 3
#     if len(symptomResult) >= n:
#         res = {k: symptomResult[k] for k in list(symptomResult.keys())[:n]}  # 字典切片
#         return list(res.keys())
#     return list(symptomResult.keys())
#
# diseaseNameList = ["糖尿病","膀胱炎","尿道综合征","尿失禁"]
# symptomList = ['尿频', '尿急']
# res = qiulei_get_new_symptoms(diseaseNameList, symptomList)
# print(res)

# x = { 'apple': 1, 'banana': 2 }
# y = { 'banana': 10, 'pear': 11 }
# from collections import Counter
# z = dict(Counter(x)+Counter(y))
# print(z)
# from actions.functions_new import getQueryRecord
#
# failedSymptom = "恶心"
# diseaseName = "梅尼埃病"
# cypher = "match (s:Symptom) - [r:疾病相关症状] - (d:Disease) where s.name='{0}' and d.name='{1}' return r.count".format(failedSymptom, diseaseName)
# res = getQueryRecord(cypher)
# print(len(res))
aa ="abc"
a = [aa]
print(a)