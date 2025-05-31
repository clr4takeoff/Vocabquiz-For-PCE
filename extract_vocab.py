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

        for line in lines:
            line = line.strip()

            if line.startswith("뜻:") or line.count("• Meaning:") > 1:
                continue

            if collecting_meaning:
                if line.lower().startswith(("example sentence:", "example:")):
                    example = line.split(":", 1)[-1].strip()
                    collecting_meaning = False

                    if current_word and meaning_lines:
                        meaning = re.sub(r'[•\.\-\s]+$', '', " ".join(meaning_lines).strip())
                        if not (has_kor(meaning) or has_kor(example)):
                            vocab_quads.append((current_word, meaning, example, chapter))

                    current_word = None
                    meaning_lines, example = [], ""
                    continue

                if re.match(r'^[0-9]+[.)]', line):
                    collecting_meaning = False
                    meaning = " ".join(meaning_lines).strip()
                    if current_word and meaning and not has_kor(meaning):
                        vocab_quads.append((current_word, meaning, "", chapter))

                    current_word = None
                    meaning_lines = []
                    continue

                meaning_lines.append(line)
                continue

            if re.match(r'^\d+[.)]?\s+.+$', line):
                current_word = line.split(maxsplit=1)[1].strip()
            elif (
                line
                and not line.startswith("•")
                and line[0].isupper()
                and len(line.split()) <= 3
                and not line.lower().startswith(("lesson", "here's"))
            ):
                current_word = line.strip()
            elif re.match(r'^[•\s]*meaning:', line, re.I):
                first = re.sub(r'^[•\s]*meaning:\s*', '', line, flags=re.I).strip()
                meaning_lines = [first] if first else []
                collecting_meaning = True

    return vocab_quads
