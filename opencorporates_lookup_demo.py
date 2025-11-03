#!/usr/bin/env python3.11
"""
OpenCorporates Business Lookup Demo for LendLogic v3.4
Demonstrates real-time business verification with fallback logic and Supabase integration
"""

import json
import os
from datetime import datetime

# Sample companies from test deal
BORROWER_NAME = "Midwest Freight Solutions LLC"
BORROWER_STATE = "IL"
VENDOR_NAME = "Midwest Truck Sales"
VENDOR_STATE = "IN"
DEAL_ID = "DEAL-2025-001"

def opencorporates_lookup(company_name, jurisdiction=None):
    """
    Primary lookup using OpenCorporates API.
    In production, this would make a real API call to:
    https://api.opencorporates.com/v0.4/companies/search?q={company_name}&jurisdiction_code={jurisdiction}
    """
    
    api_key = os.environ.get('OPENCORPORATES_API_KEY')
    
    if not api_key:
        print(f"⚠️  No OPENCORPORATES_API_KEY found in environment variables")
        print(f"    Using simulated data for demonstration purposes\n")
        return simulate_opencorporates_result(company_name, jurisdiction)
    
    # In production, make actual API call here
    # For demo, use simulation
    return simulate_opencorporates_result(company_name, jurisdiction)

def simulate_opencorporates_result(company_name, jurisdiction):
    """Simulate OpenCorporates API response."""
    
    # Simulate different scenarios
    if "Midwest Freight" in company_name:
        return {
            "success": True,
            "source": "OpenCorporates",
            "data": {
                "company_name": company_name,
                "incorporation_date": "2020-03-15",
                "jurisdiction": f"us_{jurisdiction.lower()}" if jurisdiction else "us_il",
                "registration_number": "LLC-2020-12345",
                "company_status": "Active",
                "officers": [
                    {"name": "John Smith", "role": "Managing Member"},
                    {"name": "Sarah Johnson", "role": "Member"}
                ],
                "registered_address": "1234 Industrial Parkway, Chicago, IL 60601"
            }
        }
    elif "Midwest Truck" in company_name:
        return {
            "success": True,
            "source": "OpenCorporates",
            "data": {
                "company_name": company_name,
                "incorporation_date": "2015-08-22",
                "jurisdiction": f"us_{jurisdiction.lower()}" if jurisdiction else "us_in",
                "registration_number": "CORP-2015-67890",
                "company_status": "Active",
                "officers": [
                    {"name": "Michael Davis", "role": "President"},
                    {"name": "Jennifer Wilson", "role": "Secretary"}
                ],
                "registered_address": "5678 Highway 41, Hammond, IN 46320"
            }
        }
    else:
        # Simulate no match found
        return {
            "success": False,
            "source": "OpenCorporates",
            "error": "No matching company found"
        }

def fallback_web_search(company_name, state):
    """
    Fallback #1: Structured web search
    In production, this would use search APIs or browser automation
    """
    print(f"🔄 Fallback #1: Running web search for {company_name}...")
    
    # Simulate finding company website
    return {
        "success": True,
        "source": "Web Search - Google",
        "data": {
            "company_name": company_name,
            "website": f"https://www.{company_name.lower().replace(' ', '')}.com",
            "incorporation_date": None,  # Not always available from web search
            "company_status": "Active (inferred from active website)",
            "officers": [],
            "note": "Limited data from web search - manual verification recommended"
        }
    }

def fallback_third_party_api(company_name):
    """
    Fallback #2: Third-party data APIs (BBB, TLO, etc.)
    In production, this would call actual APIs
    """
    print(f"🔄 Fallback #2: Checking third-party APIs for {company_name}...")
    
    # Simulate BBB lookup
    return {
        "success": True,
        "source": "BBB API",
        "data": {
            "company_name": company_name,
            "bbb_rating": "A+",
            "years_in_business": 8,
            "company_status": "Active",
            "officers": [],
            "note": "Data from BBB - incorporation details not available"
        }
    }

def fallback_manual_review(company_name):
    """
    Fallback #3: Mark for manual review
    """
    print(f"⚠️  Fallback #3: Marking {company_name} for manual review...")
    
    return {
        "success": False,
        "source": "Manual Review Required",
        "data": {
            "company_name": company_name,
            "company_status": "Unverified",
            "note": "All automated lookups failed - manual verification required"
        }
    }

def perform_business_lookup(company_name, state, entity_type="Borrower"):
    """
    Complete business lookup with fallback logic
    """
    print(f"\n{'='*70}")
    print(f"BUSINESS LOOKUP: {entity_type}")
    print(f"{'='*70}\n")
    print(f"🔍 Looking up: {company_name} ({state})")
    print()
    
    # Step 1: Try OpenCorporates
    result = opencorporates_lookup(company_name, state)
    
    if result["success"]:
        print(f"✅ Found via {result['source']}")
        return result
    
    # Step 2: Fallback to web search
    print(f"❌ OpenCorporates lookup failed: {result.get('error', 'Unknown error')}")
    result = fallback_web_search(company_name, state)
    
    if result["success"]:
        print(f"✅ Found via {result['source']}")
        return result
    
    # Step 3: Fallback to third-party APIs
    print(f"❌ Web search failed")
    result = fallback_third_party_api(company_name)
    
    if result["success"]:
        print(f"✅ Found via {result['source']}")
        return result
    
    # Step 4: Manual review
    print(f"❌ Third-party API lookup failed")
    return fallback_manual_review(company_name)

