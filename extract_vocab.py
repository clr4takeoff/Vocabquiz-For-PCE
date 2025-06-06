import fitz
import re

def extract_vocab_from_pdf(file_path, chapter):
    doc = fitz.open(file_path)
    vocab_quads = []

    current_word = None
    collecting_meaning = False
    meaning_lines = []
    example = ""

    # 한글 포함 여부 판단
    has_kor = lambda s: re.search(r'[ㄱ-ㅎ가-힣]', s)

    # 단어 정제 함수: 괄호 안 한글 제거 및 불필요한 공백 제거
    def clean_word(word):
        word = re.sub(r'\(.*?[ㄱ-ㅎ가-힣]+.*?\)', '', word)  # 괄호 내 한글 제거
        word = re.sub(r'[ㄱ-ㅎ가-힣]+', '', word)              # 남아있는 한글 제거
        return word.strip()

    for page in doc:
        lines = page.get_text().splitlines()

        for i, line in enumerate(lines):
            line = line.strip()

            # 단어 시작 조건
            if re.match(r'^\d+[.)]?\s+.+$', line):
                if current_word and meaning_lines:
                    meaning = re.sub(r'[•\.\-\s]+$', '', " ".join(meaning_lines).strip())
                    if not has_kor(meaning):
                        vocab_quads.append((current_word, meaning, example, chapter))

                raw_word = line.split(maxsplit=1)[1].strip()
                current_word = clean_word(raw_word)  # 단어 정제 적용
                meaning_lines, example = [], ""
                collecting_meaning = False
                continue

            # Meaning 줄 인식
            if re.match(r'^[•\s]*meaning:', line, re.I):
                first_meaning = re.sub(r'^[•\s]*meaning:\s*', '', line, flags=re.I).strip()
                meaning_lines = [first_meaning] if first_meaning else []
                collecting_meaning = True
                continue

            # 예문 줄 인식
            if collecting_meaning and re.match(r'^(example|example sentence):', line, re.I):
                example = re.sub(r'^(example|example sentence):', '', line, flags=re.I).strip()
                collecting_meaning = False
                continue

            # 의미 줄 계속 수집
            if collecting_meaning:
                if line == "" or line.lower().startswith("chapter"):
                    collecting_meaning = False
                    continue
                meaning_lines.append(line)

    # 마지막 단어 처리
    if current_word and meaning_lines:
        meaning = re.sub(r'[•\.\-\s]+$', '', " ".join(meaning_lines).strip())
        if not has_kor(meaning):
            vocab_quads.append((current_word, meaning, example, chapter))

    return vocab_quads
