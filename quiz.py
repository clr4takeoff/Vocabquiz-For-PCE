from flask import Flask, render_template, request
from extract_vocab import extract_vocab_from_pdf
import random, os

app = Flask(__name__)

# ✅ PDF 폴더 전체에서 단어 불러오기
vocab_list = []
pdf_folder = 'contents'

for filename in os.listdir(pdf_folder):
    if filename.endswith('.pdf'):
        file_path = os.path.join(pdf_folder, filename)
        vocab_list.extend(extract_vocab_from_pdf(file_path))

print(f"✅ 총 {len(vocab_list)}개의 단어가 로딩되었습니다.")

@app.route('/')
def index():
    if not vocab_list:
        return "단어 목록이 비어 있습니다. PDF 내용을 확인하세요."
    word_item = random.choice(vocab_list)
    return render_template('index.html', definition=word_item[1], answer=word_item[0])

@app.route('/check', methods=['POST'])
def check():
    user_input = request.form['user_input']
    correct_answer = request.form['correct_answer']
    definition = request.form['definition']

    is_correct = user_input.strip().lower() == correct_answer.lower()
    
    return render_template('index.html',
                           definition=definition,
                           answer=correct_answer,
                           user_input=user_input,
                           is_correct=is_correct)

if __name__ == '__main__':
    app.run(debug=True)
