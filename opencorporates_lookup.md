
# OpenCorporates Business Lookup Module

**Version:** 1.0
**Author:** The AI CEO

---

## 1. Overview

This module provides real-time business verification and data enrichment for the LendLogic v3.4 agent. It uses the OpenCorporates API as the primary source and includes a multi-tier fallback system to ensure maximum data coverage. All results are logged to a Supabase database for traceability and analysis.

## 2. Workflow

The lookup process follows a sequential, multi-step approach for each company in a deal (borrower and vendor).

### Step 1: Primary Lookup (OpenCorporates)

1.  **Action:** For each company, perform a live API call to the OpenCorporates database using the company name and jurisdiction (if available).
2.  **API Key:** The agent must use a secure `OPENCORPORATES_API_KEY` from environment variables.
3.  **Data to Collect:**
    -   Incorporation Date
    -   Jurisdiction & Registration Number
    -   Officer Names (Directors, Principals)
    -   Company Status (Active, Dissolved, Inactive)
    -   Registered Address

### Step 2: Supabase Integration

1.  **Action:** Upon receiving a successful result from OpenCorporates, write the data to the `business_profiles` table in Supabase.
2.  **Logic (Upsert):**
    -   Use `company_name` as the primary lookup key.
    -   If a record for that company already exists, **update** it with the new data.
    -   If no record exists, **insert** a new row.
3.  **Traceability:** Set the `source` field to `"OpenCorporates"`.

### Step 3: Multi-Tier Fallback Logic

If the OpenCorporates API returns no match, an error, or an incomplete record, the agent must trigger the following fallbacks in order.

#### 🔄 Fallback #1: Structured Web Search

1.  **Action:** Perform a structured web search (e.g., Google, Bing) using queries like `"[Company Name] official website"` or `"[Company Name] incorporation details [State]"`.
2.  **Goal:** Find the company’s official website or a state business registry page.
3.  **On Success:** If found, parse the page for the required data. Set the `fallback_source` field in Supabase to `"Web Search - [google.com/bing.com]"`.

#### 🔄 Fallback #2: Third-Party Data APIs

1.  **Action:** If the web search fails, query other connected data provider APIs.
2.  **Potential Sources:** TLO, BBB (Better Business Bureau), Trustpilot.
3.  **On Success:** If a match is found, extract the relevant data and set the `fallback_source` to the name of the API used (e.g., `"BBB API"`).

#### 🔄 Fallback #3: Manual Review Flag

1.  **Action:** If all automated lookups fail, mark the company for manual review.
2.  **Supabase Entry:**
    -   Set the `company_status` to `"Unverified"`.
    -   Set the `fallback_source` to `"Manual Review Required"`.
    -   Flag this in the final underwriting summary.

## 4. Company Review Enrichment

For every company (whether matched via OpenCorporates or fallback), the agent must generate and store review and social media links to enable further due diligence.

### Google Reviews Link

1.  **Generate URL:** Create a Google Search link formatted as:
    ```
    https://www.google.com/search?q=[company name] [city] reviews
    ```
2.  **Example:** For "Midwest Freight Solutions" in "Chicago":
    ```
    https://www.google.com/search?q=Midwest+Freight+Solutions+Chicago+reviews
    ```
3.  **Store in Supabase:** Save this link in the `google_review_link` column.

### LinkedIn Company Search Link

1.  **Generate URL:** Create a LinkedIn search link formatted as:
    ```
    https://www.linkedin.com/search/results/companies/?keywords=[company name]
    ```
2.  **Example:** For "Midwest Freight Solutions":
    ```
    https://www.linkedin.com/search/results/companies/?keywords=Midwest+Freight+Solutions
    ```
3.  **Store in Supabase:** Save this link in the `linkedin_search_link` column.

### Integration Points

These links must be included in:
-   AI underwriting summaries
-   Notion deal notes
-   Netlify dashboard views
-   Final Deal Memo outputs

## 5. Risk Handling

The agent must automatically flag deals for higher risk if the lookup reveals any of the following:

-   **Company Status:** Anything other than `"Active"` (e.g., `"Dissolved"`, `"Inactive"`).
-   **Missing Incorporation Date:** The `incorporation_date` field is null.
-   **No Officers Listed:** The `officers` array is empty.

These flags should be prominently displayed in the internal-facing Stack Rank.

## 6. Supabase Schema

A `business_profiles` table is required to store the enriched data.

```sql
CREATE TABLE business_profiles (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  company_name TEXT UNIQUE NOT NULL,
  incorporation_date DATE,
  jurisdiction TEXT,
  registration_number TEXT,
  company_status TEXT,
  officers JSONB,
  source TEXT, -- e.g., 'OpenCorporates'
  fallback_source TEXT, -- e.g., 'Web Search - google.com'
  google_review_link TEXT, -- Google search link for reviews
  linkedin_search_link TEXT, -- LinkedIn company search link
  risk_flags JSONB,
  last_updated_at TIMESTAMPTZ DEFAULT now(),
  created_at TIMESTAMPTZ DEFAULT now()
);
```

## 7. Important Notes

-   **Live Execution:** This entire process must run in real-time during the underwriting session.
-   **Clear Labeling:** All fallback sources must be clearly labeled in the Supabase record.
-   **Notifications:** The agent must notify the user if a fallback is triggered or if data remains incomplete after all steps.
