# Tesseract OCR Document Processing Module

**Version:** 1.0  
**Author:** The AI CEO

---

## 1. Overview

This module integrates Tesseract OCR (Optical Character Recognition) into the LendLogic v3.5 workflow to automate the extraction and analysis of text from uploaded financial documents. It is designed to handle a variety of document types, including scanned contracts, tax forms, bank statements, and identification, providing both raw text extraction and automated risk review.

## 2. Core OCR Task

For every document file provided with a deal submission, the agent must perform the following steps.

### 2a. Text Extraction

1.  **Engine:** Use the Tesseract OCR engine.
2.  **Supported Formats:** The system must be able to process standard image and document formats, including `PDF`, `PNG`, `JPG`, `JPEG`, and `TIFF`.
3.  **Multi-Language Support:** Enable Tesseract's multi-language capabilities (e.g., `eng+spa`) to handle documents that may contain languages other than English.

### 2b. Data Output & Storage

For each processed document, save the following outputs to Supabase or include them in the final JSON result:

-   `ocr_text_raw`: The full, unstructured text output from Tesseract.
-   `ocr_metadata`: A JSON object containing:
    -   `document_name`: The original filename.
    -   `detected_language`: The language(s) detected (e.g., "eng").
    -   `ocr_confidence_score`: The average confidence score of the OCR extraction (0-100).
    -   `page_count`: The number of pages processed.

## 3. Post-OCR Risk Review

After raw text extraction, the agent must perform an automated risk review by scanning the `ocr_text_raw` for potential red flags.

### 3a. Risk Detection Criteria

1.  **Missing Required Fields:**
    -   **Trigger:** Scan for keywords that imply missing information.
    -   **Keywords:** "Signature: ________", "Date: ", "Amount: ", "N/A", "Not Provided".
    -   **Comment:** `"Document may be missing required fields (e.g., signature, date, amount)."`

2.  **Value Mismatches:**
    -   **Trigger:** Compare key values across different sections of the document (e.g., total amount on page 1 vs. summary on page 3).
    -   **Action:** If a discrepancy is found, flag it.
    -   **Comment:** `"Inconsistent values detected across the document."`

3.  **Adverse Financial Mentions:**
    -   **Trigger:** Scan for keywords indicating financial distress.
    -   **Keywords:** "Delinquency", "Unpaid Taxes", "Overdue", "Past Due", "Collection Notice", "Lien".
    -   **Comment:** `"Adverse financial language detected (e.g., delinquency, overdue balances)."`

4.  **Legal Red Flags:**
    -   **Trigger:** Scan for keywords indicating legal issues.
    -   **Keywords:** "Bankruptcy", "Court Order", "Judgment", "Lawsuit", "Regulatory Action".
    -   **Comment:** `"Potential legal issues mentioned (e.g., bankruptcy, court orders)."`

5.  **Potential Alterations:**
    -   **Trigger:** Look for signs of document tampering.
    -   **Keywords:** "Corrected Copy", "Amended", duplicate serial numbers, inconsistent fonts (requires advanced analysis).
    -   **Comment:** `"Potential document alteration detected (e.g., duplicate entries, corrected copy markers)."`

### 3b. Output & Integration

-   **Report Section:** Summarize all findings in a new section titled **"Document Risk Review"** in the main AI-generated underwriting report.
-   **Supabase Logging:** Append the findings to the `judgment_risk_notes` JSONB column in the `business_profiles` table, keyed by document name.

## 4. Error Handling

If the OCR process fails for a specific document:

1.  **Log the Failure:** Set `ocr_status = "failed"` in the Supabase record for that document.
2.  **Create a Warning:** Add a flag to the underwriting summary: `"OCR failed for document [filename] due to low image quality or unreadable format."`
3.  **Notify for Manual Review:** Alert the user that the document requires manual inspection.

## 5. Supabase Schema Updates

### `documents` Table (New or Existing)

A table to track each uploaded document is recommended.

```sql
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  deal_id UUID REFERENCES deals(id),
  file_name TEXT NOT NULL,
  ocr_status TEXT, -- e.g., 'success', 'failed'
  ocr_text_raw TEXT,
  ocr_metadata JSONB, -- {language, confidence, page_count}
  document_risk_review JSONB, -- {missing_fields, mismatches, legal_flags}
  created_at TIMESTAMPTZ DEFAULT now()
);
```

### `business_profiles` Table Update

The `judgment_risk_notes` column can be updated to include a key for document-related risks.

```json
{
  "business_age_warning": null,
  "address_concerns": null,
  "legal_mentions": null,
  "document_risks": {
    "invoice.pdf": "Adverse financial language detected (e.g., delinquency, overdue balances).",
    "application.pdf": "Document may be missing required fields (e.g., signature, date, amount)."
  }
}
```

---

## 6. Agentic Flow

This module should be integrated into the main workflow, typically after the initial intake.

1.  **Announce Action:**
    > `"I will now process the uploaded documents using OCR to extract and analyze the text..."`

2.  **Process Each Document:** Run the OCR and risk review pipeline for every file.

3.  **Summarize Findings:**
    > `"OCR processing is complete. I analyzed [X] documents. [Y] documents were flagged for potential risks. See the 'Document Risk Review' section for details."`

4.  **Handle Failures:**
    > `"⚠️ OCR failed for 'document.pdf'. This file may be corrupted or have very low quality and requires manual review."`

---

This structured approach ensures that all documents are not only digitized but also automatically reviewed for critical risk factors, significantly enhancing the speed and quality of the underwriting process.
