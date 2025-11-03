# LendLogic v3.5 - Final Integration Guide

**Version:** 3.5.0  
**Date:** November 3, 2025  
**Author:** The AI CEO

---

## Overview

LendLogic v3.5 is a complete, real-time due diligence agent for equipment finance underwriting. It combines business verification, review enrichment, address validation, DOT/FMCSA checks, and lender matching into a single, conversational agentic workflow.

This guide provides a comprehensive overview of the system architecture, data flow, and integration points.

---

## System Architecture

### Core Components

1.  **OpenCorporates Business Lookup** - Primary business verification with multi-tier fallback
2.  **Google Maps Address Validation** - Geocoding and location type verification
3.  **FMCSA/DOT Verification** - Transportation company safety and compliance checks
4.  **Review Enrichment** - Google Reviews and LinkedIn search links
5.  **LendLogic Scoring Engine** - Deal classification and risk assessment
6.  **Lender Matching** - Bank recommendation based on credit windows

### Data Storage

-   **Supabase Tables:**
    -   `business_profiles` - Enriched company data with review links
    -   `deals` - Deal submissions with verification results
    -   `fmcsa_verifications` - DOT/SAFER check results
    -   `google_maps_validations` - Address verification results

---

## Workflow Sequence

### Phase 1: Intake & Normalization

1.  User submits deal via Netlify UI
2.  Agent acknowledges receipt and confirms inputs
3.  Data is normalized (trim whitespace, standardize capitalization)

### Phase 2: Document Processing & OCR Risk Review

-   **Run Tesseract OCR:** Extract raw text from all uploaded documents (PDF, PNG, JPG, TIFF).
-   **Perform Risk Review:** Scan for missing fields, adverse financial language, legal issues, and alterations.
-   **Log to Supabase:** Store OCR text, metadata, and risk findings in the `documents` table.

### Phase 3: Business Verification & Enrichment

#### Step 2a: OpenCorporates Lookup

-   **API Call:** `https://api.opencorporates.com/v0.4/companies/search?q={company_name}&jurisdiction_code={state}`
-   **Data Extracted:**
    -   Incorporation Date
    -   Jurisdiction & Registration Number
    -   Company Status
    -   Officer Names & Roles

#### Step 2b: Fallback Logic

If OpenCorporates fails:

1.  **Fallback #1:** Structured web search via Google
2.  **Fallback #2:** Third-party APIs (TLO, BBB, Trustpilot)
3.  **Fallback #3:** Mark as "Unverified" and flag for manual review

#### Step 2c: Review Enrichment

Generate and store:

-   **Google Reviews Link:** `https://www.google.com/search?q={company}+{city}+reviews`
-   **LinkedIn Search Link:** `https://www.linkedin.com/search/results/companies/?keywords={company}`

#### Step 2d: Supabase Upsert

```sql
INSERT INTO business_profiles (
  company_name,
  incorporation_date,
  jurisdiction,
  registration_number,
  company_status,
  officers,
  source,
  fallback_source,
  google_review_link,
  linkedin_search_link,
  risk_flags
) VALUES (...)
ON CONFLICT (company_name) 
DO UPDATE SET ...;
```



-   **Analyze Data:** Check for business age warnings, address concerns, and legal mentions.
-   **Announce Findings:** Report any identified contextual risks.
-   **Log to Supabase:** Save notes to the `judgment_risk_notes` column.

### Phase 5: Additional Verifications

-   **Google Maps:** Geocode addresses, validate location types
-   **FMCSA/DOT:** Check transportation company safety ratings



-   **Analyze Data:** Check for business age warnings, address concerns, and legal mentions.
-   **Announce Findings:** Report any identified contextual risks.
-   **Log to Supabase:** Save notes to the `judgment_risk_notes` column.

### Phase 6: Scoring & Matching

-   **LendLogic Algorithm:**
    -   FICO: 40%
    -   Time in Business: 25%
    -   Docs Ready: 15%
    -   Equipment/Collateral: 15%
    -   Timeline/Urgency: 5%
-   **Classification:**
    -   90-100: Excellent 💪
    -   75-89: Strong 🦾
    -   60-74: Good 👌
    -   50-59: Borderline 🛂
    -   <50: Poor 👎

### Phase 5: Output Generation

-   **Internal Stack Rank** (emoji-coded, tactical)
-   **External Deal Memo** (professional, underwriter-ready)

---

## Integration Points

### 1. Netlify Dashboard

-   Display enriched company profiles
-   Show Google Reviews and LinkedIn links
-   Visualize risk flags (🔴/🟡/🟢)

