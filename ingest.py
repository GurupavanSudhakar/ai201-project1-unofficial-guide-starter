import os
import re
import json
import html
import glob
import random

REVIEWS_DIR = "rmp_professor_files"
OUTPUT_DIR = "data/chunks"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "chunks.json")

REVIEW_SPLIT_RE = re.compile(r"^Review #\d+", re.MULTILINE)
PROFESSOR_RE = re.compile(r"^Professor:\s*(.+)", re.MULTILINE)
COMMENT_RE = re.compile(r"^\s*Comment:\s*(.*)", re.MULTILINE)
FIELD_LINE_RE = re.compile(r"^\s+\w[\w\s]*:\s")


def read_file(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(path, encoding="latin-1") as f:
            return f.read()


def extract_professor_name(content):
    m = PROFESSOR_RE.search(content)
    return m.group(1).strip() if m else ""


def extract_comment(block):
    m = COMMENT_RE.search(block)
    if not m:
        return None

    lines = [m.group(1)]
    rest = block[m.end():]

    for line in rest.splitlines():
        if not line.strip():
            break
        if FIELD_LINE_RE.match(line):
            break
        lines.append(line.strip())

    return " ".join(lines)


def clean_text(text):
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def process_file(path):
    content = read_file(path)
    filename = os.path.basename(path)
    professor = extract_professor_name(content)

    parts = REVIEW_SPLIT_RE.split(content)
    # parts[0] is the file header; parts[1:] are review blocks
    chunks = []
    for block in parts[1:]:
        raw = extract_comment(block)
        if not raw:
            continue
        text = clean_text(raw)
        if text:
            chunks.append({"source": filename, "professor": professor, "text": text})

    return chunks


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    txt_files = sorted(glob.glob(os.path.join(REVIEWS_DIR, "*.txt")))
    all_chunks = []

    for path in txt_files:
        file_chunks = process_file(path)
        all_chunks.extend(file_chunks)

    for i, chunk in enumerate(all_chunks, start=1):
        chunk["chunk_id"] = f"chunk_{i:04d}"

    # Reorder keys for readability
    all_chunks = [
        {"chunk_id": c["chunk_id"], "source": c["source"], "professor": c["professor"], "text": c["text"]}
        for c in all_chunks
    ]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"Total chunks: {len(all_chunks)}")
    print(f"Saved to: {OUTPUT_FILE}\n")

    samples = random.sample(all_chunks, min(5, len(all_chunks)))
    print("=== 5 Random Sample Chunks ===\n")
    for chunk in samples:
        print(f"chunk_id : {chunk['chunk_id']}")
        print(f"source   : {chunk['source']}")
        print(f"professor: {chunk['professor']}")
        print(f"text     : {chunk['text']}")
        print()


if __name__ == "__main__":
    main()
