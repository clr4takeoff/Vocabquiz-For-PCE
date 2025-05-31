from flask import render_template, request
from extract_vocab import extract_vocab_from_pdf
from tracker import vocab_list, shown_history, score_tracker
import os, re, random

def ensure_tracking_initialized(key):
    if key not in shown_history:
        shown_history[key] = []
    if key not in score_tracker:
        score_tracker[key] = {"correct": 0, "wrong": 0}

def register_routes(app):
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
    @app.route('/')
    def index():
        chapter = request.args.get('chapter')
        action  = request.args.get('action')

        if not chapter or chapter.lower() in ('none', 'null'):
            chapter = ''
        key = chapter or 'all'

        if action == 'next':
            shown_history[key].append(index)
        else:
            # 새로고침이나 첫 접속일 경우 진행 기록 초기화
            shown_history[key] = []
            score_tracker[key] = {"correct": 0, "wrong": 0}

        filtered = [v for v in vocab_list if not chapter or str(v[3]) == chapter]
        total    = len(filtered)
        if total == 0:
            return "⚠️ 해당 챕터에 단어가 없습니다."

        used = [i for i in shown_history[key] if i < total]
        shown_history[key] = used

        if len(used) >= total:
            shown_history[key] = []
            used = []

        available = list(set(range(total)) - set(used))
        index     = random.choice(available)
        word      = filtered[index]

        if action == 'next':
            shown_history[key].append(index)

        progress_current = len(shown_history[key])
        progress_percent = int(progress_current / total * 100) if total else 0

        return render_template(
            'index.html',
            definition       = word[1],
            answer           = word[0],
            example          = word[2],
            selected_chapter = chapter,
            user_input       = None,
            progress_total   = total,
            progress_current = progress_current,
            progress_percent = progress_percent,
            correct_count    = score_tracker[key]["correct"],
            wrong_count      = score_tracker[key]["wrong"]
        )

    @app.route('/check', methods=['POST'])
    def check():
        user_input = request.form['user_input']
        correct_answer = request.form['correct_answer']
        definition = request.form['definition']
        example = request.form.get('example', '')
        chapter = request.form.get('chapter', '')
        if not chapter or chapter.lower() in ('none', 'null'):
            chapter = ''
        key = chapter or 'all'
        ensure_tracking_initialized(key)

        filtered = [v for v in vocab_list if not chapter or str(v[3]) == chapter]
        total = len(filtered)

        is_correct = user_input.strip().lower() == correct_answer.strip().lower()

        for idx, item in enumerate(filtered):
            if item[0].strip().lower() == correct_answer.strip().lower():
                if idx not in shown_history[key]:
                    shown_history[key].append(idx)
                break

        if is_correct:
            score_tracker[key]["correct"] += 1
        else:
            score_tracker[key]["wrong"] += 1

        current = len(shown_history[key])
        progress_percent = int(current / total * 100) if total else 0

        return render_template('index.html',
                               definition=definition,
                               answer=correct_answer,
                               user_input=user_input,
                               is_correct=is_correct,
                               example=example,
                               selected_chapter=chapter,
                               progress_total=total,
                               progress_current=current,
                               progress_percent=progress_percent,
                               correct_count=score_tracker[key]["correct"],
                               wrong_count=score_tracker[key]["wrong"])
