#!/usr/bin/env python3.11
"""
Judgment & Risk Context Analysis Demo for LendLogic v3.5
Demonstrates automated red flag detection for business age, address concerns, and legal issues
"""

import json
import re
from datetime import datetime, timedelta

# Sample company data (from previous enrichment)
BORROWER_DATA = {
    "company_name": "Midwest Freight Solutions LLC",
    "incorporation_date": "2020-03-15",
    "registered_address": "1234 Industrial Parkway, Chicago, IL 60601",
    "google_maps_place_type": "Commercial",
    "officers": [
        {"name": "John Smith", "role": "Managing Member"},
        {"name": "Sarah Johnson", "role": "Member"}
    ]
}

VENDOR_DATA = {
    "company_name": "QuickStart Logistics Inc",
    "incorporation_date": "2024-09-01",  # Less than 12 months old
    "registered_address": "PMB 456, 789 Virtual Office Blvd, Dallas, TX 75201",
    "google_maps_place_type": "Mail Service",
    "officers": [
        {"name": "Michael Davis", "role": "President"}
    ]
}

def calculate_business_age_months(incorporation_date_str):
    """Calculate the age of the business in months"""
    if not incorporation_date_str:
        return None
    
    incorporation_date = datetime.strptime(incorporation_date_str, "%Y-%m-%d")
    current_date = datetime.utcnow()
    age_delta = current_date - incorporation_date
    age_months = age_delta.days / 30.44  # Average days per month
    
    return age_months

def check_business_age_warning(company_data):
    """Check if the business is less than 12 months old"""
    incorporation_date = company_data.get("incorporation_date")
    
    if not incorporation_date:
        return None
    
    age_months = calculate_business_age_months(incorporation_date)
    
    if age_months and age_months < 12:
        return {
            "flag": "business_age_warning",
            "triggered": True,
            "age_months": round(age_months, 1),
            "comment": "Newly formed entity — proceed with caution."
        }
    
    return {
        "flag": "business_age_warning",
        "triggered": False,
        "age_months": round(age_months, 1) if age_months else None,
        "comment": None
    }

def check_address_concerns(company_data):
    """Check for non-physical or shared addresses"""
    address = company_data.get("registered_address", "")
    place_type = company_data.get("google_maps_place_type", "")
    
    # Keywords that indicate problematic addresses
    risky_keywords = ["PO Box", "P.O. Box", "PMB", "Virtual Office", "Mail Service", "Suite"]
    
    # Check for keywords in address
    for keyword in risky_keywords:
        if keyword.lower() in address.lower():
            return {
                "flag": "address_concerns",
                "triggered": True,
                "reason": f"Address contains '{keyword}'",
                "place_type": place_type,
                "comment": "Non-physical or shared address may indicate operational risk."
            }
    
    # Check Google Maps place type
    risky_place_types = ["Mail Service", "Virtual Office", "Residential"]
    if place_type in risky_place_types:
        return {
            "flag": "address_concerns",
            "triggered": True,
            "reason": f"Google Maps place type is '{place_type}'",
            "place_type": place_type,
            "comment": "Non-physical or shared address may indicate operational risk."
        }
    
    return {
        "flag": "address_concerns",
        "triggered": False,
        "reason": None,
        "place_type": place_type,
        "comment": None
    }

def check_legal_mentions(company_data):
    """
    Check for legal issues (liens, judgments, bankruptcies)
    In production, this would query TLO API or perform web searches
    """
    company_name = company_data.get("company_name")
    officers = company_data.get("officers", [])
    
    # Simulated check (in production, would call TLO API or web search)
    # For demo purposes, we'll flag if the company name contains certain keywords
    
    risky_indicators = ["lawsuit", "bankrupt", "lien", "judgment"]
    
    # Simulate finding no issues for most companies
    # (In production, this would be a real API call or web search)
    
    return {
        "flag": "legal_mentions",
        "triggered": False,
        "sources_checked": ["TLO API (simulated)", "Web Search (simulated)"],
        "comment": None
    }

def analyze_judgment_risk(company_data, entity_type="Company"):
    """Perform complete judgment and risk context analysis"""
    
    print(f"\n{'='*70}")
    print(f"JUDGMENT & RISK CONTEXT ANALYSIS: {entity_type}")
    print(f"{'='*70}\n")
    print(f"🔍 Analyzing: {company_data.get('company_name')}")
    print()
    
    # Run all checks
    age_check = check_business_age_warning(company_data)
    address_check = check_address_concerns(company_data)
    legal_check = check_legal_mentions(company_data)
    
    # Compile results
    judgment_risk_notes = {}
    triggered_flags = []
    
    if age_check["triggered"]:
        judgment_risk_notes["business_age_warning"] = age_check["comment"]
        triggered_flags.append(f"⚠️ Business Age: {age_check['age_months']} months old")
    
    if address_check["triggered"]:
        judgment_risk_notes["address_concerns"] = address_check["comment"]
        triggered_flags.append(f"⚠️ Address: {address_check['reason']}")
    
    if legal_check["triggered"]:
        judgment_risk_notes["legal_mentions"] = legal_check["comment"]
        triggered_flags.append("⚠️ Legal: Adverse history found")
    
    # Display results
    if triggered_flags:
        print("⚠️  CONTEXTUAL RISKS IDENTIFIED:\n")
        for flag in triggered_flags:
            print(f"   {flag}")
        print()
    else:
        print("✅ No contextual risk flags detected\n")
    
    # Detailed breakdown
    print("**Analysis Details:**\n")
    print(f"1. Business Age Check:")
    if age_check["triggered"]:
        print(f"   ⚠️  {age_check['comment']}")
        print(f"   Age: {age_check['age_months']} months")
    else:
        print(f"   ✅ Business is {age_check['age_months']} months old (> 12 months)")
    print()
    
    print(f"2. Address Verification:")
    if address_check["triggered"]:
        print(f"   ⚠️  {address_check['comment']}")
        print(f"   Reason: {address_check['reason']}")
    else:
        print(f"   ✅ Address appears to be a physical {address_check['place_type']} location")
    print()
    
    print(f"3. Legal & Public Records:")
    if legal_check["triggered"]:
        print(f"   ⚠️  {legal_check['comment']}")
    else:
        print(f"   ✅ No adverse legal or financial history found")
        print(f"   Sources checked: {', '.join(legal_check['sources_checked'])}")
    print()
    
    return {
        "company_name": company_data.get("company_name"),
        "entity_type": entity_type,
        "judgment_risk_notes": judgment_risk_notes if judgment_risk_notes else None,
        "risk_flag_count": len(triggered_flags),
        "risk_level": "High" if len(triggered_flags) >= 2 else ("Medium" if len(triggered_flags) == 1 else "Low"),
        "detailed_checks": {
            "business_age": age_check,
            "address": address_check,
            "legal": legal_check
        }
    }

