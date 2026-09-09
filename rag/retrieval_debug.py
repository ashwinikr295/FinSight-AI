from rag.rag_pipeline import process_rag_query

def debug_retrieval(query: str, company: str = None):
    res = process_rag_query(query, company_name=company)
    print(f"\n--- Debug RAG Query: {query} ---")
    print(f"Answer:\n{res['answer']}\n")
    print("Citations:")
    for c in res['citations']:
        print(f"[{c['id']}] {c['company_name']} ({c['fiscal_year']}) - {c['section_title']} ({c['confidence']})")

if __name__ == "__main__":
    debug_retrieval("Why did revenue increase in 2024?")
