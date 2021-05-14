import datetime

from external_data.diagnose_data.disease_names import disease_names
from external_data.diagnose_data.special_departments import oldDepartment, manDepartment, womanDeparment, \
    childDepartment, \
    reprocessingDepartment
from external_data.diagnose_data.symptome_names import symptom_names
from actions.action_config import REWARD_WEIGHT, PUNISH_WEIGHT, LIST_LENGTH
from actions.functions_new import getAllDiseaseName, getdiseaseSymptomSum, getQueryRecord, getAllDiseaseInfo, \
    getEdgeValue, getRanking
import math




def getSymptomAndDisease(entity_list):
    """
    input:已识别的实体列表(List(String))
    output:症状列表(List(String))，疾病列表(List(String))
    """
    symptomList = []
    diseaseList = []
    # otherStringList = []
    # 匹配症状词和疾病词
    for item in entity_list:
        if item in symptom_names:
            symptomList.append(item)
        if item in disease_names:
            disease_names.append(item)
    dict = {
        'symptomList': symptomList,
        'diseaseList': diseaseList
    }
    return dict


def symptomToDiease(symptomList):
    """
    根据症状进行疾病诊断
    input:症状列表(List(String))
    output:疾病列表(List(String))
    """
    symptomDiseases = {}
    for symptomName in symptomList:
        getDiseaseListCypher = "MATCH (d:Disease)-[r:疾病相关症状]-(s:Symptom) where s.name='{0}' return d.name,r.count,d.age,d.sex".format(symptomName)
        results = getQueryRecord(getDiseaseListCypher)
        if results:
            symptomDiseases[symptomName] = results
    global diseaseInfo
    diseaseInfo = getAllDiseaseInfo(symptomDiseases)  # 合并所有主诉症状相关疾病的详细信息到一个列表里
    allDiseaseCount = len(diseaseInfo)  # 所有主诉症状相关疾病总数，这里是公式里的N，IDF项的分子

    # 计算症状对应的所有疾病数
    symptomToDiseaseCount = {}
    for symptomName in symptomList:
        diseaseInfoList = symptomDiseases[symptomName]
        count = len(diseaseInfoList)
        symptomToDiseaseCount[symptomName] = count  # 某一症状对应多少个疾病，公式里IDF项的分母

    # 初步计算疾病权重
    diseaseRateList = {}
    for diseaseName in diseaseInfo.keys():
        diseaseRate = 0
        diseaseSymptomWeightSum = getdiseaseSymptomSum(diseaseName)  # 这里求的是链接diseaseName的所有症状边上的权重之和，即公式中TF的分母
        for symptomName in symptomList:
            diseaseSymptomWeightSingle = getEdgeValue(symptomDiseases, symptomName, diseaseName)  # TF项的分子，单个症状和疾病的权重
            symptomDiseaseCount = symptomToDiseaseCount[symptomName]  # IDF项的分母
            # 计算某一症状相关疾病权重
            if diseaseSymptomWeightSingle > 0:
                weigth = 0
                if len(symptomList) == 1:
                    weigth = (diseaseSymptomWeightSingle / (diseaseSymptomWeightSum))
                else:
                    weigth = (diseaseSymptomWeightSingle / (diseaseSymptomWeightSum)) * math.log((allDiseaseCount) / (symptomDiseaseCount + 1), 10)
                diseaseRate += weigth  # 添加到总权重中
        diseaseRateList[diseaseName] = diseaseRate
    return diseaseRateList


def fusionDiseaseAgeSex(diseaseRateList, age, sex):
    """
    融合年龄性别等信息，排除不匹配疾病
    input:疾病列表(map(疾病名->权重)),年龄(int),性别(String)
    output:疾病列表(map(疾病名->权重))
    """
    global diseaseInfo
    errorDiseases = []
    for diseaseName, diseaseRate in diseaseRateList.items():
        if diseaseName in diseaseInfo.keys():
            diseaseAge, diseaseSex = diseaseInfo[diseaseName]
            if diseaseAge is not None:
                if (diseaseAge == "老人" and age == "儿童") or (diseaseAge == "儿童" and age == "老人") or (diseaseAge == "老人" and age == "其他") or (diseaseAge == "其他" and age == "老人") or (diseaseAge == "儿童" and age == "其他") or (diseaseAge == "其他" and age == "儿童"):
                    errorDiseases.append(diseaseName)
                    continue
            if diseaseSex is not None:
                if diseaseSex != sex:
                    errorDiseases.append(diseaseName)
    for errorDisease in errorDiseases:
        diseaseRateList.pop(errorDisease, '404')
    return diseaseRateList


