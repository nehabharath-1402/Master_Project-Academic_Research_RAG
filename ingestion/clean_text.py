from pathlib import Path
import re

INPUT_DIR = Path("output")
CLEAN_DIR = Path("output/cleaned")
CLEAN_DIR.mkdir(exist_ok=True)

def clean_text(text: str) -> str:
    # Remove page numbers like "Page 1"
    text = re.sub(r'Page \d+', '', text)

    # Remove multiple empty lines
    text = re.sub(r'\n\s*\n', '\n\n', text)

    # Strip extra spaces
    text = re.sub(r'[ \t]+', ' ', text)

    # Normalize line breaks within paragraphs
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)

    return text.strip()

def main():
    for txt_file in INPUT_DIR.glob("*.txt"):
        print(f"Cleaning: {txt_file.name}")
        with open(txt_file, "r", encoding="utf-8") as f:
            text = f.read()

        cleaned_text = clean_text(text)

        output_file = CLEAN_DIR / txt_file.name
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        print(f"Saved cleaned text to: {output_file}")

if __name__ == "__main__":
    main()