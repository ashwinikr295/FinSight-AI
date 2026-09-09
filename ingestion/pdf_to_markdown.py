import os
from pathlib import Path
from config.settings import MARKDOWN_DIR

def convert_pdf_to_markdown(pdf_path: str, company_name: str, fiscal_year: int) -> str:
    """
    Converts annual report PDF to Markdown text format.
    Uses PyMuPDF4LLM or PyMuPDF if available, with robust fallback text parser.
    """
    filename_stem = Path(pdf_path).stem
    out_md_path = MARKDOWN_DIR / f"{company_name.lower().replace(' ', '_')}_{fiscal_year}_{filename_stem}.md"
    
    markdown_content = ""
    
    # Try PyMuPDF4LLM first
    try:
        import pymupdf4llm
        markdown_content = pymupdf4llm.to_markdown(pdf_path)
    except Exception as e:
        print(f"Notice: PyMuPDF4LLM notice ({e}). Using PyMuPDF / text parser fallback.")
        try:
            import fitz # PyMuPDF
            doc = fitz.open(pdf_path)
            pages_md = []
            for i, page in enumerate(doc):
                text = page.get_text()
                pages_md.append(f"## Page {i+1}\n\n{text}")
            markdown_content = "\n\n".join(pages_md)
        except Exception as e2:
            print(f"Fallback reading raw text file / plain text parser: {e2}")
            # Fallback if file is text/md or simple reader
            with open(pdf_path, 'r', encoding='utf-8', errors='ignore') as f:
                markdown_content = f.read()

    # Add Document Header
    header = f"# Annual Financial Report\n**Company**: {company_name}\n**Fiscal Year**: {fiscal_year}\n\n---\n\n"
    final_content = header + markdown_content

    with open(out_md_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
        
    print(f"Converted {pdf_path} -> {out_md_path}")
    return str(out_md_path)