### 2. Notion Deal Notes

-   Auto-populate deal pages with verification results
-   Embed clickable review links
-   Track fallback sources and risk flags

### 3. GitHub Reports

-   Store deal memos as Markdown files
-   Version control for audit trails

### 4. Supabase Database

-   Central source of truth for all verification data
-   Enables analytics and reporting across deals

---

## Risk Flagging System

### Document Risk Flags

-   📄 **Missing Fields:** Signature, date, or amount missing
-   📄 **Adverse Financials:** Delinquency, overdue, lien, etc.
-   📄 **Legal Issues:** Bankruptcy, judgment, lawsuit, etc.
-   📄 **Alterations:** Corrected copy, duplicate entries, etc.

### Contextual Risk Flags

-   ⚖️ **Business Age Warning:** Incorporated < 12 months ago
-   ⚖️ **Address Concerns:** PO Box, virtual office, or shared address
-   ⚖️ **Legal Mentions:** Liens, judgments, or bankruptcies found

### High-Risk Indicators

-   ⚠️ Company status is not "Active"
-   ⚠️ Missing incorporation date
-   ⚠️ No officers listed
-   ⚠️ Fallback used with inconclusive data
-   ⚠️ FMCSA status is "Inactive" or "Out of Service"
-   ⚠️ Safety rating is "Conditional" or "Unsatisfactory"

### Visual Indicators

-   🔴 **High Risk** - 2+ flags
-   🟡 **Medium Risk** - 1 flag
-   🟢 **Low Risk** - 0 flags

---

## API Requirements

### Required API Keys

-   `OPENCORPORATES_API_KEY` - Business verification
-   `GOOGLE_MAPS_API_KEY` - Address geocoding
-   `SUPABASE_URL` + `SUPABASE_KEY` - Database access

### Optional API Keys

-   `TLO_API_KEY` - Fallback business data
-   `BBB_API_KEY` - Better Business Bureau data
-   `TRUSTPILOT_API_KEY` - Review data

---

## Sample Output

### Enriched Business Profile (Supabase)

```json
{
  "company_name": "Midwest Freight Solutions LLC",
  "incorporation_date": "2020-03-15",
  "jurisdiction": "us_il",
  "registration_number": "LLC-2020-12345",
  "company_status": "Active",
  "officers": [
    {"name": "John Smith", "role": "Managing Member"},
    {"name": "Sarah Johnson", "role": "Member"}
  ],
  "source": "OpenCorporates",
  "fallback_source": null,
  "google_review_link": "https://www.google.com/search?q=Midwest+Freight+Solutions+LLC+Chicago+reviews",
  "linkedin_search_link": "https://www.linkedin.com/search/results/companies/?keywords=Midwest+Freight+Solutions+LLC",
  "risk_flags": [],
  "entity_type": "Borrower",
  "deal_id": "DEAL-2025-001",
  "last_updated_at": "2025-11-03T04:56:39Z"
}
```

### Deal Memo Excerpt

```markdown
## Business Verification

**Borrower: Midwest Freight Solutions LLC**

| Field | Value |
|---|---|
| Status | Active ✅ |
| Incorporation Date | March 15, 2020 |
| Jurisdiction | Illinois (us_il) |
| Registration # | LLC-2020-12345 |
| Officers | John Smith (Managing Member), Sarah Johnson (Member) |

**Due Diligence Links:**
- 🔍 [Google Reviews](https://www.google.com/search?q=Midwest+Freight+Solutions+LLC+Chicago+reviews)
- 💼 [LinkedIn](https://www.linkedin.com/search/results/companies/?keywords=Midwest+Freight+Solutions+LLC)

**Risk Assessment:** 🟢 Low Risk - No flags detected
```

---

## Deployment Checklist

- [ ] Set up Supabase tables with correct schema
- [ ] Configure API keys in environment variables
- [ ] Deploy Netlify UI with dashboard components
- [ ] Connect Notion workspace for deal notes
- [ ] Set up GitHub repository for deal memos
- [ ] Test all fallback mechanisms
- [ ] Verify Supabase upsert logic
- [ ] Confirm review link generation
- [ ] Test end-to-end workflow with sample deals

---

## Support & Maintenance

-   **Documentation:** All modules documented in repository
-   **Demo Scripts:** Working examples for each verification module
-   **Test Data:** Sample deals and lender matrix included
-   **Version Control:** Full Git history on GitHub

**Repository:** https://github.com/IntrapreneurAI/lendlogic-v3.4

---

**End of Integration Guide**
