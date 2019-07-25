import math

class RuleModel:
    def __init__(self,dataLoader,histroyRatio):
        self.dataLoader = dataLoader
        self.recommend_number = 100
        self.histroyRatio = histroyRatio


    def detect_rule_recommend(self,user_id):
        detect_list = set([])
        if user_id in self.dataLoader.user_read_list:
            history_list = {}
            user_read_datas = self.dataLoader.user_read_list[user_id]
            # 읽은 파일을 관련 글 리스트 기록
            for user_read_data in user_read_datas:
                user_read_data_split =  user_read_data.split("_")
                user_read_data_point = user_read_data_split[0]
                # 나온 brunch id 에서 앞뒤로 하나씩 추가
                add_dator = user_read_data_point + "_"
                detect_list.add(add_dator + str(int(user_read_data_split[1]) + 1))
                detect_list.add(add_dator + str(int(user_read_data_split[1]) + 2))
                detect_list.add(add_dator + str(int(user_read_data_split[1]) - 1))
                detect_list.add(add_dator + str(int(user_read_data_split[1]) - 2))
                if user_read_data_point in self.dataLoader.brunch_id_match:
                    if user_read_data_point in history_list:
                        history_list[user_read_data_point][0] += 1
                    else:
                        same_authors = self.dataLoader.brunch_id_match[user_read_data_point]
                        history_list[user_read_data_point] = [1,same_authors]
            #앞에서부터 시간순 임으로 시간순으로 삽입
            for history in history_list.values():
                count = max(int(history[0] - 1) * 5,20)
                for add_dator in history[1]:
                    count -= 1
                    if count < 0:
                        break
                    detect_list.add(add_dator)
            if user_id in self.dataLoader.metaData and len(self.dataLoader.metaData[user_id]["following_list"]) != 0:
                for following_id in self.dataLoader.metaData[user_id]["following_list"]:
                    if following_id in self.dataLoader.brunch_id_match:
                        limit_count = 10
                        for recommend_brunch in self.dataLoader.brunch_id_match[following_id]:
                            if limit_count <= 0:
                                break
                            limit_count-=1
                            detect_list.add(recommend_brunch)

            # 사용자가 본리스트는 다시 제거
            detect_list = detect_list - set(user_read_datas)


        if len(detect_list) >= self.histroyRatio:
            detect_list = set(list(detect_list)[:self.histroyRatio])

        if len(detect_list) >= self.recommend_number:
            return list(detect_list)
        # 나머지 수는 가장 인기 있는 리스트로 채우기
        for add_dator in self.dataLoader.hot_brunch_list:
            detect_list.add(add_dator.split(" ")[0])
            if len(detect_list) >= self.recommend_number:
                break
        return list(detect_list)


