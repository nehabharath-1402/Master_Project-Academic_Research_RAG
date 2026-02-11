from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter

INPUT_DIR = Path("output/cleaned")
CHUNK_DIR = Path("output/chunks")
CHUNK_DIR.mkdir(exist_ok=True)

def main():
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    for txt_file in INPUT_DIR.glob("*.txt"):
        print(f"Chunking: {txt_file.name}")
        with open(txt_file, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = text_splitter.split_text(text)

        for i, chunk in enumerate(chunks):
            output_file = CHUNK_DIR / f"{txt_file.stem}_chunk_{i+1}.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(chunk)

        print(f"Saved {len(chunks)} chunks for {txt_file.name}")

if __name__ == "__main__":
    main()