def assess_risk(data):
    """Assess risk based on business lookup data"""
    risk_flags = []
    
    if data.get("company_status") != "Active":
        risk_flags.append("⚠️ Company status is not Active")
    
    if not data.get("incorporation_date"):
        risk_flags.append("⚠️ Missing incorporation date")
    
    if not data.get("officers") or len(data.get("officers", [])) == 0:
        risk_flags.append("⚠️ No officers listed")
    
    return risk_flags

def create_supabase_payload(company_name, result, entity_type, deal_id):
    """Create JSON payload for Supabase business_profiles table"""
    
    data = result.get("data", {})
    risk_flags = assess_risk(data)
    
    payload = {
        "company_name": company_name,
        "incorporation_date": data.get("incorporation_date"),
        "jurisdiction": data.get("jurisdiction"),
        "registration_number": data.get("registration_number"),
        "company_status": data.get("company_status"),
        "officers": data.get("officers", []),
        "source": result.get("source"),
        "fallback_source": result.get("source") if result.get("source") != "OpenCorporates" else None,
        "risk_flags": risk_flags,
        "entity_type": entity_type,
        "deal_id": deal_id,
        "last_updated_at": datetime.utcnow().isoformat() + 'Z'
    }
    
    return payload

def format_output(company_name, result, entity_type):
    """Format business lookup results for display"""
    
    data = result.get("data", {})
    risk_flags = assess_risk(data)
    
    output = f"\n**{entity_type}: {company_name}**\n"
    output += f"Source: {result.get('source')}\n\n"
    
    if result.get("success"):
        output += "| Field | Value |\n"
        output += "|---|---|\n"
        output += f"| Status | {data.get('company_status', 'Unknown')} |\n"
        
        if data.get("incorporation_date"):
            output += f"| Incorporation Date | {data.get('incorporation_date')} |\n"
        
        if data.get("jurisdiction"):
            output += f"| Jurisdiction | {data.get('jurisdiction')} |\n"
        
        if data.get("registration_number"):
            output += f"| Registration # | {data.get('registration_number')} |\n"
        
        if data.get("officers"):
            officers_str = ", ".join([f"{o['name']} ({o['role']})" for o in data.get("officers", [])])
            output += f"| Officers | {officers_str} |\n"
        
        if data.get("note"):
            output += f"\nℹ️  {data.get('note')}\n"
        
        if risk_flags:
            output += "\n**Risk Flags:**\n"
            for flag in risk_flags:
                output += f"- {flag}\n"
        else:
            output += "\n✅ No risk flags detected\n"
    else:
        output += f"❌ Lookup failed: {data.get('note', 'Unknown error')}\n"
    
    return output

def main():
    print("=" * 70)
    print("OPENCORPORATES BUSINESS LOOKUP - LendLogic v3.4")
    print("=" * 70)
    
    # Lookup borrower
    borrower_result = perform_business_lookup(BORROWER_NAME, BORROWER_STATE, "Borrower")
    
    # Lookup vendor
    vendor_result = perform_business_lookup(VENDOR_NAME, VENDOR_STATE, "Vendor")
    
    # Display results
    print("\n" + "=" * 70)
    print("LOOKUP RESULTS")
    print("=" * 70)
    
    print(format_output(BORROWER_NAME, borrower_result, "Borrower"))
    print(format_output(VENDOR_NAME, vendor_result, "Vendor"))
    
    # Create Supabase payloads
    print("\n" + "=" * 70)
    print("SUPABASE LOGGING PAYLOADS")
    print("=" * 70)
    print()
    
    borrower_payload = create_supabase_payload(BORROWER_NAME, borrower_result, "Borrower", DEAL_ID)
    vendor_payload = create_supabase_payload(VENDOR_NAME, vendor_result, "Vendor", DEAL_ID)
    
    combined_payload = {
        "deal_id": DEAL_ID,
        "borrower_profile": borrower_payload,
        "vendor_profile": vendor_payload,
        "lookup_timestamp": datetime.utcnow().isoformat() + 'Z'
    }
    
    print(json.dumps(combined_payload, indent=2))
    
    # Save to file
    output_file = "/home/ubuntu/lendlogic-v3.4/opencorporates_lookup_result.json"
    with open(output_file, 'w') as f:
        json.dump(combined_payload, f, indent=2)
    
    print()
    print(f"✅ Results saved to: {output_file}")
    print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"Borrower: {borrower_result.get('source')}")
    print(f"Vendor: {vendor_result.get('source')}")
    print()
    
    if borrower_result.get("source") != "OpenCorporates" or vendor_result.get("source") != "OpenCorporates":
        print("⚠️  One or more fallback sources were used")
    else:
        print("✅ All lookups completed via primary source (OpenCorporates)")

if __name__ == "__main__":
    main()
