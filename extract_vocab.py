import fitz  # PyMuPDF
import re

def extract_vocab_from_pdf(file_path):
    doc = fitz.open(file_path)
    vocab_pairs = []

    current_word = None
    collecting_meaning = False
    meaning_lines = []

    for page in doc:
        text = page.get_text()
        lines = text.splitlines()

        for line in lines:
            line = line.strip()

            # 뜻 수집 중
            if collecting_meaning:
                if line.lower().startswith("example:") or re.search(r'^[0-9]+[.)]', line):
                    # 뜻 끝
                    full_meaning = " ".join(meaning_lines).strip()
                    if current_word and full_meaning and not re.search(r'[ㄱ-ㅎ가-힣]', full_meaning):
                        vocab_pairs.append((current_word, full_meaning))
                    collecting_meaning = False
                    meaning_lines = []
                    current_word = None
                else:
                    meaning_lines.append(line)
                    continue

            # 단어 줄
            if re.match(r'^\d+[.)]?\s+[A-Za-z][A-Za-z\s\-]+$', line):
                # 예: "1. Complaint", "2) Analyze"
                parts = line.split(maxsplit=1)
                current_word = parts[1].strip() if len(parts) > 1 else parts[0].strip()

            elif line and line.lower().startswith("meaning:"):
                # 뜻 시작
                english_meaning = line.split("Meaning:")[-1].strip()
                if english_meaning:
                    meaning_lines = [english_meaning]
                else:
                    meaning_lines = []
                collecting_meaning = True

    # 마지막 처리
    if current_word and meaning_lines:
        full_meaning = " ".join(meaning_lines).strip()
        if not re.search(r'[ㄱ-ㅎ가-힣]', full_meaning):  # 한글 제거
            vocab_pairs.append((current_word, full_meaning))

    return vocab_pairs
