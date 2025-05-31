import fitz
import re

def extract_vocab_from_pdf(file_path):
    doc = fitz.open(file_path)
    vocab_triples = []
    
    current_word = None
    collecting_meaning = False
    meaning_lines = []
    example = ""

    for page in doc:
        lines = page.get_text().splitlines()
        
        for line in lines:
            line = line.strip()

            if collecting_meaning:
                if line.lower().startswith("example:"):
                    example = line.split("Example:")[-1].strip()
                    collecting_meaning = False
                    if current_word and meaning_lines:
                        meaning = " ".join(meaning_lines).strip()
                        if not re.search(r'[ㄱ-ㅎ가-힣]', meaning):
                            vocab_triples.append((current_word, meaning, example))
                    current_word = None
                    meaning_lines = []
                    example = ""
                elif re.match(r'^[0-9]+[.)]', line):
                    collecting_meaning = False
                    meaning = " ".join(meaning_lines).strip()
                    if current_word and meaning:
                        vocab_triples.append((current_word, meaning, ""))
                    current_word = None
                    meaning_lines = []
                else:
                    meaning_lines.append(line)
                continue

            if re.match(r'^\d+[.)]?\s+[A-Za-z][A-Za-z\s\-]+$', line):
                parts = line.split(maxsplit=1)
                current_word = parts[1].strip() if len(parts) > 1 else parts[0].strip()
            elif line.lower().startswith("meaning:"):
                meaning_lines = [line.split("Meaning:")[-1].strip()]
                collecting_meaning = True

    return vocab_triples
