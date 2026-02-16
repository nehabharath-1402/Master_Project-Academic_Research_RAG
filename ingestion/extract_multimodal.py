from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List

import fitz  # PyMuPDF


@dataclass
class Element:
    element_type: str  # "text" | "table" | "image"
    page: int
    index: int
    content: str  # text OR markdown table OR (later) image caption/OCR text
    meta: Dict[str, Any]


def _pixmap_to_png_bytes(pix: fitz.Pixmap) -> bytes:
    # Convert CMYK->RGB if needed
    if pix.n - pix.alpha > 3:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    return pix.tobytes("png")


def extract_multimodal(pdf_path: Path, out_dir: Path) -> List[Element]:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "images").mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    elements: List[Element] = []

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        page_num = page_idx + 1

        # TEXT
        text = page.get_text("text").strip()
        if text:
            elements.append(
                Element(
                    element_type="text",
                    page=page_num,
                    index=0,
                    content=text,
                    meta={"source": pdf_path.name},
                )
            )

        # TABLES (PyMuPDF table detector)
        try:
            tables = page.find_tables()
            for t_i, table in enumerate(tables.tables):
                df = table.to_pandas()
                md = df.to_markdown(index=False)
                elements.append(
                    Element(
                        element_type="table",
                        page=page_num,
                        index=t_i,
                        content=md,
                        meta={
                            "source": pdf_path.name,
                            "rows": int(df.shape[0]),
                            "cols": int(df.shape[1]),
                        },
                    )
                )
        except Exception:
            pass

        # IMAGES
        imgs = page.get_images(full=True)
        for i_i, img in enumerate(imgs):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            png_bytes = _pixmap_to_png_bytes(pix)

            img_path = out_dir / "images" / f"{pdf_path.stem}_p{page_num:03d}_img{i_i:02d}.png"
            img_path.write_bytes(png_bytes)

            elements.append(
                Element(
                    element_type="image",
                    page=page_num,
                    index=i_i,
                    content="",  # filled later via caption/OCR
                    meta={"source": pdf_path.name, "image_path": str(img_path)},
                )
            )

    return elements


def save_jsonl(elements: List[Element], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for el in elements:
            f.write(json.dumps(asdict(el), ensure_ascii=False) + "\n")


if __name__ == "__main__":
    pdf = Path("data/raw_pdfs")  # folder
    out_dir = Path("output/multimodal")

    pdfs = list(pdf.glob("*.pdf"))
    if not pdfs:
        raise SystemExit("No PDFs found in data/raw_pdfs")

    all_elements: List[Element] = []
    for p in pdfs:
        all_elements.extend(extract_multimodal(p, out_dir))

    save_jsonl(all_elements, out_dir / "elements.jsonl")
    print(f"Extracted {len(all_elements)} elements -> {out_dir/'elements.jsonl'}")
