'''# Google Maps API Address Validation Module

**Version:** 1.0
**Author:** The AI CEO

## 1. Overview

This module provides instructions for a Manus agent to validate borrower and vendor addresses using the Google Maps Geocoding API. Accurate address verification is a crucial step in due diligence for equipment finance, helping to confirm the physical presence of a business and assess location-based risk.

## 2. Logic

The agent is instructed to perform the following steps for both the borrower and the vendor:

1.  **Construct Query:** Use the business name along with the city and state to form a search query.
2.  **API Call:** If a `GOOGLE_MAPS_API_KEY` is securely available as an environment variable, make a call to the Google Maps Geocoding API.
3.  **Data Extraction:** From the API response, extract the following information:
    *   Standardized, formatted address.
    *   Latitude and longitude coordinates.
    *   Location type (e.g., `ROOFTOP`, `RANGE_INTERPOLATED`).
    *   A clickable Google Maps link generated from the coordinates.
4.  **Confidence Scoring:** Assess the quality of the result. A `ROOFTOP` result indicates a precise, high-confidence match (100%). Other results (e.g., `GEOMETRIC_CENTER`) imply a less precise match and should be scored accordingly (e.g., 85%).
5.  **Format Output:** Present the extracted data in a clean, structured Markdown format.
6.  **Handle Failures:** If the address cannot be confidently validated or the API call fails, return a clear "Unverified" status.

## 3. API Key Security

The agent MUST use the API key securely from environment variables. The key itself MUST NOT be exposed in logs, prompts, or final outputs.

## 4. Output Format

The validation results should be presented in the following Markdown format:

```markdown
**Google Maps Validation**

**Borrower:** [Business Name – City, State](Google Maps Link)
- **Match Score:** 95%
- **Type:** Commercial
- **Lat/Long:** 41.8781° N, 87.6298° W

**Vendor:** [Vendor Name – City, State](Google Maps Link)
- **Match Score:** 100%
- **Type:** Industrial
- **Lat/Long:** 41.5834° N, 87.4967° W
```

If an address cannot be verified, the output for that entity should be:

> **[Borrower/Vendor]:** Unverified — confirm manually.

## 5. Permissions

To execute this logic, the Manus agent requires:

-   Access to environment variables to read the `GOOGLE_MAPS_API_KEY`.
-   `web_scrape` or equivalent permission to make external API calls.
'''
