import fitz
import re

def extract_vocab_from_pdf(file_path, chapter):
    doc = fitz.open(file_path)
    vocab_quads = []

    current_word = None
    meaning_lines = []
    example = ""
    collecting_meaning = False

    has_kor = lambda s: re.search(r'[ㄱ-ㅎ가-힣]', s)

    def clean_word(word):
        word = re.sub(r'\(.*?[ㄱ-ㅎ가-힣]+.*?\)', '', word)  # 괄호+한글 제거
        word = re.sub(r'[ㄱ-ㅎ가-힣]', '', word)             # 남은 한글 제거
        return word.strip()

    def is_vocab_line(line):
        return (
            re.match(r'^\d+[.)]?\s+.+$', line) or           # 기존 방식 유지
            (re.match(r'^[A-Z][a-zA-Z\s/-]{2,}$', line) and not has_kor(line))  # 추가 조건
        )

    for page in doc:
        lines = page.get_text().splitlines()

        for line in lines:
            line = line.strip()

            # 단어 시작 줄
            if is_vocab_line(line):
                # 이전 단어 저장
                if current_word and meaning_lines:
                    meaning = " ".join(meaning_lines).strip()
                    if not has_kor(meaning):
                        vocab_quads.append((current_word, meaning, example.strip(), chapter))
                # 새 단어 준비
                raw_word = re.sub(r'^\d+[.)]?\s+', '', line).strip()
                current_word = clean_word(raw_word)
                meaning_lines, example = [], ""
                collecting_meaning = True
                continue

            # Meaning 시작 줄 (선택적)
            if re.match(r'^[•\s]*meaning[:\-]?', line, re.I):
                first_meaning = re.sub(r'^[•\s]*meaning[:\-]?\s*', '', line, flags=re.I).strip()
                meaning_lines = [first_meaning] if first_meaning else []
                collecting_meaning = True
                continue

            # Example 줄 감지
            if re.match(r'^[•\s]*(example|example sentence)[:\-]?', line, re.I):
                example = re.sub(r'^[•\s]*(example|example sentence)[:\-]?\s*', '', line, flags=re.I).strip()
                continue

            # 뜻 수집 계속
            if collecting_meaning:
                if line.lower().startswith("chapter") or is_vocab_line(line):
                    collecting_meaning = False
                    continue
                if line:
                    meaning_lines.append(line)

    # 마지막 단어 처리
    if current_word and meaning_lines:
        meaning = " ".join(meaning_lines).strip()
        if not has_kor(meaning):
            vocab_quads.append((current_word, meaning, example.strip(), chapter))

    return vocab_quads
