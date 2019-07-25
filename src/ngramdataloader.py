# -*- coding: utf_8 -*-
import os
import sys
import json
import zipfile

class NgramDataLoader:
    def __init__(self,data_path, train_number):
        self.data_path = data_path
        self.magazine = {}
        self.magazine_r = {}
        self.metaData = {}
        self.metaData_keyword = {}
        self.userData = {}
        self.train_number = train_number
        self.input_data = []
        self.user_read_list = {}
        self.hot_brunch_list = []
        self.brunch_id_match = {}

    def data_loader(self, days):
        try:
            with open(self.data_path["magazinePath"], "r", encoding="utf-8") as magazineTarget:
                lines = magazineTarget.readlines()
                for line in lines:
                    json_file = json.loads(line)
                    self.magazine[json_file["id"]] = json_file["magazine_tag_list"]
                    for tag in json_file["magazine_tag_list"]:
                        if tag in self.magazine_r:
                            self.magazine_r[tag].append(json_file["id"])
                        else:
                            self.magazine_r[tag] = [json_file["id"]]

                with open(self.data_path["metadataPath"], "r", encoding="utf-8") as metaTarget:
                    lines = metaTarget.readlines()
                    for line in lines:
                        json_file = json.loads(line)
                        self.metaData[json_file["id"]] = json_file
                        for keyword in json_file["keyword_list"]:
                            if keyword in self.metaData_keyword:
                                self.metaData_keyword[keyword].append([json_file["id"],json_file["magazine_id"]])
                            else:
                                self.metaData_keyword[keyword] = [json_file["id"],json_file["magazine_id"]]

                with open(self.data_path["usersPath"], "r", encoding="utf-8") as userTarget:
                    lines = userTarget.readlines()
                    for line in lines:
                        json_file = json.loads(line)
                        if len(json_file["keyword_list"]) != 0 or len(json_file["following_list"]) != 0:
                            self.metaData[json_file["id"]] = json_file
                self.factory_data_load(days)
                # 데이터 로드
                # 데이터가 커서 임시 보류
                # self.input_data_loader()
        except FileNotFoundError as e:
            print("해당 파일이 존재하지 않습니다.")
            print(e)
            sys.exit(1)


    def factory_data_load(self,days):
        try:
            with open(self.data_path["factory_path"] + "/" + str(days) + "days_hot_brunch_file.txt", "r") as hot_brunch_file:
                lines = hot_brunch_file.readlines()
                for line in lines:
                    self.hot_brunch_list.append(line.strip())

            with open(self.data_path["factory_path"] + "/" + str(days) + "brunch_id_match.json", "r") as brunch_id_file:
                self.brunch_id_match = json.loads(brunch_id_file.read())

            with open(self.data_path["factory_path"] + "/" + str(days) + "user_history.json", "r") as user_read_file:
                self.user_read_list = json.loads(user_read_file.read())

        except FileNotFoundError as e:
            print("해당 파일이 존재하지 않습니다.")
            print(e)
            sys.exit(1)

    def input_data_loader(self):
        line_number = 0
        for root, dirs, files in os.walk(self.data_path["contentsPath"]):
            for file in files:
                with open(root + "/" + file, "r", encoding="utf-8") as target:
                    while True:
                        if line_number > self.train_number: return
                        line_number += 1
                        line = target.readline()
                        if not line : break
                        json_file = json.loads(line)
                        self.input_embedding(json_file)

    def target_data_loader(self,path):
        datas = []
        try:
            with open(path, "r") as target_data_file:
                lines = target_data_file.readlines()
                for line in lines:
                    datas.append(line.strip())
        except FileNotFoundError as e:
            print("해당 파일이 존재하지 않습니다.")
            print(e)
            sys.exit(1)

        return datas

    def write_result(self,path,result_data):
        try:
            with open(path, "w", encoding="utf-8") as f:
                for data in result_data:
                    if len(data.split(" ")) != 101:
                        print("데이터 100줄 초과")
                    f.write(data + "\n")
            with zipfile.ZipFile(path[:-3] + "zip", 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(os.path.relpath(os.path.join("", path)), "recommend.txt")
                zf.close()
        except Exception as e:
            print("해당경로가 존재하지 않습니다.")
            print(e)
