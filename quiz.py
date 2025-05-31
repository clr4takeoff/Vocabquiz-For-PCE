from flask import Flask, render_template, request
from extract_vocab import extract_vocab_from_pdf
from collections import defaultdict
import random, os
import re

app = Flask(__name__)

vocab_list = []
for filename in os.listdir('contents'):
    if filename.endswith('.pdf'):
        path = os.path.join('contents', filename)

        match = re.search(r'chapter\s*([1-3])', filename, re.IGNORECASE)
        if match:
            chapter = match.group(1)
            vocab_list.extend(extract_vocab_from_pdf(path, chapter))
        else:
            print(f"⚠️ 챕터 정보 추출 실패: {filename}")

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
        print(f"[📘 선택된 챕터: {chapter}] 해당 챕터 단어 수: {len(filtered_vocab)}개")
    else:
        print(f"[📘 전체 보기] 전체 단어 수: {len(vocab_list)}개")

    if not filtered_vocab:
        word_item = random.choice(vocab_list)
    else:
        word_item = random.choice(filtered_vocab)

    return render_template('index.html',
                           definition=word_item[1],
                           answer=word_item[0],
                           example=word_item[2],
                           selected_chapter=chapter,
                           user_input=None)


@app.route('/check', methods=['POST'])
def check():
    user_input = request.form['user_input']
    correct_answer = request.form['correct_answer']
    definition = request.form['definition']
    example = request.form.get('example', '')

    is_correct = user_input.strip().lower() == correct_answer.lower()

    return render_template('index.html',
                           definition=definition,
                           answer=correct_answer,
                           user_input=user_input,
                           is_correct=is_correct,
                           example=example)

if __name__ == '__main__':
    app.run(debug=True)