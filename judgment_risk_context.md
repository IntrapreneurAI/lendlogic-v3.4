# Judgment & Risk Context Module

**Version:** 1.0  
**Author:** The AI CEO

---

## 1. Overview

This module adds a critical layer of automated judgment and contextual risk analysis to the LendLogic v3.5 workflow. After the primary business verification and enrichment are complete, this module analyzes the collected data to identify potential red flags that may not be apparent from surface-level data.

Its purpose is to move beyond simple data verification and provide actionable, context-aware insights for underwriters.

## 2. Risk Analysis Criteria

The agent must analyze each company profile for the following specific red flags:

### ⚖️ Business Age Warning

1.  **Trigger:** The company's `incorporation_date` is less than 12 months from the current date.
2.  **Action:** If triggered, add the following comment to the `judgment_risk_notes`:
    > `"Newly formed entity — proceed with caution."`

### ⚖️ Address Concerns

1.  **Trigger:** The verified address (from Google Maps or OpenCorporates) indicates a non-physical or shared location.
2.  **Detection Methods:**
    -   Check for keywords like "PO Box", "PMB", "Virtual Office".
    -   Use Google Maps place types: flag if the type is not clearly `Commercial`, `Industrial`, or `Warehouse` (e.g., if it's a known mail service provider).
    -   (Advanced) Cross-reference the address to see if multiple unrelated businesses are registered at the exact same suite number.
3.  **Action:** If triggered, add the following comment:
    > `"Non-physical or shared address may indicate operational risk."`

### ⚖️ Court or Legal Mentions

1.  **Trigger:** A search for the company or its principals returns mentions of legal issues.
2.  **Detection Methods:**
    -   **Primary:** Query connected APIs like TLO for public records, liens, judgments, or bankruptcies.
    -   **Secondary (Fallback):** Perform a structured web search using queries like `"[Company Name]" + "lawsuit"`, `"[Principal Name]" + "lien"`, or `"[Company Name]" + "bankruptcy"`.
3.  **Action:** If credible negative information is found, add the following comment:
    > `"Adverse legal or financial history found (liens, judgments, or bankruptcy mentions)."`

## 3. Integration & Output

### 3a. Supabase Storage

-   All findings must be compiled into a single text block or JSON array.
-   This data must be saved to a new `judgment_risk_notes` column in the `business_profiles` table in Supabase.

### 3b. AI Underwriting Report

-   A new section titled **"Judgment & Risk Context"** must be added to the final AI-generated underwriting report.
-   This section will list all the flagged comments from the analysis.

### 3c. Risk Weighting

-   The overall deal risk score should be adjusted upwards if any of these contextual flags are triggered.
-   The internal Stack Rank should reflect this increased risk, potentially moving a deal from `Good 👌` to `Borderline 🛂`.

### 3d. Dashboard & UI Integration

-   The flagged notes must be clearly visible in the Netlify dashboard.
-   Use color-coding (e.g., a red icon or highlight) to draw attention to deals with contextual risk flags.
-   The notes should also be synced to the corresponding Notion deal page.

## 4. Supabase Schema Update

The `business_profiles` table needs to be updated to include the new column.

```sql
ALTER TABLE business_profiles
ADD COLUMN judgment_risk_notes JSONB;
```

This allows for storing structured notes, such as:

```json
{
  "business_age_warning": "Newly formed entity — proceed with caution.",
  "address_concerns": "Non-physical or shared address may indicate operational risk.",
  "legal_mentions": null
}
```

---

## 5. Agentic Flow

This module should run immediately after the "Business Verification & Review Enrichment" step and before the final "Scoring & Classification" step. The agent should announce its action:

> `"Now, I will analyze the verified data for deeper contextual risks..."`

If any risks are found, they should be announced clearly:

> `"⚠️ I've identified some contextual risks: the business is less than 12 months old and the registered address appears to be a virtual office."`
