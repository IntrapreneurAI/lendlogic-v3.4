#!/usr/bin/env python3.11
"""
RAG Embedding Generation & Vector Storage Demo for LendLogic v3.5
Demonstrates embedding generation and storage workflow for pgvector integration
"""

import json
from sentence_transformers import SentenceTransformer
from datetime import datetime
import uuid

# Sample financial documents for embedding
SAMPLE_DOCUMENTS = [
    {
        "document_type": "Financial Statement",
        "source_file": "financial_statement.pdf",
        "text_chunks": [
            "The company reported total assets of $5,120,000 as of December 31, 2023, representing a 16.9% increase from the prior year.",
            "Net income for the year ended December 31, 2023 was $472,500, demonstrating strong profitability and operational efficiency.",
            "Cash and cash equivalents increased to $1,250,000, providing adequate liquidity for operations and debt service.",
            "Long-term debt increased to $2,100,000, primarily to finance equipment purchases and facility expansion."
        ],
        "tags": ["cash_flow", "profitability", "assets", "debt"]
    },
    {
        "document_type": "Lending Policy",
        "source_file": "underwriting_guidelines_2024.pdf",
        "text_chunks": [
            "For transportation companies, minimum FICO score requirement is 680 with at least 24 months in business.",
            "Debt-to-equity ratio should not exceed 3:1 for equipment financing deals above $500,000.",
            "Companies with bankruptcy history within the past 7 years require additional underwriting review and executive approval.",
            "Collateral must be appraised at no less than 120% of the loan amount for equipment purchases."
        ],
        "tags": ["policy", "requirements", "fico", "debt_ratio", "bankruptcy"]
    },
    {
        "document_type": "Analyst Note",
        "source_file": "deal_DEAL-2024-156_notes.txt",
        "text_chunks": [
            "Borrower demonstrated strong cash flow management with consistent monthly deposits exceeding $150,000.",
            "Minor concern: registered address appears to be a shared office space, but physical operations confirmed at separate warehouse facility.",
            "FMCSA safety rating is Satisfactory with no violations in the past 24 months. Fleet size of 22 units is appropriate for revenue level.",
            "Recommendation: Approve with standard terms. Risk level assessed as Low-Medium due to strong financials and clean safety record."
        ],
        "tags": ["cash_flow", "address_concern", "fmcsa", "recommendation", "low_risk"]
    }
]

def generate_embeddings(text_chunks, model_name="all-MiniLM-L6-v2"):
    """
    Generate vector embeddings for text chunks using sentence-transformers
    """
    print(f"\n🧠 Loading embedding model: {model_name}...")
    model = SentenceTransformer(model_name)
    
    print(f"✅ Model loaded. Embedding dimension: {model.get_sentence_embedding_dimension()}")
    print(f"\n📊 Generating embeddings for {len(text_chunks)} text chunks...")
    
    embeddings = model.encode(text_chunks, show_progress_bar=True)
    
    print(f"✅ Embeddings generated successfully")
    print(f"   Shape: {embeddings.shape}")
    
    return embeddings, model.get_sentence_embedding_dimension()

def create_vector_records(documents, embeddings_by_doc, embedding_dim):
    """
    Create vector records ready for pgvector storage
    """
    vector_records = []
    deal_id = str(uuid.uuid4())
    company_id = str(uuid.uuid4())
    
    chunk_index = 0
    for doc in documents:
        document_id = str(uuid.uuid4())
        
        for i, text_chunk in enumerate(doc["text_chunks"]):
            embedding = embeddings_by_doc[chunk_index].tolist()
            
            vector_record = {
                "id": str(uuid.uuid4()),
                "deal_id": deal_id,
                "company_id": company_id,
                "document_id": document_id,
                "embedding": embedding,
                "embedding_dimension": embedding_dim,
                "source_text": text_chunk,
                "document_type": doc["document_type"],
                "source_file": doc["source_file"],
                "tags": doc["tags"],
                "created_at": datetime.utcnow().isoformat() + 'Z'
            }
            
            vector_records.append(vector_record)
            chunk_index += 1
    
    return vector_records

