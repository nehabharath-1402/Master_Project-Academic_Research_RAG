from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter

INPUT_DIR = Path("output/cleaned")
OUTPUT_DIR = Path("output/chunks_with_metadata")
OUTPUT_DIR.mkdir(exist_ok=True)

def get_section_name(text):
    # Simple example: take the first line as section
    first_line = text.split("\n")[0]
    return first_line.strip() if first_line else "Unknown"

def main():
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    for txt_file in INPUT_DIR.glob("*.txt"):
        print(f"Processing: {txt_file.name}")
        with open(txt_file, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = splitter.split_text(text)

        for i, chunk in enumerate(chunks):
            section = get_section_name(chunk)
            metadata = {
                "document_id": txt_file.stem,
                "section_name": section,
                "chunk_id": i+1
            }

            output_file = OUTPUT_DIR / f"{txt_file.stem}_chunk_{i+1}.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"METADATA: {metadata}\n\n{chunk}")

        print(f"Saved {len(chunks)} chunks with metadata for {txt_file.name}")

if __name__ == "__main__":
    main()