def findValidSynonymyDisease(diseaseRateList):
    """
    因为有一些疾病可能连接不到科室
    input:疾病权重列表
    output:疾病权重列表（数量可能会增加）
    """
    noDepartmentDiseases = []
    synonymyDiseases = {}
    for diseaseName, diseaseRate in diseaseRateList.items():
        DiseaseToDepartmentCypher = "MATCH p=(d:Disease)-[r:`疾病相关科室`]-(lev2:Level2) where d.name='{0}' RETURN count(r)".format(
            diseaseName)
        count = getQueryRecord(DiseaseToDepartmentCypher)[0]['count(r)']
        if count == 0:
            noDepartmentDiseases.append(diseaseName)
            getSynonymyDiseaseNameCypher = "MATCH p=(d1:Disease)-[r:`疾病同义`]-(d2:Disease) where d1.name='{0}' RETURN d2.name".format(
                diseaseName)
            synonymyDiseaseNameList = getQueryRecord(getSynonymyDiseaseNameCypher)
            for synonymyDiseaseName in synonymyDiseaseNameList:
                synonymyDiseaseToDepartmentCypher = "MATCH p=(d:Disease)-[r:`疾病相关科室`]-(lev2:Level2) where d.name='{0}' RETURN count(r)".format(
                    synonymyDiseaseName['d2.name'])
                synonymyCount = getQueryRecord(synonymyDiseaseToDepartmentCypher)[0]['count(r)']
                if synonymyCount > 0:
                    synonymyDiseases[synonymyDiseaseName['d2.name']] = diseaseRate


    for noDepartmentDisease in noDepartmentDiseases:
        diseaseRateList.pop(noDepartmentDisease, '404')
    for synonymyDiseaseName, synonymyDiseaseRate in synonymyDiseases.items():
        diseaseRateList[synonymyDiseaseName] = synonymyDiseaseRate
    # diseaseRateList.update(synonymyDiseases)
    return diseaseRateList


def findUpDisease(diseaseRateList):
    """
    找到上位疾病
    """
    upDiseaseRateList = {}
    for diseaseName, diseaseRate in diseaseRateList.items():
        FindUpDiseaseCountCypher = "MATCH (d1:Disease) - [r:上下位] -> (d2:Disease) WHERE d1.name='{0}' RETURN count(d2)".format(diseaseName)
        count = getQueryRecord(FindUpDiseaseCountCypher)[0]['count(d2)']
        if count > 0:
            FindUpDiseaseCypher = "MATCH (d1:Disease) - [r:上下位] -> (d2:Disease) WHERE d1.name='{0}' RETURN d2.name".format(
                diseaseName)
            upDiseaseName = getQueryRecord(FindUpDiseaseCypher)[0]['d2.name']
            if upDiseaseName in upDiseaseRateList.keys():
                oldRate = upDiseaseRateList[upDiseaseName]
                newRate = oldRate + diseaseRate
                upDiseaseRateList[upDiseaseName] = newRate
            else:
                upDiseaseRateList[upDiseaseName] = diseaseRate
        else:
            upDiseaseRateList[diseaseName] = diseaseRate

    return upDiseaseRateList






def diseaseToDepartment(diseaseRateList):
    """
    input：疾病权重列表
    output: 科室权重列表
    """
    diseaseDepartments = {}
    for diseaseName, diseaseRate in diseaseRateList.items():
        getDiseaseDeparmentCypher = "MATCH p=(d:Disease)-[r:`疾病相关科室`]-(lev2:Level2) where d.name = '{0}' RETURN lev2.name, r.count".format(
            diseaseName)
        departmentList = getQueryRecord(getDiseaseDeparmentCypher)
        diseaseDepartmentRates = {}
        for department in departmentList:
            departmentName = department['lev2.name']
            departmentCount = department['r.count']
            departmentRate = departmentCount * diseaseRate  # 边上的count*疾病的权重
            diseaseDepartmentRates[departmentName] = departmentRate
        diseaseDepartments[diseaseName] = diseaseDepartmentRates  # 一个疾病对应N个科室 每个科室的权重

    # 融合所有疾病的科室
    departmentRateList = {}
    for diseaseName, diseaseDepartmentRates in diseaseDepartments.items():
        for departmentName, departmentRate in diseaseDepartmentRates.items():
            if departmentName in departmentRateList.keys():
                oldRate = departmentRateList[departmentName]
                newRate = oldRate + departmentRate
                departmentRateList[departmentName] = newRate
            else:
                departmentRateList[departmentName] = departmentRate

    return departmentRateList


