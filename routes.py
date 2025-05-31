import os, re, random
from flask import render_template, request, redirect, url_for, session
from extract_vocab import extract_vocab_from_pdf
from tracker import vocab_list, shown_history, score_tracker


def ensure_tracking_initialized(key):
    if key not in shown_history:
        shown_history[key] = []
    if key not in score_tracker:
        score_tracker[key] = {"correct": 0, "wrong": 0}


def register_routes(app):
    if not app.secret_key:
        app.secret_key = os.getenv("SECRET_KEY", "devkey")

    if not vocab_list:
        for filename in os.listdir("contents"):
            if filename.endswith(".pdf"):
                path = os.path.join("contents", filename)
                match = re.search(r"chapter\s*([1-3])", filename, re.IGNORECASE)
                if match:
                    chapter = match.group(1)
                    vocab_list.extend(extract_vocab_from_pdf(path, chapter))
                else:
                    print(f"챕터 정보 추출 실패: {filename}")
        print(f"총 단어 수: {len(vocab_list)}개")

    @app.route("/")
    def index():
        chapter = request.args.get("chapter", "") or ""
        key = chapter or "all"
        from_next = session.pop("from_next", False)
        if not from_next:
            shown_history[key] = []
            score_tracker[key] = {"correct": 0, "wrong": 0}
            session.pop("current_word", None)
        ensure_tracking_initialized(key)
        saved = session.get("current_word")
        if saved and saved.get("chapter") == chapter:
            idx = saved["idx"]
        else:
            filtered_all = [
                v for v in vocab_list if not chapter or str(v[3]) == chapter
            ]
            if not filtered_all:
                return "해당 챕터에 단어가 없습니다."
            idx = random.randrange(len(filtered_all))
            session["current_word"] = {"idx": idx, "chapter": chapter}
        filtered = [v for v in vocab_list if not chapter or str(v[3]) == chapter]
        word = filtered[idx]
        total = len(filtered)
        progress_current = len(shown_history[key])
        progress_percent = int(progress_current / total * 100) if total else 0
        return render_template(
            "index.html",
            definition=word[1],
            answer=word[0],
            example=word[2],
            selected_chapter=chapter,
            user_input=None,
            progress_total=total,
            progress_current=progress_current,
            progress_percent=progress_percent,
            correct_count=score_tracker[key]["correct"],
            wrong_count=score_tracker[key]["wrong"],
        )

    @app.route("/next", methods=["POST"])
    def next_word():
        chapter = request.form.get("chapter", "") or ""
        key = chapter or "all"
        ensure_tracking_initialized(key)
        filtered = [v for v in vocab_list if not chapter or str(v[3]) == chapter]
        total = len(filtered)
        if not total:
            return "해당 챕터에 단어가 없습니다."
        used = [i for i in shown_history[key] if i < total]
        available = list(set(range(total)) - set(used)) or list(range(total))
        idx = random.choice(available)
        shown_history[key].append(idx)
        session["current_word"] = {"idx": idx, "chapter": chapter}
        session["from_next"] = True
        return redirect(url_for("index", chapter=chapter))

    @app.route("/check", methods=["POST"])
    def check():
        user_input = request.form["user_input"]
        correct_answer = request.form["correct_answer"]
        definition = request.form["definition"]
        example = request.form.get("example", "")
        chapter = request.form.get("chapter", "") or ""
        key = chapter or "all"
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
        return render_template(
            "index.html",
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
            wrong_count=score_tracker[key]["wrong"],
        )
