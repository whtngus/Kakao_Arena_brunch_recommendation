# -*- coding: utf_8 -*-
# import pickle
import _pickle as pickle
import json
import os
import sys
from collections import Counter


# from sklearn.externals import joblib

class DataFactory:
    def __init__(self,data_path, limit_date_count):
        self.data_path = data_path
        self.magazine = {}
        self.magazine_r = {}
        self.metaData = {}
        self.metaData_keyword = {}
        self.userData = {}
        self.input_data = []
        self.user_read_list = {}
        self.hot_brunch_list = []
        self.brunch_id_match = {}
        self.limit_date_count = limit_date_count * 23

    def data_factory(self,write_file_path):
        # 하루에 파일이 23개씩 있음
        # brunch_read_list = {}
        id_read_list = {}
        brunch_read_count = {}
        brunch_id_dict = {}
        date_count = 0
        try:
            for root, dirs, files in os.walk(self.data_path["history"]):
                #최신 날짜 기준으로 정렬
                files.sort(reverse=True)
                for file in files:
                    #리미트 날짜까지만 history를 확인
                    if date_count > self.limit_date_count:
                        break

                    with open(root + "/" + file, "r", encoding="utf-8") as target:
                        date_count += 1
                        lines = target.readlines()
                        for line in lines:
                            # id_read_list 시간순으로 append
                            # 문장 뒤 \n 제거
                            line_data = line.strip().split(" ")
                            if line_data[0] in id_read_list:
                                id_read_list[line_data[0]] = id_read_list[line_data[0]] + line_data[1:]
                            else:
                                id_read_list[line_data[0]] = line_data[1:]
                            # brunch list id  시간순으로 append
                            for index in range(1,len(line_data)):
                                line_data_index = line_data[index]
                                point_id = line_data_index.split("_")[0]
                                if point_id in brunch_id_dict:
                                    target_point_id = brunch_id_dict[point_id]
                                    if line_data_index not in target_point_id:
                                        target_point_id += [line_data_index]
                                else:
                                    brunch_id_dict[point_id] = [line_data_index]

                                if line_data_index in brunch_read_count:
                                    # brunch_read_list[line_data_index] = brunch_read_list[line_data_index] + [line_data[0]]
                                    brunch_read_count[line_data_index] = brunch_read_count[line_data_index] + 1
                                else:
                                    # brunch_read_list[line_data_index] = [line_data[0]]
                                    brunch_read_count[line_data_index] = 1


            with open(write_file_path + "/" + str(int(self.limit_date_count / 23)) + "user_history.json","w") as user_read_file:
                user_read_file.write(json.dumps(id_read_list))

            with open(write_file_path + "/" + str(int(self.limit_date_count / 23)) + "brunch_id_match.json", "w") as brunch_id_file:
                brunch_id_file.write(json.dumps(brunch_id_dict))

            brunch_read_count_re = sorted(brunch_read_count.items(),reverse=True,key = lambda t : t[1])
            with open(write_file_path + "/" + str(int(self.limit_date_count / 23)) + "days_hot_brunch_file.txt","w") as hot_brunch_file:
                for data in brunch_read_count_re:
                    hot_brunch_file.write("{} {}\n".format(data[0],data[1]))

        except FileNotFoundError as e:
            print("해당 파일, 경로가 존재하지 않습니다.")
            print(e)
            sys.exit(1)

    def user_associate_list(self, write_file_path):
        result_unigram = {}
        result_bigram = {}
        result_trigram = {}
        date_count = 0
        user_lead_path = self.data_path["history"]
        try:
            for root, dirs, files in os.walk(user_lead_path):
                #최신 날짜 기준으로 정렬
                files.sort(reverse=True)
                for file in files:
                    #리미트 날짜까지만 history를 확인
                    if date_count > self.limit_date_count:
                        break
                    if date_count % 23 == 0:
                        print("{}일차 작업 완료".format(date_count/23))
                    with open(root + "/" + file, "r", encoding="utf-8") as target:
                        date_count += 1
                        lines = target.readlines()
                        for line in lines:
                            # id_read_list 시간순으로 append
                            # 문장 뒤 \n 제거
                            line_data = line.strip().split(" ")[1:]
                            count = Counter(line_data)
                            line_data_len = len(line_data)
                            for i in range(line_data_len):
                                inputs = [line_data[i]]
                                # unigram
                                if inputs[0] in result_unigram:
                                    result_unigram[inputs[0]] += count
                                else:
                                    result_unigram[inputs[0]] = count
                                # bigram
                                if i + 1 < line_data_len:
                                    inputs.append(line_data[i+1])
                                    inputs.sort()
                                    strs = " ".join(inputs)
                                    if strs in result_bigram:
                                        result_bigram[strs] += count
                                    else:
                                        result_bigram[strs] = count
                                # thrigram
                                if i + 2 < line_data_len:
                                    inputs.append(line_data[i+2])
                                    inputs.sort()
                                    strs = " ".join(inputs)
                                    if strs in result_trigram:
                                        result_trigram[strs] += count
                                    else:
                                        result_trigram[strs] = count

            # Counter를 Dict 로 변경  and value가 1인 것들 제거 -- 용량 아끼기
            result_unigram = self.counter_to_dict(result_unigram)
            result_bigram = self.counter_to_dict(result_bigram)
            result_trigram = self.counter_to_dict(result_trigram)

            # 파일 저장
            with open(write_file_path + "/" + str(int(self.limit_date_count / 23)) + "result_unigram.json","wb") as result_unigram_file:
                pickle.dump(result_unigram, result_unigram_file)
                del result_unigram
                result_unigram_file.close()
            with open(write_file_path + "/" + str(int(self.limit_date_count / 23)) + "result_bigram.json", "wb") as result_bigram_file:
                pickle.dump(result_bigram, result_bigram_file)
                del result_bigram
                result_bigram_file.close()
            with open(write_file_path + "/" + str(int(self.limit_date_count / 23)) + "result_trigram.json", "wb") as result_trigram_file:
                pickle.dump(result_trigram, result_trigram_file)
                del result_trigram
                result_trigram_file.close()
        except Exception as e:
            print("data_line_loader Error")
            print(e)

    def detail_factory(self,target_path):
        lines = self.data_line_loader(target_path)
        for line in lines:
            print(line)


    def data_line_loader(self,target_path):
        try:
            with open(target_path, "r", encoding="utf-8") as target_file:
                while True:
                    line = target_file.readline()
                    if not line: break
                    yield json.loads(line)
        except Exception as e:
            print("data_line_loader Error")
            print(e)

    def counter_to_dict(self,target):
        for dict_key in target.keys():
            del_list = []
            # target[dict_key] = dict(target[dict_key])
            for key in target[dict_key]:
                if 1 == target[dict_key][key]:
                    del_list.append(key)
            # count 가 1인 Value 전부 삭제
            for del_target in del_list:
                del target[dict_key][del_target]

        return  target


if __name__ == "__main__":
    factory_path = "../res/factory"
    detail_data_path = "../res/contents/data.0"
    history_limite_date = 15
    dataPath = {"contentsPath": "../res/contents",
                "magazinePath": "../res/others/magazine.json",
                "metadataPath": "../res/others/metadata.json",
                "usersPath": "../res/others/users.json",
                "predictPath": "../res/predict",
                "history": "../res/read",
                "factory_path": "../res/factory"}
    dataFactory = DataFactory(dataPath, history_limite_date)
    # 사전 데이터 생성
    dataFactory.data_factory(factory_path)
    # 데이러 로드
    # dataFactory.data_loader()
    # 디테일 데이터 생성 작업 x
    # dataFactory.detail_factory(detail_data_path)
    # n-gram 생성
    dataFactory.user_associate_list(factory_path)