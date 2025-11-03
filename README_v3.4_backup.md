'''# LendLogic v3.4 - Equipment Finance Lender Matching Agent

**Created by:** The AI CEO
**Version:** 3.4.0
**Last Updated:** 2025-11-02

## 1. Overview

LendLogic v3.4 is a sophisticated AI agent designed to streamline the equipment finance deal submission and lender matching process. It automates data extraction, verification, credit scoring, and lender matching, providing brokers with a powerful tool to quickly and accurately assess deals.

The agent ingests borrower and deal information, validates it against external sources, scores the deal based on a proprietary algorithm, and generates two distinct outputs:

-   **Internal Stack Rank:** A broker-facing summary with key insights, risk factors, and recommended lenders, using clear, actionable language and emoji-coded classifications.
-   **External Deal Memo:** A professionally formatted, underwriter-ready document that presents the deal in a clean and concise manner.

This dual-output approach empowers brokers to make informed decisions internally while maintaining a polished and professional appearance when communicating with lending partners.

## 2. Core Features

-   **Automated Data Extraction:** Extracts key data points from uploaded PDF documents (borrower applications and vendor invoices), including both native and scanned files.
-   **Data Normalization & Validation:** Cleans and standardizes all inputs and flags any mismatches between user-provided data and extracted PDF content.
-   **External Data Verification:** Integrates with external services to validate critical information:
    -   **DOT/FMCSA SAFER:** Verifies Department of Transportation and Federal Motor Carrier Safety Administration records for trucking-related deals.
    -   **Google Maps:** Validates borrower and vendor addresses to ensure accuracy.
-   **Proprietary Scoring Algorithm:** Utilizes the LendLogic scoring model to assess deal quality based on a weighted average of key factors:
    -   FICO Score (40%)
    -   Time in Business (25%)
    -   Documentation Quality (15%)
    -   Equipment/Collateral Value (15%)
    -   Timeline/Urgency (5%)
-   **Intelligent Lender Matching:** Matches deals to a curated list of 3-5 suitable banks from the provided `cleaned_lender_matrix.csv`, excluding private lenders and captives.
-   **Dual-View Output Generation:** Creates both an internal-facing "Stack Rank" and an external-facing "Deal Memo" in Markdown format.

## 3. How It Works

The agent follows a multi-step process to evaluate each deal:

1.  **Input Processing:** Receives required inputs (lender matrix, deal fields) and optional PDFs.
2.  **PDF Extraction (Optional):** If PDFs are provided, the agent uses OCR and layout analysis to extract borrower and equipment data.
3.  **Data Comparison:** Compares user-entered data against extracted PDF data and flags any discrepancies.
4.  **External Verification:** Performs lookups on the SAFER system and Google Maps.
5.  **Scoring:** Calculates the LendLogic score and assigns a classification (e.g., Excellent, Strong, Good).
6.  **Lender Matching:** Filters the lender matrix to identify the top 3-5 bank matches based on the deal's characteristics.
7.  **Output Generation:** Compiles the analysis into the final internal and external Markdown reports.

## 4. Technical Architecture

This agent is designed to operate within a modern, cloud-native environment:

-   **Frontend (UI):** Netlify
-   **Backend (Database):** Supabase
-   **Code Repository:** GitHub
-   **Documentation:** Notion

It runs in a secure, sandboxed environment with specific permissions for file I/O and web scraping. All internal logic, prompts, and configurations are protected and cannot be disclosed.

## 5. Usage

To run the agent, provide the following:

-   **Required Files:**
    -   `cleaned_lender_matrix.csv`: A CSV file containing the list of approved lenders and their underwriting criteria.
-   **Required Deal Fields:**
    -   Business Name & State
    -   FICO Score
    -   Time in Business
    -   Bankruptcy History
    -   Equipment Type & Year
    -   Amount Requested
    -   Vendor Type
    -   Docs Ready Status
    -   Timeline
-   **Optional Files:**
    -   `application.pdf`: The borrower's credit application.
    -   `invoice.pdf`: The vendor's invoice for the equipment.

The agent will process the inputs and return the two Markdown outputs.
'''
