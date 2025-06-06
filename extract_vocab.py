import fitz
import re

def extract_vocab_from_pdf(file_path, chapter):
    doc = fitz.open(file_path)
    vocab_quads = []

    current_word = None
    meaning_lines = []
    example = ""
    collecting_meaning = False

    # 한글 포함 여부
    has_kor = lambda s: re.search(r'[ㄱ-ㅎ가-힣]', s)

    # 단어 정제: 괄호 내 한글 및 전체 한글 제거
    def clean_word(word):
        word = re.sub(r'\(.*?[ㄱ-ㅎ가-힣]+.*?\)', '', word)  # 괄호+한글 제거
        word = re.sub(r'[ㄱ-ㅎ가-힣]', '', word)             # 남은 한글 제거
        return word.strip()

    for page in doc:
        lines = page.get_text().splitlines()

        for line in lines:
            line = line.strip()

            # 새 단어 시작
            if re.match(r'^\d+[.)]?\s+.+$', line):
                # 이전 단어 저장 (있다면)
                if current_word and meaning_lines:
                    meaning = " ".join(meaning_lines).strip()
                    if not has_kor(meaning):
                        vocab_quads.append((current_word, meaning, example.strip(), chapter))
                # 상태 초기화 후 새 단어 추출
                raw_word = line.split(maxsplit=1)[1].strip()
                current_word = clean_word(raw_word)
                meaning_lines, example = [], ""
                collecting_meaning = False
                continue

            # Meaning 시작
            if re.match(r'^[•\s]*meaning:', line, re.I):
                first_meaning = re.sub(r'^[•\s]*meaning:\s*', '', line, flags=re.I).strip()
                meaning_lines = [first_meaning] if first_meaning else []
                collecting_meaning = True
                continue

            # 예문 처리 (뜻이 있는 경우만 저장)
            if re.match(r'^(example|example sentence):', line, re.I):
                if current_word and meaning_lines:
                    example = re.sub(r'^(example|example sentence):\s*', '', line, flags=re.I).strip()
                continue

            # 의미 계속 수집
            if collecting_meaning:
                if line == "" or line.lower().startswith("chapter"):
                    collecting_meaning = False
                    continue
                meaning_lines.append(line)

    # 마지막 단어 처리
    if current_word and meaning_lines:
        meaning = " ".join(meaning_lines).strip()
        if not has_kor(meaning):
            vocab_quads.append((current_word, meaning, example.strip(), chapter))

    return vocab_quads