def fusionDepartmentAgeSex(departmentRateList, age, sex):
    """
    融合年龄性别信息到科室推荐
    input: 科室权重列表, 年龄, 性别
    output: 科室权重列表
    """
    errorDepartments = []
    # specialDepartments = []
    for departmentName, departmentRate in departmentRateList.items():
        if (departmentName in oldDepartment) and (age != "老人"):
            errorDepartments.append(departmentName)
        if (departmentName in childDepartment) and (age != "儿童"):
            errorDepartments.append(departmentName)
        if (departmentName in womanDeparment) and (sex == "男"):
            errorDepartments.append(departmentName)
        if (departmentName in manDepartment) and (sex == "女"):
            errorDepartments.append(departmentName)

        # if (departmentName in oldDepartment) and (age == "老人"):
        #     specialDepartments.append(departmentName)
        # if (departmentName in childDepartment) and (age == "儿童"):
        #     specialDepartments.append(departmentName)
        # if (departmentName in womanDeparment) and (sex == "女"):
        #     specialDepartments.append(departmentName)
        # if (departmentName in manDepartment) and (sex == "男"):
        #     specialDepartments.append(departmentName)

    for errorDepartment in errorDepartments:
        departmentRateList.pop(errorDepartment, "404")
    for departmentName in reprocessingDepartment:
        departmentRateList.pop(departmentName, '404')

    # for specialDepartment in specialDepartments:
    #     oldRate = departmentRateList[specialDepartment]
    #     ranking = getRanking(departmentRateList, specialDepartment)
    #     if ranking:
    #         newRate = oldRate * math.log((ranking + 1), 10)
    #         departmentRateList[specialDepartment] = newRate

    return departmentRateList


def standarizeDepartmentRate(departmentRateList):
    """
    归一化科室权重
    input: 科室权重列表
    output: 科室权重列表
    """
    countSum = 0
    for k, v in departmentRateList.items():
        countSum = countSum + v
    if countSum > 0:
        for departmentName, departmentRate in departmentRateList.items():
            departmentRateList[departmentName] = float(departmentRate) / float(countSum)
    return departmentRateList


def detect(age, sex, entity_list):
    time1 = datetime.datetime.now()
    """
    整合所有函数，进行诊断和科室推荐
    """
    # 疾病诊断
    dict = getSymptomAndDisease(entity_list)
    symptomList = dict['symptomList']
    print(symptomList)
    diseaseRateList = symptomToDiease(symptomList)
    print(len(diseaseRateList))
    diseaseRateList = fusionDiseaseAgeSex(diseaseRateList, age, sex)
    print(len(diseaseRateList))
    diseaseRateList = findValidSynonymyDisease(diseaseRateList)
    print(len(diseaseRateList))

    # 科室推荐
    departmentRateList = diseaseToDepartment(diseaseRateList)
    departmentRateList = fusionDepartmentAgeSex(departmentRateList, age, sex)
    departmentRateList = standarizeDepartmentRate(departmentRateList)

    #科室排序
    dl = sorted(departmentRateList.items(), key=lambda item: item[1], reverse=True)
    if len(diseaseRateList) > 3:
        dl = dl[:3]
    departmentResult = {}
    for l in dl:
        departmentResult[l[0]] = l[1]

    #疾病排序
    diseaseRateList = findUpDisease(diseaseRateList)
    print(len(diseaseRateList))
    DL = sorted(diseaseRateList.items(), key=lambda item: item[1], reverse=True)
    if len(diseaseRateList) > 3:
        DL = DL[:3]
    diseaseResult = {}
    for L in DL:
        diseaseResult[L[0]] = L[1]


    time2 = datetime.datetime.now()
    print("消耗时间为：")
    print((time2 - time1).seconds)
    return diseaseResult, departmentResult


def getDiseaseRateList(age, sex, entity_list):
    # 疾病诊断
    dict = getSymptomAndDisease(entity_list)
    symptomList = dict['symptomList']
    print(symptomList)
    diseaseRateList = symptomToDiease(symptomList)
    print(len(diseaseRateList))
    diseaseRateList = fusionDiseaseAgeSex(diseaseRateList, age, sex)
    print(len(diseaseRateList))
    diseaseRateList = findValidSynonymyDisease(diseaseRateList)
    print(len(diseaseRateList))

    # 疾病排序
    DL = sorted(diseaseRateList.items(), key=lambda item: item[1], reverse=True)
    if len(diseaseRateList) > LIST_LENGTH:
        DL = DL[:LIST_LENGTH]
    diseaseResult = {}
    for L in DL:
        diseaseResult[L[0]] = L[1]
    return diseaseResult


