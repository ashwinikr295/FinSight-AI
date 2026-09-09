import re
from typing import List, Dict

def create_semantic_chunks(markdown_content: str, company_name: str, fiscal_year: int, doc_id: str) -> List[Dict]:
    """
    Splits markdown financial document into semantic chunks preserving headers and context.
    """
    # Split by headers (e.g., #, ##, ###) or page breaks
    raw_sections = re.split(r'\n(?=#+ |\n## Page )', markdown_content)
    
    chunks = []
    chunk_index = 0
    
    for section in raw_sections:
        section = section.strip()
        if not section:
            continue
            
        # Detect section title if present
        header_match = re.match(r'^(#+\s*|\n## Page \d+\s*)([^\n]+)', section)
        section_title = header_match.group(2) if header_match else "Financial Content"
        
        # If section is very long, split into paragraphs/paragraphs groups (~500 words per chunk)
        paragraphs = section.split('\n\n')
        current_chunk_text = ""
        
        for para in paragraphs:
            if len(current_chunk_text) + len(para) > 1200:
                chunk_index += 1
                chunks.append({
                    "chunk_id": f"{doc_id}_chunk_{chunk_index}",
                    "doc_id": doc_id,
                    "company_name": company_name,
                    "fiscal_year": fiscal_year,
                    "section_title": section_title,
                    "content": current_chunk_text.strip()
                })
                current_chunk_text = para + "\n\n"
            else:
                current_chunk_text += para + "\n\n"
                
        if current_chunk_text.strip():
            chunk_index += 1
            chunks.append({
                "chunk_id": f"{doc_id}_chunk_{chunk_index}",
                "doc_id": doc_id,
                "company_name": company_name,
                "fiscal_year": fiscal_year,
                "section_title": section_title,
                "content": current_chunk_text.strip()
            })
            
    print(f"Generated {len(chunks)} semantic chunks for {company_name} ({fiscal_year}).")
    return chunks