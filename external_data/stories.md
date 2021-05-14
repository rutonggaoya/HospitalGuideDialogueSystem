## happy_path_1
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
* complaint
    - action_set_symptoms
    - action_diagnose
    - action_show_result
    - utter_bye
* bye

## happy_path_2
* greet
    - utter_greet
* affirm
    - action_get_information
* choose_age{"age":"老人"}
    - slot{"age":"老人"}
    - action_get_information
* choose_sex{"sex":"男"}
    - slot{"sex":"男"}
    - action_get_information
* complaint
    - action_set_symptoms
    - utter_ask_more_symptoms
* complaint
    - action_set_symptoms
    - action_diagnose
    - action_show_result
    - utter_bye
    
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
* choose_age{"age":"其他"}
    - slot{"age":"其他"}
    - action_get_information
* choose_sex{"sex":"男"}
    - slot{"sex":"男"}
    - action_get_information
* complaint
    - action_set_symptoms
    - utter_ask_more_symptoms
* complaint
    - action_set_symptoms
    - action_diagnose
    - action_show_result
    - utter_bye    

## default_path
* stop
    - action_default_fallback

## bye
* bye
    - utter_bye

## interactive_story_1
* greet
    - utter_greet
* affirm
    - action_get_information
* choose_age{"age": "老人"}
    - slot{"age": "老人"}
    - action_get_information
* choose_sex{"sex": "男"}
    - slot{"sex": "男"}
    - action_get_information
* complaint{"symptom": "尿急"}
    - action_set_symptoms
    - slot{"symptomList": ["尿频", "尿急"]}
    - action_diagnose
    - slot{"diseaseRateList": {"慢性前列腺炎": 0.12056858665600506, "尿失禁": 0.10735738718380686, "膀胱平滑肌瘤": 0.10286550709554428, "膀胱憩室": 0.1013194832617432, "老年人尿路感染": 0.08797585183571108}}
    - slot{"departmentRateList": {"泌尿外科": 0.9248202834555354, "其他内科": 0.06352826113097772, "内科": 0.0017431116834175022, "肾病内科": 0.001468305419438959, "普通外科": 0.0013888429700297687}}
    - action_show_result
    - utter_bye

## interactive_story_2
* greet
    - utter_greet
* affirm
    - action_get_information
* choose_age{"age": "其他"}
    - slot{"age": "其他"}
    - action_get_information
* choose_sex{"sex": "女"}
    - slot{"sex": "女"}
    - action_get_information
* complaint{"symptom": "右下腹痛"}
    - action_set_symptoms
    - slot{"symptomList": ["肚子疼", "右下腹痛"]}
    - action_diagnose
    - slot{"diseaseRateList": {"盲肠肉芽肿": 1.2274904658903678, "急性阑尾炎": 0.4988424535915488, "胃溃疡性穿孔": 0.34908648249229, "肠子宫内膜异位": 0.29294805860734097, "阑尾炎": 0.2854950236963431}}
    - slot{"departmentRateList": {"普通外科": 0.6305635663856582, "肾病内科": 0.26797806821734166, "消化内科": 0.04918181847075303, "其他内科": 0.025640643808065116, "神经外科": 0.003835025626461779}}
    - action_show_result
    - utter_bye

## interactive_story_3
* greet
    - utter_greet
* affirm
    - action_get_information
* choose_age{"age": "儿童"}
    - slot{"age": "儿童"}
    - action_get_information
* choose_sex{"sex": "男"}
    - slot{"sex": "男"}
    - action_get_information
* complaint
    - action_set_symptoms
    - utter_ask_more_symptoms
* complaint{"symptom": "夜间头痛"}
    - action_set_symptoms
    - slot{"symptomList": ["头痛", "夜间头痛"]}
    - action_diagnose
    - slot{"diseaseRateList": {"瘴疟": 0.6661185227580756, "腹型偏头痛综合征": 0.3617114802927195, "痰浊头痛": 0.19325335089804488, "鞍结节脑膜瘤": 0.16506369807267676, "空调病": 0.002964478963739014}}
    - slot{"departmentRateList": {"心血管内科": 0.43445808950207554, "神经外科": 0.10899760004182336, "内科": 0.08584549984431683, "其他内科": 0.06290739680144108, "皮肤科": 0.05064769421464113}}
    - action_show_result
    - utter_bye