def getDepartmentRateList(age, sex, diseaseRateList):
    # 科室推荐
    departmentRateList = diseaseToDepartment(diseaseRateList)
    departmentRateList = fusionDepartmentAgeSex(departmentRateList, age, sex)
    departmentRateList = standarizeDepartmentRate(departmentRateList)

    # 科室排序
    dl = sorted(departmentRateList.items(), key=lambda item: item[1], reverse=True)
    if len(diseaseRateList) > LIST_LENGTH:
        dl = dl[:LIST_LENGTH]
    departmentResult = {}
    for l in dl:
        departmentResult[l[0]] = l[1]
    return departmentResult


def get_new_symptoms(departmentName, symptomList):
    """
        得知科室列表，要加高第一名科室的权重
        input:  str            第一名科室
                List[str]      症状列表
        output: List[str]      问询症状列表
    """
    newSymptomRateList = {}
    getNewSymptomCypher = "match (l:Level2) - [r2:疾病相关科室] - (d:Disease) - [r1:疾病相关症状] - (s:Symptom) where l.name='{0}' return s.name, r1.count*r2.count as weight order by weight desc".format(departmentName)
    results = getQueryRecord(getNewSymptomCypher)
    for item in results:
        symptomName = item['s.name']
        weight = item['weight']
        newSymptomRateList[symptomName] = weight

    DL = sorted(newSymptomRateList.items(), key=lambda item: item[1], reverse=True)
    symptomResult = {}
    for L in DL:
        symptomResult[L[0]] = L[1]

    for excluded_symptom in symptomList:
        symptomResult.pop(excluded_symptom, '404')

    n = 3
    if len(symptomResult) >= n:
        res = {k: symptomResult[k] for k in list(symptomResult.keys())[:n]}  # 字典切片
        return list(res.keys())
    return list(symptomResult.keys())


def qiulei_get_new_symptoms(diseaseNameList, symptomList, failedSymptomList):
    """
        得知科室列表，要加高第一名科室的权重
        input:  list[str]      疾病列表
                List[str]      现存症状列表
        output: List[str]      问询症状列表
    """
    # 计算每个症状的count，存入dict
    newSymptomRateList = {}
    for diseaseName in diseaseNameList:
        getNewSymptomCypher = "match (s:Symptom) - [r:疾病相关症状] - (d:Disease) where d.name = '{0}' return s.name".format(diseaseName)
        results = getQueryRecord(getNewSymptomCypher)
        for item in results:
            symptomName = item['s.name']
            if symptomName not in newSymptomRateList.keys():
                newSymptomRateList[symptomName] = 1
            else:
                newSymptomRateList[symptomName] = newSymptomRateList[symptomName] + 1

    # symptomResult是根据count倒序排序的dict
    DL = sorted(newSymptomRateList.items(), key=lambda item: item[1], reverse=True)
    symptomResult = {}
    for L in DL:
        symptomResult[L[0]] = L[1]

    # 剔除已有的症状
    for excluded_symptom in symptomList:
        symptomResult.pop(excluded_symptom, '404')

    # 剔除已询问过的症状
    if failedSymptomList and len(failedSymptomList)>0:
        for excluded_symptom in failedSymptomList:
            symptomResult.pop(excluded_symptom, '404')

    # 只选择count数前1的症状
    n = 1
    if len(symptomResult) >= n:
        res = {k: symptomResult[k] for k in list(symptomResult.keys())[:n]}  # 字典切片
        return list(res.keys())
        # return res
    return list(symptomResult.keys())
    # return symptomResult


def getRewardRateList(diseaseNameList, failedSymptom):
    """
        根据否认症状，对疾病权重进行奖惩
        input:  List(String) 当前科室列表
                String       否认症状名
        output: Dict(String, Float) RewardRateList奖惩列表
    """
    rewardRateList = {}
    for diseaseName in diseaseNameList:
        cypher = "match (s:Symptom) - [r:疾病相关症状] - (d:Disease) where s.name='{0}' and d.name='{1}' return r.count".format(failedSymptom, diseaseName)
        res = getQueryRecord(cypher)
        # 无权重，疾病与否认症状无关
        if len(res) == 0:
            if diseaseName in rewardRateList.keys():
                rewardRateList[diseaseName] = rewardRateList[diseaseName] + REWARD_WEIGHT
            else:
                rewardRateList[diseaseName] = REWARD_WEIGHT
        # 有权重，疾病与否认症状有关
        else:
            if diseaseName in rewardRateList.keys():
                rewardRateList[diseaseName] = rewardRateList[diseaseName] + PUNISH_WEIGHT
            else:
                rewardRateList[diseaseName] = PUNISH_WEIGHT

    return rewardRateList

