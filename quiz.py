from flask import Flask, render_template, request
from extract_vocab import extract_vocab_from_pdf
from collections import defaultdict
import random, os
import re

app = Flask(__name__)

vocab_list = []
shown_history = defaultdict(list)

# 단어 추출 및 챕터 정보 읽기
for filename in os.listdir('contents'):
    if filename.endswith('.pdf'):
        path = os.path.join('contents', filename)

        match = re.search(r'chapter\s*([1-3])', filename, re.IGNORECASE)
        if match:
            chapter = match.group(1)
            vocab_list.extend(extract_vocab_from_pdf(path, chapter))
        else:
            print(f"챕터 정보 추출 실패: {filename}")

# 챕터별 단어 개수 출력
chapter_counts = defaultdict(int)
for v in vocab_list:
    if len(v) > 3:
        chapter = str(v[3])
        chapter_counts[chapter] += 1

print("챕터별 단어 개수:")
for chapter, count in sorted(chapter_counts.items()):
    print(f"  - Chapter {chapter}: {count}개")
print(f"전체 단어 수: {len(vocab_list)}개")


@app.route('/')
def index():
    chapter = request.args.get('chapter')

    if not vocab_list:
        return "⚠️ PDF에서 단어를 불러올 수 없습니다. contents 폴더를 확인하세요."

    filtered_vocab = vocab_list
    if chapter:
        filtered_vocab = [
            v for v in vocab_list
            if len(v) > 3 and str(v[3]) == str(chapter)
        ]
        print(f"[선택된 챕터: {chapter}] 해당 챕터 단어 수: {len(filtered_vocab)}개")
    else:
        print(f"[전체 보기] 전체 단어 수: {len(vocab_list)}개")

    if not filtered_vocab:
        return "해당 챕터에 단어가 없습니다."

    key = chapter or 'all'
    total_indices = list(range(len(filtered_vocab)))
    used_indices = shown_history[key]

    if len(used_indices) >= len(filtered_vocab):
        print(f"[리셋] 챕터 {key} 모든 단어 출제 완료. 사이클 재시작.")
        shown_history[key] = []
        used_indices = []

    available_indices = list(set(total_indices) - set(used_indices))
    chosen_index = random.choice(available_indices)
    word_item = filtered_vocab[chosen_index]

    print(f"[챕터 {key}] 출제된 단어 수: {len(shown_history[key])}/{len(filtered_vocab)}")

    progress_total = len(filtered_vocab)
    progress_current = len(shown_history[key])
    progress_percent = int(progress_current / progress_total * 100)

    return render_template('index.html',
                           definition=word_item[1],
                           answer=word_item[0],
                           example=word_item[2],
                           selected_chapter=chapter,
                           user_input=None,
                           progress_total=progress_total,
                           progress_current=progress_current,
                           progress_percent=progress_percent)



@app.route('/check', methods=['POST'])
def check():
    user_input = request.form['user_input']
    correct_answer = request.form['correct_answer']
    definition = request.form['definition']
    example = request.form.get('example', '')
    chapter = request.form.get('chapter', '')

    is_correct = user_input.strip().lower() == correct_answer.lower()

    # 필터링
    filtered_vocab = [
        v for v in vocab_list
        if len(v) > 3 and (str(v[3]) == str(chapter) if chapter else True)
    ]
    key = chapter or 'all'

    # 제출된 단어 사용 처리
    for idx, item in enumerate(filtered_vocab):
        if item[0].lower() == correct_answer.lower():
            if idx not in shown_history[key]:
                shown_history[key].append(idx)
            break

    # 진행률 계산
    progress_total = len(filtered_vocab)
    progress_current = len(shown_history[key])
    progress_percent = int(progress_current / progress_total * 100)

    return render_template('index.html',
                           definition=definition,
                           answer=correct_answer,
                           user_input=user_input,
                           is_correct=is_correct,
                           example=example,
                           selected_chapter=chapter,
                           progress_total=progress_total,
                           progress_current=progress_current,
                           progress_percent=progress_percent)



if __name__ == '__main__':
    app.run(debug=True)
