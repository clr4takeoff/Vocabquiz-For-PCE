from collections import defaultdict

# 단어 목록
vocab_list = []

# 사용자가 푼 단어 인덱스 기록
shown_history = defaultdict(list)

# 정답/오답 카운트 기록
score_tracker = defaultdict(lambda: {"correct": 0, "wrong": 0})
