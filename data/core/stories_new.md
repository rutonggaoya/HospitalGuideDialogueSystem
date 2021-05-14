## default_path
* stop
    - action_default_fallback

## bye
* bye
    - utter_bye

## happy_path_1_no_ask
* greet
    - utter_greet
* affirm
    - action_get_information
* choose_age{"age":"儿童"}
    - action_set_age
    - slot{"age":"儿童"}
    - action_get_information
* choose_sex{"sex":"女"}
    - action_set_sex
    - slot{"sex":"女"}
    - action_get_information
* complaint{"symptom": "肚子疼"}
    - action_set_symptoms
    - slot{"symptomList": ["肚子疼"]}
    - action_diagnose
    - action_show_result
* bye
    - utter_bye

## happy_path_2_one_ask
* greet
    - utter_greet
* affirm
    - action_get_information
* choose_age{"age":"老人"}
    - action_set_age
    - slot{"age":"老人"}
    - action_get_information
* choose_sex{"sex":"男"}
    - action_set_sex
    - slot{"sex":"男"}
    - action_get_information
* complaint{"symptom": "肚子疼"}
    - action_set_symptoms
    - slot{"symptomList": ["肚子疼"]}
    - action_diagnose
    - action_show_result
* affirm
    - action_set_new_symptom
    - slot{"isUpdated": "True"}
    - action_diagnose
    - action_show_result
    
    
## happy_path_3_two_ask
* greet
    - utter_greet
* affirm
    - action_get_information
* choose_age{"age":"老人"}
    - action_set_age
    - slot{"age":"老人"}
    - action_get_information
* choose_sex{"sex":"男"}
    - action_set_sex
    - slot{"sex":"男"}
    - action_get_information
* complaint
    - action_set_symptoms
    - action_diagnose
    - action_show_result
* deny
    - action_set_new_symptom
    - slot{"isUpdated": "False"}
    - action_diagnose
    - action_show_result
* affirm
    - action_set_new_symptom
    - slot{"isUpdated": "True"}
    - action_diagnose
    - action_show_result
    
## happy_path_4_three_ask
* greet
    - utter_greet
* affirm
    - action_get_information
* choose_age{"age":"老人"}
    - action_set_age
    - slot{"age":"老人"}
    - action_get_information
* choose_sex{"sex":"男"}
    - action_set_sex
    - slot{"sex":"男"}
    - action_get_information
* complaint
    - action_set_symptoms
    - action_diagnose
    - action_show_result
* deny
    - action_set_new_symptom
    - slot{"isUpdated": "False"}
    - action_diagnose
    - action_show_result
* deny
    - action_set_new_symptom
    - slot{"isUpdated": "False"}
    - action_diagnose
    - action_show_result
* affirm
    - action_set_new_symptom
    - slot{"isUpdated": "True"}
    - action_diagnose
    - action_show_result

## unhappy_path_1
* greet
    - utter_greet
* deny
    - utter_bye

## unhappy_path_2
* greet
    - utter_greet
* affirm
    - action_get_information
* choose_age
    - action_set_age
    - slot{"age":"老人"}
    - action_get_information
* choose_sex{"sex":"女"}
    - action_set_sex
    - slot{"sex":"女"}
    - action_get_information
* complaint
    - action_set_symptoms
    - utter_ask_more_symptoms
* complaint
    - action_set_symptoms
    - action_diagnose
    - action_show_result

## interactive_story_1
* greet
    - utter_greet
* affirm
    - action_get_information
* choose_age
    - action_set_age
    - slot{"age": "其他"}
    - action_get_information
* choose_sex
    - action_set_sex
    - slot{"sex": "男"}
    - action_get_information
* complaint{"symptom": "尿不尽"}
    - action_set_symptoms
    - slot{"symptomList": ["尿急", "尿频", "尿不尽"]}
    - action_diagnose
    - slot{"diseaseRateList": {"膀胱炎": 0.26689550055473915, "尿道综合征": 0.13596574939144548, "前列腺炎": 0.12640818688749114}}
    - slot{"departmentRateList": {"泌尿外科": 0.7510205040210632, "肾病内科": 0.2026565349170766, "其他内科": 0.03539237666162459}}
    - action_show_result
* bye
    - utter_bye

## interactive_story_2
* greet
    - utter_greet
* affirm
    - action_get_information
* choose_age
    - action_set_age
    - slot{"age": "其他"}
    - action_get_information
* choose_sex
    - action_set_sex
    - slot{"sex": "男"}
    - action_get_information
* complaint{"symptom": "胃疼"}
    - action_set_symptoms
    - slot{"symptomList": ["肚子疼", "胃疼"]}
    - action_diagnose
    - slot{"diseaseRateList": {"幽门螺旋杆菌感染": 0.020415231407439834, "胃溃疡": 0.015100655899261168, "肠炎": 0.010946137246426551}}
    - slot{"departmentRateList": {"消化内科": 0.849154078935243, "肾病内科": 0.09351966894152247, "普通外科": 0.026307864698964005}}
    - action_show_result
