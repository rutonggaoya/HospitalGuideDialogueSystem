from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, UserUtteranceReverted
from actions.diagnose_new import detect, get_new_symptoms


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
        DepartmentRateList = tracker.get_slot("departmentRateList")
        isUpdated = tracker.get_slot("isUpdated")

        # 如果三个列表诊断结果全空DiseaseRateList DepartmentRateList newSymptomList，代表初次诊断
        if (DiseaseRateList is None or DepartmentRateList is None) and newSymptomList is None:
            # 如果当前症状列表不为空，再进行诊断
            if entity_list and len(entity_list) > 0:
                diseaseRateList, departmentRateList = detect(age, sex, entity_list)
                # 低于阈值，效果不好，要进行新症状询问，添加新症状列表
                if list(departmentRateList.values())[0] < 0.7:
                    new_symptoms = get_new_symptoms(list(departmentRateList.keys())[0], entity_list)
                    return [SlotSet("newSymptomList", new_symptoms if new_symptoms is not None else []),
                            SlotSet("diseaseRateList", diseaseRateList if diseaseRateList is not None else []),
                            SlotSet("departmentRateList", departmentRateList if departmentRateList is not None else [])]
                else:  # 如果高于阈值诊断效果良好，不用添加新症状列表， 直接结束
                    return [SlotSet("diseaseRateList", diseaseRateList if diseaseRateList is not None else []),
                            SlotSet("departmentRateList", departmentRateList if departmentRateList is not None else [])]
        else:  # 如果新症状列表不为空，证明进入问询阶段
            if isUpdated:  # 如果当前症状列表有更新，再重新诊断
                if entity_list and len(entity_list) > 0:
                    diseaseRateList, departmentRateList = detect(age, sex, entity_list)
                    return [SlotSet("diseaseRateList", diseaseRateList if diseaseRateList is not None else []),
                            SlotSet("departmentRateList", departmentRateList if departmentRateList is not None else [])]
            else:  # 如果当前症状列表无变动，不用更新，直接跳过
                return []

        return []


class ActionShowResult(Action):
    def name(self) -> Text:
        return "action_show_result"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        DiseaseRateList = tracker.get_slot("diseaseRateList")
        DepartmentRateList = tracker.get_slot("departmentRateList")
        if (DiseaseRateList is not None and len(DiseaseRateList) > 0) and (
                DepartmentRateList is not None and len(DepartmentRateList)) > 0:
            # 情况1达到阈值，诊断结束
            if list(DepartmentRateList.values())[0] >= 0.7:
                final_disease = list(DiseaseRateList.keys())[0]
                final_department = list(DepartmentRateList.keys())[0]
                dispatcher.utter_message(text="本次导诊最终推荐科室为{0}。诊断疾病可能是{1}。".format(final_department, final_disease))
            # 情况2没达到阈值
            else:
                newSymptomList = tracker.get_slot("newSymptomList")
                # 新症状列表还有内容，还没问完，继续问询
                if newSymptomList and len(newSymptomList) > 0:
                    nextSymptom = newSymptomList[0]
                    dispatcher.utter_message(text="您是否有{}的症状？".format(nextSymptom))
                # 新症状列表存在，但是内容已经空了，证明问询轮次到了，诊断结束
                else:
                    final_disease = list(DiseaseRateList.keys())[0]
                    final_department = list(DepartmentRateList.keys())[0]
                    dispatcher.utter_message(text="本次导诊最终推荐科室为{0}。诊断疾病可能是{1}。".format(final_department, final_disease))

        else:
            dispatcher.utter_message(text="十分抱歉，本次未获取到症状，诊断失败。")

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
        # 用户无法确定有此症状，更新状态false
        else:
            newSymptomList.pop(0)
            return [SlotSet("newSymptomList", newSymptomList),
                    SlotSet("isUpdated", False)]


class ActionChitchat(Action):
    """
    chitchat时自动回复
    """

    def name(self):
        return "action_chitchat"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="我们还是回归导诊吧，可以陈述一下您的症状。")
        return [UserUtteranceReverted()]