def create_supabase_payload(analysis_result, deal_id):
    """Create Supabase payload with judgment risk notes"""
    
    return {
        "company_name": analysis_result["company_name"],
        "entity_type": analysis_result["entity_type"],
        "judgment_risk_notes": analysis_result["judgment_risk_notes"],
        "risk_flag_count": analysis_result["risk_flag_count"],
        "risk_level": analysis_result["risk_level"],
        "deal_id": deal_id,
        "analyzed_at": datetime.utcnow().isoformat() + 'Z'
    }

def format_report_section(borrower_analysis, vendor_analysis):
    """Format the Judgment & Risk Context section for the underwriting report"""
    
    output = "\n## Judgment & Risk Context\n\n"
    
    # Borrower
    output += f"### Borrower: {borrower_analysis['company_name']}\n\n"
    output += f"**Risk Level:** {borrower_analysis['risk_level']}\n\n"
    
    if borrower_analysis["judgment_risk_notes"]:
        output += "**Identified Concerns:**\n\n"
        for key, comment in borrower_analysis["judgment_risk_notes"].items():
            output += f"- {comment}\n"
    else:
        output += "✅ No contextual risk flags detected.\n"
    
    output += "\n"
    
    # Vendor
    output += f"### Vendor: {vendor_analysis['company_name']}\n\n"
    output += f"**Risk Level:** {vendor_analysis['risk_level']}\n\n"
    
    if vendor_analysis["judgment_risk_notes"]:
        output += "**Identified Concerns:**\n\n"
        for key, comment in vendor_analysis["judgment_risk_notes"].items():
            output += f"- {comment}\n"
    else:
        output += "✅ No contextual risk flags detected.\n"
    
    return output

def main():
    print("=" * 70)
    print("JUDGMENT & RISK CONTEXT ANALYSIS - LendLogic v3.5")
    print("=" * 70)
    print()
    print("This module analyzes verified business data for deeper contextual risks.")
    print()
    
    # Analyze borrower
    borrower_analysis = analyze_judgment_risk(BORROWER_DATA, "Borrower")
    
    # Analyze vendor
    vendor_analysis = analyze_judgment_risk(VENDOR_DATA, "Vendor")
    
    # Create Supabase payloads
    print("\n" + "=" * 70)
    print("SUPABASE LOGGING PAYLOADS")
    print("=" * 70)
    print()
    
    deal_id = "DEAL-2025-001"
    
    borrower_payload = create_supabase_payload(borrower_analysis, deal_id)
    vendor_payload = create_supabase_payload(vendor_analysis, deal_id)
    
    combined_payload = {
        "deal_id": deal_id,
        "borrower_judgment": borrower_payload,
        "vendor_judgment": vendor_payload,
        "analysis_timestamp": datetime.utcnow().isoformat() + 'Z'
    }
    
    print(json.dumps(combined_payload, indent=2))
    
    # Save to file
    output_file = "/home/ubuntu/lendlogic-v3.4/judgment_risk_result.json"
    with open(output_file, 'w') as f:
        json.dump(combined_payload, f, indent=2)
    
    print()
    print(f"✅ Results saved to: {output_file}")
    
    # Generate report section
    print("\n" + "=" * 70)
    print("UNDERWRITING REPORT SECTION")
    print("=" * 70)
    
    report_section = format_report_section(borrower_analysis, vendor_analysis)
    print(report_section)
    
    # Save report section
    report_file = "/home/ubuntu/lendlogic-v3.4/judgment_risk_report_section.md"
    with open(report_file, 'w') as f:
        f.write(report_section)
    
    print(f"\n✅ Report section saved to: {report_file}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"Borrower Risk Level: {borrower_analysis['risk_level']} ({borrower_analysis['risk_flag_count']} flags)")
    print(f"Vendor Risk Level: {vendor_analysis['risk_level']} ({vendor_analysis['risk_flag_count']} flags)")
    print()
    
    if borrower_analysis['risk_flag_count'] > 0 or vendor_analysis['risk_flag_count'] > 0:
        print("⚠️  Contextual risks identified - review recommended")
    else:
        print("✅ No contextual risks identified")

if __name__ == "__main__":
    main()
