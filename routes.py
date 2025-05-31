from flask import render_template, request
from extract_vocab import extract_vocab_from_pdf
from tracker import vocab_list, shown_history, score_tracker
import os, re, random
from collections import defaultdict

def register_routes(app):
    # 서버 시작 시 단어 불러오기
    if not vocab_list:
        for filename in os.listdir('contents'):
            if filename.endswith('.pdf'):
                path = os.path.join('contents', filename)
                match = re.search(r'chapter\s*([1-3])', filename, re.IGNORECASE)
                if match:
                    chapter = match.group(1)
                    vocab_list.extend(extract_vocab_from_pdf(path, chapter))
                else:
                    print(f"⚠️ 챕터 정보 추출 실패: {filename}")

        print(f"총 단어 수: {len(vocab_list)}개")

    @app.route('/')
    def index():
        chapter = request.args.get('chapter')
        key = chapter or 'all'

        filtered = [v for v in vocab_list if not chapter or str(v[3]) == chapter]

        total = len(filtered)
        used = shown_history[key]

        if total == 0:
            return "⚠️ 해당 챕터에 단어가 없습니다."

        if len(used) >= total:
            shown_history[key] = []
            used = []

        available = list(set(range(total)) - set(used))
        index = random.choice(available)
        word = filtered[index]

        progress_current = len(used)

        return render_template('index.html',
                            definition=word[1],
                            answer=word[0],
                            example=word[2],
                            selected_chapter=chapter,
                            user_input=None,
                            progress_total=total,
                            progress_current=progress_current,
                            progress_percent=int(progress_current / total * 100),
                            correct_count=score_tracker[key]["correct"],
                            wrong_count=score_tracker[key]["wrong"])


    @app.route('/check', methods=['POST'])
    def check():
        user_input = request.form['user_input']
        correct_answer = request.form['correct_answer']
        definition = request.form['definition']
        example = request.form.get('example', '')
        chapter = request.form.get('chapter', '')
        key = chapter or 'all'

        is_correct = user_input.strip().lower() == correct_answer.lower()

        filtered = [v for v in vocab_list if not chapter or str(v[3]) == chapter]

        # 기록
        for idx, item in enumerate(filtered):
            if item[0].lower() == correct_answer.lower():
                if idx not in shown_history[key]:
                    shown_history[key].append(idx)
                break

        # 점수 업데이트
        if is_correct:
            score_tracker[key]["correct"] += 1
        else:
            score_tracker[key]["wrong"] += 1

        total = len(filtered)
        current = len(shown_history[key])

        return render_template('index.html',
                               definition=definition,
                               answer=correct_answer,
                               user_input=user_input,
                               is_correct=is_correct,
                               example=example,
                               selected_chapter=chapter,
                               progress_total=total,
                               progress_current=current,
                               progress_percent=int(current/total*100),
                               correct_count=score_tracker[key]["correct"],
                               wrong_count=score_tracker[key]["wrong"])
