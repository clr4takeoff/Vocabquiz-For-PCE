import fitz
import re

def extract_vocab_from_pdf(file_path, chapter):
    doc = fitz.open(file_path)
    vocab_quads = []

    current_word = None
    collecting_meaning = False
    meaning_lines = []
    example = ""

    def contains_korean(text):
        return bool(re.search(r'[ㄱ-ㅎ가-힣]', text))

    for page in doc:
        lines = page.get_text().splitlines()

        for line in lines:
            line = line.strip()

            if collecting_meaning:
                if line.lower().startswith("example sentence:") or line.lower().startswith("example:"):
                    example = line.split(":", 1)[-1].strip()
                    collecting_meaning = False
                    if current_word and meaning_lines:
                        meaning = " ".join(meaning_lines).strip()
                        if not contains_korean(meaning) and not contains_korean(example):
                            vocab_quads.append((current_word, meaning, example, chapter))
                    current_word = None
                    meaning_lines = []
                    example = ""
                elif re.match(r'^[0-9]+[.)]', line):
                    collecting_meaning = False
                    meaning = " ".join(meaning_lines).strip()
                    if current_word and meaning and not contains_korean(meaning):
                        vocab_quads.append((current_word, meaning, "", chapter))
                    current_word = None
                    meaning_lines = []
                else:
                    meaning_lines.append(line)
                continue

            if re.match(r'^\d+[.)]?\s+.+$', line):
                parts = line.split(maxsplit=1)
                current_word = parts[1].strip() if len(parts) > 1 else parts[0].strip()
            elif (
                line
                and not line.startswith("•")
                and line[0].isupper()
                and len(line.split()) <= 3
                and not line.lower().startswith("lesson")
                and not line.lower().startswith("here's")
            ):
                current_word = line.strip()
            elif line.lower().startswith("meaning:"):
                meaning_lines = [line.split(":", 1)[-1].strip()]
                collecting_meaning = True

    return vocab_quads
