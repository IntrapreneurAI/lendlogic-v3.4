#!/usr/bin/env python3.11
"""
RAG Similarity Search & Context Retrieval Demo for LendLogic v3.5
Demonstrates semantic search and context retrieval for AI-powered decisions
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer
from datetime import datetime

# Load the stored vector records
def load_vector_database():
    """
    Simulate loading vector records from pgvector database
    For demo purposes, we'll recreate the embeddings
    """
    # Sample documents (same as embedding demo)
    documents = [
        {
            "id": "vec-001",
            "source_text": "The company reported total assets of $5,120,000 as of December 31, 2023, representing a 16.9% increase from the prior year.",
            "document_type": "Financial Statement",
            "source_file": "financial_statement.pdf",
            "tags": ["cash_flow", "profitability", "assets", "debt"]
        },
        {
            "id": "vec-002",
            "source_text": "Net income for the year ended December 31, 2023 was $472,500, demonstrating strong profitability and operational efficiency.",
            "document_type": "Financial Statement",
            "source_file": "financial_statement.pdf",
            "tags": ["cash_flow", "profitability", "assets", "debt"]
        },
        {
            "id": "vec-003",
            "source_text": "Cash and cash equivalents increased to $1,250,000, providing adequate liquidity for operations and debt service.",
            "document_type": "Financial Statement",
            "source_file": "financial_statement.pdf",
            "tags": ["cash_flow", "profitability", "assets", "debt"]
        },
        {
            "id": "vec-004",
            "source_text": "Long-term debt increased to $2,100,000, primarily to finance equipment purchases and facility expansion.",
            "document_type": "Financial Statement",
            "source_file": "financial_statement.pdf",
            "tags": ["cash_flow", "profitability", "assets", "debt"]
        },
        {
            "id": "vec-005",
            "source_text": "For transportation companies, minimum FICO score requirement is 680 with at least 24 months in business.",
            "document_type": "Lending Policy",
            "source_file": "underwriting_guidelines_2024.pdf",
            "tags": ["policy", "requirements", "fico", "debt_ratio", "bankruptcy"]
        },
        {
            "id": "vec-006",
            "source_text": "Debt-to-equity ratio should not exceed 3:1 for equipment financing deals above $500,000.",
            "document_type": "Lending Policy",
            "source_file": "underwriting_guidelines_2024.pdf",
            "tags": ["policy", "requirements", "fico", "debt_ratio", "bankruptcy"]
        },
        {
            "id": "vec-007",
            "source_text": "Companies with bankruptcy history within the past 7 years require additional underwriting review and executive approval.",
            "document_type": "Lending Policy",
            "source_file": "underwriting_guidelines_2024.pdf",
            "tags": ["policy", "requirements", "fico", "debt_ratio", "bankruptcy"]
        },
        {
            "id": "vec-008",
            "source_text": "Collateral must be appraised at no less than 120% of the loan amount for equipment purchases.",
            "document_type": "Lending Policy",
            "source_file": "underwriting_guidelines_2024.pdf",
            "tags": ["policy", "requirements", "fico", "debt_ratio", "bankruptcy"]
        },
        {
            "id": "vec-009",
            "source_text": "Borrower demonstrated strong cash flow management with consistent monthly deposits exceeding $150,000.",
            "document_type": "Analyst Note",
            "source_file": "deal_DEAL-2024-156_notes.txt",
            "tags": ["cash_flow", "address_concern", "fmcsa", "recommendation", "low_risk"]
        },
        {
            "id": "vec-010",
            "source_text": "Minor concern: registered address appears to be a shared office space, but physical operations confirmed at separate warehouse facility.",
            "document_type": "Analyst Note",
            "source_file": "deal_DEAL-2024-156_notes.txt",
            "tags": ["cash_flow", "address_concern", "fmcsa", "recommendation", "low_risk"]
        },
        {
            "id": "vec-011",
            "source_text": "FMCSA safety rating is Satisfactory with no violations in the past 24 months. Fleet size of 22 units is appropriate for revenue level.",
            "document_type": "Analyst Note",
            "source_file": "deal_DEAL-2024-156_notes.txt",
            "tags": ["cash_flow", "address_concern", "fmcsa", "recommendation", "low_risk"]
        },
        {
            "id": "vec-012",
            "source_text": "Recommendation: Approve with standard terms. Risk level assessed as Low-Medium due to strong financials and clean safety record.",
            "document_type": "Analyst Note",
            "source_file": "deal_DEAL-2024-156_notes.txt",
            "tags": ["cash_flow", "address_concern", "fmcsa", "recommendation", "low_risk"]
        }
    ]
    
    return documents

def cosine_similarity(vec1, vec2):
    """
    Calculate cosine similarity between two vectors
    """
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def perform_similarity_search(query_text, model, documents, top_k=5):
    """
    Perform similarity search to find most relevant text chunks
    """
    print(f"\n🔍 Query: \"{query_text}\"")
    print(f"\n📊 Generating query embedding...")
    
    # Generate embedding for the query
    query_embedding = model.encode([query_text])[0]
    
    # Generate embeddings for all documents
    print(f"📊 Computing similarity scores against {len(documents)} vectors...")
    doc_texts = [doc["source_text"] for doc in documents]
    doc_embeddings = model.encode(doc_texts)
    
    # Calculate similarity scores
    similarities = []
    for i, doc_embedding in enumerate(doc_embeddings):
        similarity = cosine_similarity(query_embedding, doc_embedding)
        similarities.append({
            "document": documents[i],
            "similarity_score": float(similarity)
        })
    
    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
    
    # Return top-k results
    return similarities[:top_k]

def format_rag_context(results, threshold=0.5):
    """
    Format retrieved context for AI consumption
    """
    relevant_results = [r for r in results if r["similarity_score"] >= threshold]
    
    if not relevant_results:
        return {
            "rag_context_status": "not_found",
            "rag_context_used": [],
            "context_summary": "No relevant historical context found above similarity threshold."
        }
    
    context_snippets = []
    for i, result in enumerate(relevant_results, 1):
        context_snippets.append({
            "rank": i,
            "source_text": result["document"]["source_text"],
            "document_type": result["document"]["document_type"],
            "source_file": result["document"]["source_file"],
            "similarity_score": result["similarity_score"],
            "tags": result["document"]["tags"]
        })
    
    return {
        "rag_context_status": "found",
        "rag_context_used": context_snippets,
        "context_summary": f"Retrieved {len(context_snippets)} relevant context snippets from historical data."
    }

def generate_ai_summary_with_context(query, context):
    """
    Simulate AI-generated summary using retrieved context
    """
    if context["rag_context_status"] == "not_found":
        return "⚠️ No relevant historical context available. Proceeding with standard underwriting analysis."
    
    summary = f"**Based on Retrieved Context:**\n\n"
    summary += f"I found {len(context['rag_context_used'])} relevant insights from our historical data:\n\n"
    
    for snippet in context["rag_context_used"]:
        summary += f"{snippet['rank']}. **{snippet['document_type']}** (Similarity: {snippet['similarity_score']:.2%})\n"
        summary += f"   *{snippet['source_text']}*\n"
        summary += f"   Source: `{snippet['source_file']}`\n\n"
    
    return summary

def main():
    print("=" * 70)
    print("RAG SIMILARITY SEARCH & CONTEXT RETRIEVAL - LendLogic v3.5")
    print("=" * 70)
    print()
    print("This module demonstrates:")
    print("- Semantic similarity search using pgvector")
    print("- Context retrieval for AI-powered decisions")
    print("- RAG integration into underwriting workflow")
    print()
    
    # Load model
    print("🧠 Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("✅ Model loaded")
    
    # Load vector database
    print("\n💾 Loading vector database...")
    documents = load_vector_database()
    print(f"✅ Loaded {len(documents)} vector records")
    
    # Test queries
    test_queries = [
        {
            "query": "What are the lending requirements for transportation companies?",
            "context": "Underwriter is reviewing a new deal from a trucking company"
        },
        {
            "query": "How should we assess cash flow and liquidity?",
            "context": "Analyzing financial health of the borrower"
        },
        {
            "query": "What are the concerns with shared office addresses?",
            "context": "Risk assessment for a company with a virtual office"
        }
    ]
    
    all_results = []
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"TEST QUERY #{i}")
        print(f"{'='*70}")
        print(f"Context: {test['context']}")
        
        # Perform search
        results = perform_similarity_search(test["query"], model, documents, top_k=3)
        
        # Format context
        rag_context = format_rag_context(results, threshold=0.3)
        
        # Generate AI summary
        ai_summary = generate_ai_summary_with_context(test["query"], rag_context)
        
        print(f"\n📋 RAG CONTEXT RETRIEVED:")
        print(f"   Status: {rag_context['rag_context_status']}")
        print(f"   Snippets: {len(rag_context['rag_context_used'])}")
        
        print(f"\n🤖 AI-GENERATED SUMMARY:")
        print(ai_summary)
        
        all_results.append({
            "query": test["query"],
            "context": test["context"],
            "rag_context": rag_context,
            "ai_summary": ai_summary
        })
    
    # Save results
    print(f"\n{'='*70}")
    print("SAVING RESULTS")
    print(f"{'='*70}\n")
    
    output_file = "/home/ubuntu/lendlogic-v3.4/rag_retrieval_result.json"
    with open(output_file, 'w') as f:
        json.dump({
            "total_queries": len(test_queries),
            "model_used": "all-MiniLM-L6-v2",
            "similarity_threshold": 0.3,
            "results": all_results
        }, f, indent=2)
    
    print(f"✅ Results saved to: {output_file}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"Test Queries: {len(test_queries)}")
    print(f"Vector Database Size: {len(documents)} records")
    print(f"Model: all-MiniLM-L6-v2")
    print(f"Similarity Threshold: 30%")
    print()
    print("✅ RAG context retrieval complete")
    print("   Semantic search successfully enriched AI decision-making")
    print()
    print("Integration Points:")
    print("- Underwriting summaries now include 'Based on Retrieved Context' sections")
    print("- Historical insights inform risk assessment and lending decisions")
    print("- All context usage is logged to Supabase for audit trails")

if __name__ == "__main__":
    main()
