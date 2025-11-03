# PDF Financial Statement Extraction Module (Non-OCR)

**Version:** 1.0  
**Author:** The AI CEO

---

## 1. Overview

This module provides functionality to extract structured text and tables from native (machine-readable) PDF financial statements. It is designed to work in tandem with the Tesseract OCR module, handling documents that do not require OCR. The primary goal is to parse balance sheets, income statements, and cash flow statements into a structured format for analysis.

## 2. Core Extraction Task

When a PDF file is identified as containing embedded, selectable text (i.e., it is not a scanned image), the agent must use a non-OCR PDF parsing library to perform the extraction.

### 2a. Recommended Libraries

-   **`pdfplumber`**: Excellent for table extraction and text flow analysis. (Primary recommendation)
-   **`PyPDF2`** or **`pdfminer.six`**: Good for raw text extraction, but less robust for tables.

### 2b. Extraction Requirements

1.  **Full Text Extraction:**
    -   Extract all text from the document, preserving the general layout and page breaks.
    -   Pay special attention to financial notes, appendices, and management discussion sections.

2.  **Table-Aware Parsing:**
    -   Identify and extract all tabular data from the PDF.
    -   The extraction must maintain the row and column structure of the original table.
    -   Numeric formatting (e.g., currency symbols, commas, negative signs in parentheses) should be preserved or normalized.

### 2c. Data Output & Normalization

-   **Output Format:** Extracted tables should be normalized into a structured JSON format. Each table should be an object containing a list of rows, where each row is a list of cell values.
-   **Table Labeling:** The agent should attempt to identify and label each table based on surrounding text (e.g., "Consolidated Balance Sheet", "Statement of Income", "Cash Flow Statement").

## 3. Post-Extraction Usage & Supabase Integration

### 3a. Supabase Storage

Store the parsed data in the `documents` table (or a dedicated `financial_statements` table) with the following fields:

-   `pdf_text_raw`: The full, unstructured text extracted from the PDF.
-   `financial_tables_json`: A JSONB column containing the array of structured tables extracted from the document.

**Example `financial_tables_json` Structure:**

```json
[
  {
    "table_name": "Consolidated Balance Sheet",
    "page_number": 2,
    "data": [
      ["Assets", "2023", "2022"],
      ["Current Assets", "", ""],
      ["Cash and cash equivalents", "$1,250,000", "$980,000"],
      ["Accounts receivable", "$850,000", "$720,000"],
      ["Total Current Assets", "$2,100,000", "$1,700,000"]
    ]
  },
  {
    "table_name": "Statement of Income",
    "page_number": 3,
    "data": [
      ["Revenue", "$5,500,000"],
      ["Cost of Goods Sold", "($3,200,000)"],
      ["Gross Profit", "$2,300,000"]
    ]
  }
]
```

### 3b. Analytical Usage

The extracted structured data should be used to:

1.  **Feed Underwriting Metrics:** Automatically calculate key financial ratios (e.g., Debt-to-Equity, Current Ratio) from the parsed tables.
2.  **Power AI Summaries:** Enable the AI to generate narrative summaries of the company's financial health based on the extracted numbers.
3.  **Detect Inconsistencies:** Programmatically check for issues like:
    -   Balance sheet imbalances (Assets ≠ Liabilities + Equity).
    -   Sustained negative cash flow.
    -   Significant unexplained variances year-over-year.

## 4. Error Handling

If the PDF is encrypted, corrupted, or if table extraction fails to produce structured data:

1.  **Log the Failure:** Set `pdf_extraction_status = "failed"` in the Supabase record.
2.  **Create a Warning:** Add a flag to the underwriting summary: `"Automated table extraction failed for [filename]. The document may be unstructured or password-protected."`
3.  **Fallback to OCR:** As a fallback, the agent can attempt to process the document using the Tesseract OCR module, in case the failure was due to an unusual PDF format rather than a true text layer.
4.  **Manual Review:** If both methods fail, flag the document for manual review.

## 5. Agentic Flow Integration

This module should be part of the initial document processing step, working alongside the OCR module.

1.  **Document Triage:** Before processing, the agent should first determine if a PDF is native or scanned.
    -   **Test:** Attempt to extract a small amount of text using `pdfplumber`. If successful, the PDF is native.
    -   **Decision:** If native, use this PDF Extraction module. If not, or if it fails, use the Tesseract OCR module.

2.  **Announce Action:**
    > `"Processing native PDF: [filename]. Extracting text and financial tables..."`

3.  **Summarize Findings:**
    > `"PDF processing complete for [filename]. I successfully extracted [X] tables, including a Balance Sheet and Income Statement. The data is now ready for analysis."`

4.  **Handle Failures:**
    > `"⚠️ Automated table extraction failed for [filename]. Attempting OCR as a fallback..."`

---

This dual-path approach (native PDF extraction + OCR) ensures that LendLogic can handle the widest possible range of document types, maximizing automation and data capture.
