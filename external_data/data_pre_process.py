# path_train = r"D:\projects\PycharmProjects\EcustHosipitalGuideDS\external_data\raw_data\qLable_train_recombination.txt"
# path_test = r"D:\projects\PycharmProjects\EcustHosipitalGuideDS\external_data\raw_data\qLable_test_recombination.txt"
#
# path_train_raw = r"D:\projects\PycharmProjects\EcustHosipitalGuideDS\external_data\raw_data\qLable_train.txt"
# path_test_raw = r"D:\projects\PycharmProjects\EcustHosipitalGuideDS\external_data\raw_data\qLable_test.txt"
# # 将数据转化成.md格式，如 Could I pay in [yen](currency)
# def read_raw_data(path):
#     write_to_file("## intent:complaint\n")
#     with open(path, mode='r', encoding='utf-8') as f:
#         n = 0
#         is_inside = False
#         new_text = '- '
#         for text in f:
#             n += 1
#             text = text.strip('\n')
#             if len(text) >= 3:
#                 pair = text.split(' ')
#                 word, label = pair[0], pair[1]
#                 # print(word+"--"+label)
#                 if label == "I-症状描述":
#                     new_text += word
#                 elif label == "B-症状描述":
#                     if is_inside:
#                         new_text += "](symptom)[{0}".format(word)
#                     else:
#                         new_text += "[{0}".format(word)
#                         is_inside = True
#                 else:
#                     if is_inside:
#                         new_text += "](symptom){0}".format(word)
#                         is_inside = False
#                     else:
#                         new_text += word
#             else:
#                 if is_inside:
#                     new_text += "](symptom)"
#                     is_inside = False
#                 new_text = new_text.strip()
#                 new_text += "\n"
#                 print("新text为:"+new_text)
#                 write_to_file(new_text)
#                 new_text = "- "
#             # if n == 1000:
#             #     break
#
#
# # 写入nlu.md文件
# def write_to_file(text):
#     with open(r"D:\projects\PycharmProjects\EcustHosipitalGuideDS\external_data\raw_data\nlu_test_raw.md", mode='a', encoding='utf-8') as f:
#         f.write(text)
#
#
# read_raw_data(path_test_raw)

from external_data.diagnose_data.symptome_names import symptom_names

with open(r"D:\projects\PycharmProjects\EcustHosipitalGuideDS\external_data\lookup\diseasename.txt" ,encoding='utf-8', mode='a') as f:
    for i in symptom_names:
        f.write(i+'\n')
