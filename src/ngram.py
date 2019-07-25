import operator

class NgramModel:
    def __init__(self,dataLoader):
        self.dataLoader = dataLoader
        self.recommend_number = 100
        self.unigram_score = 2
        self.bigram_score = 5
        self.trigram_score = 30
        self.keyword_score = 50
        self.detect_map = {}


    def detect_rule_recommend(self,user_id):
        self.detect_map = {}
        result = []
        user_following_list = []
        user_read_datas = []
        if user_id in self.dataLoader.user_read_list:
            user_following_list = []
            if user_id in self.dataLoader.metaData and "following_list" in self.dataLoader.metaData[user_id]:
                user_following_list = self.dataLoader.metaData[user_id]["following_list"]
            user_read_datas = self.dataLoader.user_read_list[user_id]
            # 읽은 파일을 관련 글 리스트 기록
            user_read_len = len(user_read_datas)
            for index, user_read_data in enumerate(user_read_datas):
                if user_read_data in self.dataLoader.unigram:
                    for unigram_target in self.dataLoader.unigram[user_read_data]:
                        self.add_score("unigram",unigram_target,unigram_target.split("_")[0] in user_following_list)

                user_reads = [user_read_data]
                if index + 1 < user_read_len:
                    user_reads.append(user_read_datas[index + 1])
                    sorted(user_reads)
                    target_str = " ".join(user_reads)
                    if target_str in self.dataLoader.bigram:
                        for bigram_target in self.dataLoader.bigram[target_str]:
                            self.add_score("bigram",bigram_target,bigram_target.split("_")[0] in user_following_list)

                if index + 2 < user_read_len:
                    user_reads.append(user_read_datas[index + 2])
                    sorted(user_reads)
                    target_str = " ".join(user_reads)
                    if target_str in self.dataLoader.trigram:
                        for trigram_target in self.dataLoader.trigram[target_str]:
                            self.add_score("trigram",trigram_target,trigram_target.split("_")[0] in user_following_list)

            #사용자가 본 리스트 제거
            for user_read_data in user_read_datas:
                if user_read_data in self.detect_map:
                    del self.detect_map[user_read_data]

        sorted_result =  sorted(self.detect_map.items(),key = operator.itemgetter(1),reverse=True)
        for index, recommend_data in enumerate(sorted_result):
            if len(result) >= self.recommend_number:
                break
            result.append(recommend_data[0])


        if len(user_following_list) != 0:
            #follwing_list가 있는경우 그 안에서 가장 인기있는 순으로채우기
            for add_dator in self.dataLoader.hot_brunch_list:
                if len(result) >= self.recommend_number:
                    break
                target_brunch = add_dator.split(" ")[0]
                if target_brunch.split("_")[0] in user_following_list and target_brunch not in result and target_brunch not in user_read_datas:
                    result.append(target_brunch)

        # kakao 기본 결과로 채우기
        for kakao_data in self.dataLoader.kakao_data:
            if len(result) >= self.recommend_number:
                break
            if kakao_data in user_read_datas or kakao_data in result:
                continue
            result.append(kakao_data)

        # 나머지 수는 가장 인기 있는 리스트로 채우기
        for add_dator in self.dataLoader.hot_brunch_list:
            if len(result) >= self.recommend_number:
                break
            target_brunch = add_dator.split(" ")[0]
            if target_brunch not in result and target_brunch not in user_read_datas:
                result.append(add_dator.split(" ")[0])

        return result

    def add_score(self,gram,key,keyword):
        score = 0
        if keyword:
            score += self.keyword_score
        if gram == "unigram":
            score += self.unigram_score
        elif gram == "bigram":
            score += self.bigram_score
        elif gram == "trigram":
            score += self.trigram_score

        if key in self.detect_map:
            self.detect_map[key] += score
        else:
            try:
                self.detect_map[key] = score
            except:
                print("최대수")
                print(len(self.detect_map))
        # 메모리 초과로 인하여 임시 작업 TODO 변경 필요
        if len(self.detect_map) > 500000:
            sorted_result = sorted(self.detect_map.items(), key=operator.itemgetter(1), reverse=True)
            del self.detect_map
            self.detect_map = {}
            for index, recommend_data in enumerate(sorted_result):
                self.detect_map[recommend_data[0]] = recommend_data[1]
                if len(self.detect_map) >= 300000:
                    break















