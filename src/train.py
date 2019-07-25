from dataloader import DataLoader
from ngram import NgramModel
from ruleModel import RuleModel


class Train:
    def __init__(self,write_file_path):
        train_number = 100
        self.write_file_path = write_file_path
        days = 10
        self.histroyRatio = 99
        dataPath = {"contentsPath": "../res/contents",
                    "magazinePath": "../res/others/magazine.json",
                    "metadataPath": "../res/others/metadata.json",
                    "usersPath": "../res/others/users.json",
                    "predictPath": "../res/predict",
                    "factory_path": "../res/factory"
                    }
        self.dataLoader = DataLoader(dataPath, train_number)
        self.dataLoader.data_loader(days)

    def train(self,target_data_path):
        results = []
        ruleModel = RuleModel(self.dataLoader, self.histroyRatio)
        target_datas = self.dataLoader.target_data_loader(target_data_path)
        for target_data in target_datas:
            re = ruleModel.detect_rule_recommend(target_data)
            results.append(target_data + " " + " ".join(re))
        self.dataLoader.write_result(self.write_file_path,results)


    def train_ngram(self,target_data_path,days, kakao_data_path):
        results = []
        ngramModel = NgramModel(self.dataLoader)
        self.dataLoader.ngram_data_loader(days)
        self.dataLoader.kakao_data_loader(kakao_data_path)
        target_datas = self.dataLoader.target_data_loader(target_data_path)
        target_data_len = len(target_datas)
        for i, target_data in enumerate(target_datas):
            if i % (target_data_len / 100) == 0:
                print("{}% 완료".format((i / target_data_len)*100))
            re = ngramModel.detect_rule_recommend(target_data)
            results.append(target_data + " " + " ".join(re))
        self.dataLoader.write_result(self.write_file_path,results)




if __name__ == "__main__":
    target_data_path = "../res/predict/test.users"
    write_path = "../res/recommend.txt"
    kakao_data_path = "../res/factory/recommend.txt"
    ngram_days = 12
    train = Train(write_path)
    # train.train(target_data_path)
    train.train_ngram(target_data_path, ngram_days, kakao_data_path)
