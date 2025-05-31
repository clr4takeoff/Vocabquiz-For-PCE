from flask import Flask, render_template, request
from extract_vocab import extract_vocab_from_pdf
import random, os

app = Flask(__name__)

vocab_list = []
for filename in os.listdir('contents'):
    if filename.endswith('.pdf'):
        path = os.path.join('contents', filename)
        vocab_list.extend(extract_vocab_from_pdf(path))

@app.route('/')
def index():
    if not vocab_list:
        return "⚠️ PDF에서 단어를 불러올 수 없습니다. contents 폴더를 확인하세요."

    word_item = random.choice(vocab_list)
    return render_template('index.html',
                           definition=word_item[1],
                           answer=word_item[0],
                           example=word_item[2],
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
