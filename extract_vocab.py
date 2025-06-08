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
        word = re.sub(r'\(.*?[ㄱ-ㅎ가-힣]+.*?\)', '', word)
        word = re.sub(r'[ㄱ-ㅎ가-힣]', '', word)
        return word.strip()

    def is_vocab_line(line):
        return (
            re.match(r'^\d+[.)]?\s+.+$', line) or
            (re.match(r'^[A-Z][a-zA-Z\s/-]{2,}$', line) and not has_kor(line))
        )

    def trim_meaning(meaning):
        if '.' in meaning:
            return meaning.split('.')[0].strip()
        return meaning.strip()

    def clean_example(ex):
        return re.sub(r'^(sentence|example sentence|example)[:\-]?\s*', '', ex.strip(), flags=re.I)

    for page in doc:
        lines = page.get_text().splitlines()

        for line in lines:
            line = line.strip()

            if is_vocab_line(line):
                if current_word and meaning_lines:
                    raw_meaning = " ".join(meaning_lines).strip()
                    meaning = trim_meaning(raw_meaning)
                    if not has_kor(meaning):
                        vocab_quads.append((current_word, meaning, example.strip(), chapter))
                raw_word = re.sub(r'^\d+[.)]?\s+', '', line).strip()
                current_word = clean_word(raw_word)
                meaning_lines, example = [], ""
                collecting_meaning = True
                continue

            if re.match(r'^[•\s]*meaning[:\-]?', line, re.I):
                first_meaning = re.sub(r'^[•\s]*meaning[:\-]?\s*', '', line, flags=re.I).strip()
                meaning_lines = [first_meaning] if first_meaning else []
                collecting_meaning = True
                continue

            if re.match(r'^[•\s]*(example|example sentence|sentence)[:\-]?', line, re.I):
                example_text = re.sub(r'^[•\s]*(example|example sentence|sentence)[:\-]?\s*', '', line, flags=re.I).strip()
                example = clean_example(example_text)
                continue

            if collecting_meaning:
                if line.lower().startswith("chapter") or is_vocab_line(line):
                    collecting_meaning = False
                    continue
                if line:
                    meaning_lines.append(line)

    if current_word and meaning_lines:
        raw_meaning = " ".join(meaning_lines).strip()
        meaning = trim_meaning(raw_meaning)
        if not has_kor(meaning):
            vocab_quads.append((current_word, meaning, example.strip(), chapter))

    return vocab_quads