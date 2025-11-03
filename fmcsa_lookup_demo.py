#!/usr/bin/env python3.11
"""
FMCSA/DOT Lookup Demo for LendLogic v3.4
Validates DOT registration and safety status for transportation businesses
"""

import json
from datetime import datetime

# Sample borrower data from test deal
BORROWER_NAME = "Midwest Freight Solutions LLC"
DOT_NUMBER = "1234567"
DEAL_ID = "DEAL-2025-001"

def simulate_fmcsa_lookup(company_name, dot_number=None):
    """
    Simulate FMCSA SAFER database lookup.
    In production, this would use browser automation to visit:
    https://safer.fmcsa.dot.gov/CompanySnapshot.aspx
    """
    
    print(f"🔍 Checking DOT status with the FMCSA for: {company_name}")
    print(f"   Searching by DOT Number: {dot_number if dot_number else 'Not provided'}")
    print()
    
    # Simulate different scenarios
    scenarios = {
        "active_good": {
            "found": True,
            "dot_number": dot_number or "1234567",
            "mc_number": "456789",
            "entity_type": "Carrier",
            "operating_status": "Active",
            "safety_rating": "Satisfactory",
            "fleet_size": 22,
            "snapshot_url": f"https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY&query_type=queryCarrierSnapshot&query_param=USDOT&query_string={dot_number or '1234567'}",
            "risk_flags": []
        },
        "active_conditional": {
            "found": True,
            "dot_number": dot_number or "2345678",
            "mc_number": "567890",
            "entity_type": "Carrier",
            "operating_status": "Active",
            "safety_rating": "Conditional",
            "fleet_size": 8,
            "snapshot_url": f"https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY&query_type=queryCarrierSnapshot&query_param=USDOT&query_string={dot_number or '2345678'}",
            "risk_flags": ["⚠️ Poor Safety Rating: Safety Rating = 'Conditional'"]
        },
        "inactive": {
            "found": True,
            "dot_number": dot_number or "3456789",
            "mc_number": "678901",
            "entity_type": "Carrier",
            "operating_status": "Out of Service",
            "safety_rating": "Unsatisfactory",
            "fleet_size": 5,
            "snapshot_url": f"https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY&query_type=queryCarrierSnapshot&query_param=USDOT&query_string={dot_number or '3456789'}",
            "risk_flags": [
                "⚠️ Inactive Status: Operating Status ≠ 'Active'",
                "⚠️ Poor Safety Rating: Safety Rating = 'Unsatisfactory'"
            ]
        },
        "not_found": {
            "found": False,
            "risk_flags": ["⚠️ Missing Record: No DOT record found"]
        }
    }
    
    # For demo, use "active_good" scenario
    return scenarios["active_good"]

def format_fmcsa_output(result, company_name):
    """Format FMCSA lookup result in conversational style."""
    
    if not result["found"]:
        return f"""
🚫 **No DOT record found for {company_name}**

If this business is transport-related, a manual check may be needed.
"""
    
    # Build the output
    output = f"""
✅ **FMCSA record found for {company_name}**

**DOT / SAFER Verification**
| Field | Value |
|---|---|
| Status | {result['operating_status']} |
| DOT # | {result['dot_number']} |
| MC # | {result['mc_number']} |
| Entity Type | {result['entity_type']} |
| Safety Rating | {result['safety_rating']} |
| Fleet Size | {result['fleet_size']} |
| SAFER Snapshot | [View Record]({result['snapshot_url']}) |
"""
    
    # Add conversational summary
    if result['operating_status'] == 'Active' and result['safety_rating'] == 'Satisfactory':
        output += "\n✅ **Status is active, safety rating is satisfactory. No issues.**\n"
    else:
        output += "\n⚠️ **RISK FLAGS DETECTED:**\n"
        for flag in result['risk_flags']:
            output += f"- {flag}\n"
    
    return output

def create_supabase_payload(result, company_name, deal_id):
    """Create JSON payload for Supabase logging."""
    
    if not result["found"]:
        return {
            "deal_id": deal_id,
            "company_name": company_name,
            "fmcsa_verification": {
                "found": False,
                "verification_timestamp": datetime.utcnow().isoformat() + 'Z'
            }
        }
    
    return {
        "deal_id": deal_id,
        "company_name": company_name,
        "fmcsa_verification": {
            "found": True,
            "dot_number": result['dot_number'],
            "mc_number": result['mc_number'],
            "operating_status": result['operating_status'],
            "safety_rating": result['safety_rating'],
            "entity_type": result['entity_type'],
            "fleet_size": result['fleet_size'],
            "snapshot_url": result['snapshot_url'],
            "risk_flags": result['risk_flags'],
            "verification_timestamp": datetime.utcnow().isoformat() + 'Z'
        }
    }

def main():
    print("=" * 70)
    print("FMCSA/DOT VERIFICATION - LendLogic v3.4")
    print("=" * 70)
    print()
    print(f"Great — now let me check their DOT status with the FMCSA...")
    print()
    
    # Perform lookup
    result = simulate_fmcsa_lookup(BORROWER_NAME, DOT_NUMBER)
    
    print("=" * 70)
    print("VERIFICATION RESULTS")
    print("=" * 70)
    
    # Display formatted output
    output = format_fmcsa_output(result, BORROWER_NAME)
    print(output)
    
    # Create Supabase payload
    print()
    print("=" * 70)
    print("SUPABASE LOGGING PAYLOAD")
    print("=" * 70)
    print()
    print("Saving DOT verification results to Supabase...")
    print()
    
    payload = create_supabase_payload(result, BORROWER_NAME, DEAL_ID)
    print(json.dumps(payload, indent=2))
    
    # Save to file
    output_file = "/home/ubuntu/lendlogic-v3.4/fmcsa_verification_result.json"
    with open(output_file, 'w') as f:
        json.dump(payload, f, indent=2)
    
    print()
    print(f"✅ Results saved to: {output_file}")
    print()
    
    # Show what this provides
    print("=" * 70)
    print("BENEFITS OF LOGGING")
    print("=" * 70)
    print()
    print("📁 Proof that a check was run")
    print("📊 Ability to report on risky carriers across all deals")
    print("🔁 Easy re-checking later if the status changes")
    print()

if __name__ == "__main__":
    main()
