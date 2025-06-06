import fitz
import re

def extract_vocab_from_pdf(file_path, chapter):
    doc = fitz.open(file_path)
    vocab_quads = []

    current_word = None
    collecting_meaning = False
    meaning_lines = []
    example = ""

    has_kor = lambda s: re.search(r'[ㄱ-ㅎ가-힣]', s)

    for page in doc:
        lines = page.get_text().splitlines()

        for i, line in enumerate(lines):
            line = line.strip()

            # 단어 시작 조건
            if re.match(r'^\d+[.)]?\s+.+$', line):
                if current_word and meaning_lines:
                    # 의미 저장 (예문이 없는 경우 포함)
                    meaning = re.sub(r'[•\.\-\s]+$', '', " ".join(meaning_lines).strip())
                    if not has_kor(meaning):
                        vocab_quads.append((current_word, meaning, example, chapter))
                # 새 단어로 초기화
                current_word = line.split(maxsplit=1)[1].strip()
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
