'''# FMCSA / DOT Lookup Module

**Version:** 1.0
**Author:** The AI CEO

## Overview

This module provides instructions for a Manus agent to perform live lookups on the Federal Motor Carrier Safety Administration (FMCSA) SAFER database. It is designed to be integrated into workflows that require verification of a company's DOT (Department of Transportation) registration and safety information, which is a critical step in equipment finance underwriting for commercial vehicles.

## Logic

The agent is instructed to perform the following steps for any deal involving transportation or commercial vehicles:

1.  **Navigate** to the official FMCSA Company Snapshot page: `https://safer.fmcsa.dot.gov/CompanySnapshot.aspx`
2.  **Search** for the company using either the **Company Name** or its **DOT Number**.
3.  **Extract** the following key data points from the search results:
    *   DOT Number
    *   MC (Motor Carrier) Number
    *   Entity Type (e.g., Carrier, Broker)
    *   Operating Status (e.g., Active, Out of Service)
    *   Safety Rating (e.g., Satisfactory, Conditional)
    *   Number of Power Units / Vehicles
    *   A direct link to the snapshot page for auditing purposes.
4.  **Format** the extracted data into a clean, structured block for inclusion in a deal memo.
5.  **Handle exceptions** by providing a clear message if no record is found.

## Output Format

The extracted data should be presented in the following Markdown format:

```markdown
**DOT / SAFER Verification**
| Field | Value |
|---|---|
| Status | Active |
| DOT # | 3256789 |
| MC # | 123456 |
| Entity Type | Carrier |
| Safety Rating | Satisfactory |
| Fleet Size | 22 |
| SAFER Snapshot | [Link](URL_TO_SNAPSHOT) |
```

If no record is found, the output should be:

> *No DOT record found — confirm via manual search if transport-adjacent.*

## Permissions

To execute this logic, the Manus agent requires the following permissions:

-   `browser_mode = true`
-   `permissions = ["web_scrape"]`

## Optional Enhancements

For more advanced risk assessment, the agent can be extended to include these features:

-   **Flagging High-Risk Ratings:** Automatically flag deals where the `Safety Rating` is "Conditional" or "Unsatisfactory."
-   **Flagging Inactive Status:** Raise an alert if the `Operating Status` is anything other than "Active."
-   **Fleet Size Analysis:** Apply business rules to score risk based on fleet size (e.g., higher risk for very small or very large fleets, which may indicate different risk profiles).
'''
