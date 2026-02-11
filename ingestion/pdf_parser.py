import fitz  # PyMuPDF
from pathlib import Path

PDF_DIR = Path("data/raw_pdfs")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

def extract_text_from_pdf(pdf_path: Path) -> str:
    doc = fitz.open(pdf_path)
    text = []

    for page_num, page in enumerate(doc, start=1):
        page_text = page.get_text()
        if page_text.strip():
            text.append(f"\n--- Page {page_num} ---\n")
            text.append(page_text)

    return "\n".join(text)

def main():
    print("DEBUG: PDFs in folder:", list(PDF_DIR.glob("*.pdf")))
    for pdf_file in PDF_DIR.glob("*.pdf"):
        print(f"Processing: {pdf_file.name}")
        extracted_text = extract_text_from_pdf(pdf_file)

        output_file = OUTPUT_DIR / f"{pdf_file.stem}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(extracted_text)

        print(f"Saved extracted text to: {output_file}")

if __name__ == "__main__":
    main()