def simulate_pgvector_insert(vector_records):
    """
    Simulate inserting vector records into PostgreSQL with pgvector
    """
    print(f"\n💾 Simulating pgvector INSERT operations...")
    print(f"   Total records to insert: {len(vector_records)}")
    print()
    
    # Group by document type for summary
    by_type = {}
    for record in vector_records:
        doc_type = record["document_type"]
        by_type[doc_type] = by_type.get(doc_type, 0) + 1
    
    print("   Records by document type:")
    for doc_type, count in by_type.items():
        print(f"   - {doc_type}: {count} chunks")
    
    print()
    print("   SQL Example (for reference):")
    print("   ```sql")
    print("   INSERT INTO vectors (")
    print("     id, deal_id, company_id, document_id,")
    print("     embedding, source_text, document_type,")
    print("     source_file, tags, created_at")
    print("   ) VALUES (")
    print("     $1, $2, $3, $4, $5, $6, $7, $8, $9, $10")
    print("   );")
    print("   ```")
    print()
    print("✅ Simulated INSERT complete")

def main():
    print("=" * 70)
    print("RAG EMBEDDING GENERATION & VECTOR STORAGE - LendLogic v3.5")
    print("=" * 70)
    print()
    print("This module demonstrates:")
    print("- Generating embeddings from financial documents")
    print("- Preparing vector records for pgvector storage")
    print("- Simulating database insertion workflow")
    print()
    
    # Step 1: Collect all text chunks
    all_chunks = []
    for doc in SAMPLE_DOCUMENTS:
        all_chunks.extend(doc["text_chunks"])
    
    print(f"📄 Processing {len(SAMPLE_DOCUMENTS)} documents with {len(all_chunks)} total text chunks")
    
    # Step 2: Generate embeddings
    embeddings, embedding_dim = generate_embeddings(all_chunks)
    
    # Step 3: Create vector records
    print(f"\n📦 Creating vector records for pgvector storage...")
    vector_records = create_vector_records(SAMPLE_DOCUMENTS, embeddings, embedding_dim)
    print(f"✅ Created {len(vector_records)} vector records")
    
    # Step 4: Simulate database insertion
    simulate_pgvector_insert(vector_records)
    
    # Step 5: Save sample records to file
    print(f"\n💾 Saving sample vector records to file...")
    
    # Save first 3 records as examples (embeddings are large)
    sample_records = []
    for record in vector_records[:3]:
        sample = record.copy()
        # Truncate embedding for display
        sample["embedding"] = sample["embedding"][:10] + ["..."] + sample["embedding"][-5:]
        sample["embedding_note"] = f"Full embedding has {embedding_dim} dimensions"
        sample_records.append(sample)
    
    output_file = "/home/ubuntu/lendlogic-v3.4/rag_embedding_result.json"
    with open(output_file, 'w') as f:
        json.dump({
            "total_records": len(vector_records),
            "embedding_dimension": embedding_dim,
            "model_used": "all-MiniLM-L6-v2",
            "sample_records": sample_records
        }, f, indent=2)
    
    print(f"✅ Sample records saved to: {output_file}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"Documents Processed: {len(SAMPLE_DOCUMENTS)}")
    print(f"Text Chunks: {len(all_chunks)}")
    print(f"Vector Records Created: {len(vector_records)}")
    print(f"Embedding Dimension: {embedding_dim}")
    print(f"Model: all-MiniLM-L6-v2")
    print()
    print("✅ Embedding generation complete")
    print("   Vectors are ready for pgvector storage in PostgreSQL")
    print()
    print("Next Steps:")
    print("1. Set up PostgreSQL with pgvector extension")
    print("2. Create the 'vectors' table using the schema in rag_pgvector.md")
    print("3. Insert these vector records into the database")
    print("4. Perform similarity searches for RAG context retrieval")

if __name__ == "__main__":
    main()
