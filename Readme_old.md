rasa train --config config.yml --domain domain.yml --data data/
rasa train --config config_mine.yml --domain domain.yml --data data/
rasa test nlu -u external_data/raw_data/ --model models/20200517-112134.tar.gz
## 训练集
rasa test nlu -u data/nlu/nlu_new.md --model models/20200517-112134.tar.gz
rasa test nlu -u data/nlu/ --model models/20200517-112134.tar.gz
models/20200517-154605.tar.gz
## 测试集
rasa test nlu -u external_data/raw_data/nlu_test.md --model models/20200517-112134.tar.gz

rasa test nlu -u data/nlu/nlu_new.md --config config.yml --cross-validation
rasa test core --stories stories_new.md --out results


rasa interactive --config config_mine.yml --domain domain.yml --data data/
rasa interactive --model models/20200525-170528.tar.gz
rasa shell --model models/20200525-170528.tar.gz --debug

python -m rasa run --port 5005 --endpoints endpoints.yml --credentials credentials.yml --model models/20200525-195841.tar.gz --debug
python -m rasa run actions --actions actions --debug
python server.py