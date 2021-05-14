from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, UserUtteranceReverted
from actions.diagnose_new import detect, qiulei_get_new_symptoms, getRewardRateList, getDiseaseRateList, getDepartmentRateList
from actions.action_config import WEIGHT_DIFFERENCE, WEIGTH_TOP, MAX_SYMPTOM_NUM, LIST_LENGTH


class ActionGetInformation(Action):
    """
    获取所有个人信息
    """

    def name(self) -> Text:
        return "action_get_information"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 询问年龄槽
        age = tracker.get_slot("age")
        if age is None:
            dispatcher.utter_message(template="utter_ask_age")
            return []

        # 询问性别
        sex = tracker.get_slot("sex")
        if sex is None:
            dispatcher.utter_message(template="utter_ask_sex")
            return []

        # 询问症状槽
        it = tracker.get_latest_entity_values("symptom")
        try:
            next(it)
        except StopIteration:
            dispatcher.utter_message(template="utter_ask_symptom")
            return []


class ActionSetAge(Action):
    def name(self) -> Text:
        return "action_set_age"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        age = tracker.latest_message['text']
        print(age)
        return [SlotSet("age", age)]


class ActionSetSex(Action):
    def name(self) -> Text:
        return "action_set_sex"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        sex = tracker.latest_message['text']
        print(sex)
        return [SlotSet("sex", sex)]


class ActionSetSymptoms(Action):
    def name(self) -> Text:
        return "action_set_symptoms"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        it = tracker.get_latest_entity_values("symptom")
        symptoms = []
        while True:
            try:
                x = next(it)  # 获取一个数据并绑定到x
                symptoms.append(str(x))
            except StopIteration:
                if len(symptoms) > 0:
                    return [SlotSet("symptomList", symptoms)]
                else:
                    return []


class ActionDiagnose(Action):

    def name(self) -> Text:
        return "action_diagnose"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # 获取个人信息槽
        entity_list = tracker.get_slot("symptomList")
        age = tracker.get_slot("age")
        sex = tracker.get_slot("sex")
        newSymptomList = tracker.get_slot("newSymptomList")
        DiseaseRateList = tracker.get_slot("diseaseRateList")
        # DepartmentRateList = tracker.get_slot("departmentRateList")
        isUpdated = tracker.get_slot("isUpdated")

        diseaseRateList = {}
        # 如果newSymptomList结果为空，代表第一次诊断；或者症状列表已经更新，代表需要新诊断
        if (newSymptomList is None and isUpdated is None) or isUpdated:
            # 如果当前症状列表不为空，再进行诊断
            if entity_list and len(entity_list) > 0:
                diseaseRateList = getDiseaseRateList(age, sex, entity_list)
        else:  # 进入问询阶段且症状列表没有更新
            RewardRateList = tracker.get_slot("rewardRateList")
            #  合并疾病权重列表和奖惩列表
            from collections import Counter
            diseaseRateList = dict(Counter(DiseaseRateList) + Counter(RewardRateList))
            #  还是只取前3
            DL = sorted(diseaseRateList.items(), key=lambda item: item[1], reverse=True)
            if len(diseaseRateList) > LIST_LENGTH:
                DL = DL[:LIST_LENGTH]
            diseaseResult = {}
            for L in DL:
                diseaseResult[L[0]] = L[1]
            diseaseRateList = diseaseResult

        # 如果高于阈值——诊断效果良好，或者是症状词>=5，不用添加新症状列表，推荐科室直接结束
        if list(diseaseRateList.values())[0] >= WEIGTH_TOP or (
                list(diseaseRateList.values())[0] - list(diseaseRateList.values())[1]) >= WEIGHT_DIFFERENCE or len(
                entity_list) >= MAX_SYMPTOM_NUM:
            departmentRateList = getDepartmentRateList(age, sex, diseaseRateList)
            return [SlotSet("diseaseRateList", diseaseRateList if diseaseRateList is not None else []),
                    SlotSet("departmentRateList", departmentRateList if departmentRateList is not None else [])]
        else:  # 低于阈值，效果不好，要进行新症状询问，添加新症状列表
            failedSymptomList = tracker.get_slot("failedSymptomList")
            new_symptoms = qiulei_get_new_symptoms(list(diseaseRateList.keys()), entity_list, failedSymptomList)
            return [SlotSet("newSymptomList", new_symptoms if new_symptoms is not None else []),
                    SlotSet("diseaseRateList", diseaseRateList if diseaseRateList is not None else [])]


class ActionShowResult(Action):
    def name(self) -> Text:
        return "action_show_result"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        DiseaseRateList = tracker.get_slot("diseaseRateList")
        DepartmentRateList = tracker.get_slot("departmentRateList")

        # 如果已经生成了推荐科室，导诊结束
        if DepartmentRateList is not None and len(DepartmentRateList) > 0:
            final_disease = list(DiseaseRateList.keys())[0]
            final_department = list(DepartmentRateList.keys())[0]
            dispatcher.utter_message(text="本次导诊最终推荐科室为{0}。诊断疾病可能是{1}。".format(final_department, final_disease))
        # 没生成推荐科室，需要继续问询
        else:
            newSymptomList = tracker.get_slot("newSymptomList")
            # 新症状列表有内容继续问询
            if newSymptomList and len(newSymptomList) > 0:
                nextSymptom = newSymptomList[0]
                dispatcher.utter_message(text="您是否有{}的症状？".format(nextSymptom))
            # 新症状列表存在，但是内容已经空了，出现异常
            else:
                final_disease = list(DiseaseRateList.keys())[0]
                final_department = list(DepartmentRateList.keys())[0]
                dispatcher.utter_message(text="系统问询异常结束...本次导诊最终推荐科室为{0}。诊断疾病可能是{1}。".format(final_department, final_disease))

        return []


class ActionSetNewSymptom(Action):

    def name(self):
        return "action_set_new_symptom"

    def run(self, dispatcher, tracker, domain):

        reply = tracker.latest_message['intent']['name']
        newSymptomList = tracker.get_slot("newSymptomList")
        # 用户确定有此症状，加入新症状，更新状态True
        if reply == "affirm":
            symptomList = tracker.get_slot("symptomList")
            symptomList.append(newSymptomList.pop(0))
            return [SlotSet("symptomList", symptomList),
                    SlotSet("newSymptomList", newSymptomList),
                    SlotSet("isUpdated", True)]
        # 用户否认有此症状，更新状态false，记录奖惩信息
        else:
            failedSymptom = newSymptomList.pop(0)
            DiseaseRateList = tracker.get_slot("diseaseRateList")
            rewardRateList = getRewardRateList(list(DiseaseRateList.keys()), failedSymptom)

            # 问过的症状也保存
            failedSymptomList = tracker.get_slot("failedSymptomList")
            if failedSymptomList is not None:
                failedSymptomList.append(failedSymptom)
            else:
                failedSymptomList = [failedSymptom]

            # 填入奖惩列表
            return [SlotSet("newSymptomList", newSymptomList),
                    SlotSet("isUpdated", False),
                    SlotSet("rewardRateList", rewardRateList),
                    SlotSet("failedSymptomList", failedSymptomList)]


class ActionChitchat(Action):
    """
    chitchat时自动回复
    """

    def name(self):
        return "action_chitchat"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="我们还是回归导诊吧，可以陈述一下您的症状。")
        return [UserUtteranceReverted()]
