# RAG & pgvector Integration Module

**Version:** 1.0  
**Author:** The AI CEO

---

## 1. Overview

This module integrates Retrieval-Augmented Generation (RAG) into the LendLogic v3.5 workflow using PostgreSQL with the `pgvector` extension. It enables the system to perform semantic searches over a corpus of financial documents, policies, and historical data, providing deep contextual insights to the AI reasoning layer during the underwriting process.

This approach keeps structured data and vector embeddings within a single, ACID-compliant database, ensuring data integrity, security, and simplified management.

## 2. Vector Embedding Workflow

The core of the RAG system is the generation and storage of vector embeddings from various text sources.

### 2a. Text Sources for Embedding

Embeddings should be generated from the following sources:

-   **Financial Document Text:** Raw text extracted from financial statements, contracts, and applications via the OCR or PDF Extraction modules.
-   **Lending Policy Documents:** The full text of internal credit policies, underwriting guidelines, and compliance manuals.
-   **Analyst Notes & Decisions:** Historical commentary, risk assessments, and decision rationale from past deals.
-   **Risk Summaries:** Text from the "Judgment & Risk Context" and "Document Risk Review" sections.

### 2b. Embedding Generation

1.  **Chunking:** Before embedding, large documents must be split into smaller, semantically coherent chunks (e.g., paragraphs or sections of 100-250 tokens).
2.  **Embedding Model:** Use a high-quality sentence-transformer model (e.g., `all-MiniLM-L6-v2`, `text-embedding-ada-002`) to convert text chunks into dense vector embeddings.
3.  **De-identification:** Ensure no Personally Identifiable Information (PII) such as names, addresses, or SSNs are included in the text chunks before embedding.

### 2c. PostgreSQL `pgvector` Storage

Embeddings are stored in a dedicated `vectors` table within the PostgreSQL database.

**Table Schema:**

```sql
-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the table to store embeddings
CREATE TABLE vectors (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  deal_id UUID REFERENCES deals(id), -- Link to the specific deal
  company_id UUID REFERENCES business_profiles(id), -- Link to the company
  document_id UUID REFERENCES documents(id), -- Link to the source document
  
  embedding VECTOR(384), -- Or 1536 for text-embedding-ada-002
  source_text TEXT NOT NULL, -- The original text chunk
  
  document_type TEXT, -- e.g., 'Financial Statement', 'Lending Policy', 'Analyst Note'
  source_file TEXT, -- The name of the source file
  tags TEXT[], -- e.g., {'cash_flow', 'risk', 'legal', 'policy_section_3.2'}
  
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Create an IVFFlat index for fast approximate nearest neighbor search
CREATE INDEX ON vectors USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
```

## 3. RAG Query & Context Retrieval

When the AI agent requires context to make a decision, it performs a similarity search against the `vectors` table.

### 3a. Query Process

1.  **Formulate a Query:** The agent generates a query based on the current task (e.g., "assessing cash flow risk for a transportation company," "lending guidelines for sub-680 FICO scores").
2.  **Generate Query Embedding:** The query text is converted into a vector embedding using the same model as the stored documents.
3.  **Perform Similarity Search:** Use `pgvector` to find the top-k (e.g., top 3-5) most relevant text chunks from the `vectors` table using cosine similarity (or L2 distance).

**Example SQL Query:**

```sql
-- Find the 5 most relevant text chunks related to the query
SELECT
  source_text,
  document_type,
  source_file,
  1 - (embedding <=> :query_embedding) AS similarity_score
FROM
  vectors
ORDER BY
  embedding <=> :query_embedding
LIMIT 5;
```
*Note: `<=>` is the L2 distance operator. For cosine similarity, use `<=>` on normalized vectors or the `<#>` operator.* 

### 3b. Context Integration

-   **Feed to AI Layer:** The retrieved `source_text` snippets are compiled and fed into the prompt of the Large Language Model (LLM) as context.
-   **AI-Generated Output:** The LLM uses this context to generate more accurate, transparent, and defensible summaries, risk notes, and decisions.
-   **Traceability:** The final output includes a section titled **"Based on Retrieved Context"** that lists the source snippets used, providing a clear audit trail.

## 4. Error Handling & Guardrails

-   **No Match Found:** If the similarity search returns no results with a score above a certain threshold (e.g., 0.75), the agent should proceed without the augmented context and log `rag_context_status = "not_found"`.
-   **Vector Hygiene:** Implement a process to delete or archive vector entries associated with a deal or company when that entity is deleted from the system to prevent outdated information from being retrieved.
-   **Security:** As embeddings can potentially be reverse-engineered, do not embed text containing direct PII. Focus on semantic meaning, financial terms, and de-identified case data.

## 5. Agentic Flow Integration

RAG is not a single step but a continuous capability available throughout the workflow.

1.  **Embedding (Post-Processing):**
    -   After **Step 2 (Document Processing)**, announce: `"Generating and storing vector embeddings for all extracted text to enhance contextual understanding..."`

2.  **Retrieval (As Needed):**
    -   During **Step 4 (Judgment & Risk Context)**, announce: `"Searching for relevant historical data and policy guidelines to inform risk assessment..."`
    -   During **Step 6 (Scoring & Matching)**, announce: `"Retrieving context to support the final lending decision and summary..."`

3.  **Output:**
    -   When context is used, the AI summary will include the **"Based on Retrieved Context"** section.
    -   The final Supabase record for the deal summary will include `rag_context_used` (the retrieved snippets) and `rag_context_status`.

---

By integrating RAG with `pgvector`, LendLogic gains a powerful, secure, and governable long-term memory, enabling it to make smarter, data-driven decisions that improve over time as more knowledge is added to the vector database.
