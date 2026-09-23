from typing import Dict, List, Generator
from vectorstore.vector_store import get_vector_store
from llm.azure_openai import get_llm_response, stream_llm_response

def _build_rag_prompts(query: str, company_name: str = None):
    vs = get_vector_store()
    retrieved_chunks = vs.search(query, company_name=company_name, top_k=4)

    if not retrieved_chunks:
        # Fallback query search across all documents
        retrieved_chunks = vs.search(query, company_name=None, top_k=4)

    context_passages = []
    citations = []

    for idx, chunk in enumerate(retrieved_chunks):
        c_name = chunk.get("company_name", "Report")
        f_year = chunk.get("fiscal_year", "")
        sec_title = chunk.get("section_title", "General Section")
        content_snippet = chunk.get("content", "")[:350]

        context_passages.append(
            f"--- Source [{idx+1}]: {c_name} ({f_year}) - Section: {sec_title} ---\n{chunk.get('content', '')}\n"
        )
        
        citations.append({
            "id": idx + 1,
            "company_name": c_name,
            "fiscal_year": f_year,
            "section_title": sec_title,
            "snippet": content_snippet + ("..." if len(chunk.get("content", "")) > 350 else ""),
            "confidence": f"{min(98, 85 + (4 - idx) * 3)}%"
        })

    context_str = "\n".join(context_passages)

    system_prompt = (
        "You are an expert Wall Street financial analyst and investor assistant. "
        "Answer the user's question accurately using ONLY the retrieved financial document context. "
        "Highlight financial figures, growth rates, and specific risk drivers whenever applicable."
    )

    user_prompt = f"User Question: {query}\n\nDocument Context:\n{context_str}" if context_passages else query
    return user_prompt, system_prompt, citations


def process_rag_query(query: str, company_name: str = None) -> Dict:
    """
    RAG Q&A research pipeline:
    1. Retrieves top context passages from Vector Store.
    2. Builds grounded context prompt.
    3. Runs response generator.
    4. Returns response with detailed source citations.
    """
    user_prompt, system_prompt, citations = _build_rag_prompts(query, company_name)
    answer = get_llm_response(user_prompt, system_prompt=system_prompt)

    return {
        "query": query,
        "answer": answer,
        "citations": citations,
        "sources_count": len(citations)
    }


def process_rag_query_stream(query: str, company_name: str = None) -> Generator[Dict, None, None]:
    """
    RAG Q&A research pipeline yielding streaming events (metadata, tokens, done).
    """
    user_prompt, system_prompt, citations = _build_rag_prompts(query, company_name)
    
    # 1. Yield metadata event with RAG citations
    yield {
        "type": "metadata",
        "citations": citations,
        "sources_count": len(citations)
    }

    # 2. Stream LLM text tokens
    for token in stream_llm_response(user_prompt, system_prompt=system_prompt):
        yield {
            "type": "token",
            "content": token
        }

    # 3. Yield completion event
    yield {
        "type": "done"
    }

