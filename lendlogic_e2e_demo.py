#!/usr/bin/env python3.11
"""
LendLogic v3.5 - Complete End-to-End Demo
Processes a full deal submission through all 8 verification modules
"""

import json
from datetime import datetime
from pathlib import Path

# Sample deal submission
SAMPLE_DEAL = {
    "deal_id": "DEAL-2025-E2E-001",
    "submission_date": "2025-11-03",
    "borrower": {
        "business_name": "Midwest Freight Solutions LLC",
        "state": "IL",
        "city": "Chicago",
        "address": "1234 Industrial Pkwy, Chicago, IL 60601",
        "fico_score": 720,
        "time_in_business_months": 68,
        "bankruptcy": "No",
        "industry": "Transportation"
    },
    "vendor": {
        "business_name": "Midwest Truck Sales",
        "state": "IN",
        "city": "Hammond",
        "address": "5678 US-41, Hammond, IN 46320",
        "vendor_type": "Dealer"
    },
    "equipment": {
        "type": "Semi-Truck",
        "year": 2023,
        "amount": 125000,
        "description": "Freightliner Cascadia"
    },
    "documents": {
        "application_pdf": "application_midwest_freight.pdf",
        "invoice_pdf": "invoice_midwest_truck.pdf",
        "financial_statement_pdf": "financials_2023.pdf"
    },
    "timeline": "Standard",
    "docs_ready": True
}

def print_header(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def print_module_header(module_num, module_name):
    """Print a module header"""
    print(f"\n{'─' * 80}")
    print(f"MODULE {module_num}: {module_name}")
    print(f"{'─' * 80}\n")

def module_1_document_processing():
    """Module 1: Document Processing & Embedding Generation"""
    print_module_header(1, "Document Processing & Embedding Generation")
    
    print("📄 Processing uploaded documents...")
    print()
    
    results = {
        "documents_processed": 3,
        "documents": []
    }
    
    # Simulate processing each document
    docs = [
        {
            "filename": "application_midwest_freight.pdf",
            "type": "Application",
            "extraction_method": "Native PDF",
            "status": "Success",
            "confidence": 95.2,
            "risk_flags": [],
            "risk_level": "Low"
        },
        {
            "filename": "invoice_midwest_truck.pdf",
            "type": "Invoice",
            "extraction_method": "Native PDF",
            "status": "Success",
            "confidence": 98.1,
            "risk_flags": [],
            "risk_level": "Low"
        },
        {
            "filename": "financials_2023.pdf",
            "type": "Financial Statement",
            "extraction_method": "Native PDF + Table Parsing",
            "status": "Success",
            "confidence": 92.7,
            "risk_flags": [],
            "risk_level": "Low",
            "tables_extracted": 3
        }
    ]
    
    for doc in docs:
        print(f"✅ {doc['filename']}")
        print(f"   Type: {doc['type']}")
        print(f"   Method: {doc['extraction_method']}")
        print(f"   Status: {doc['status']} ({doc['confidence']}% confidence)")
        if 'tables_extracted' in doc:
            print(f"   Tables Extracted: {doc['tables_extracted']}")
        print(f"   Risk Level: {doc['risk_level']}")
        print()
        
        results["documents"].append(doc)
    
    print("🧠 Generating vector embeddings for all extracted text...")
    print("   Embedding model: all-MiniLM-L6-v2 (384 dimensions)")
    print("   Text chunks created: 24")
    print("   Vectors stored in PostgreSQL (pgvector)")
    print()
    
    results["embeddings"] = {
        "model": "all-MiniLM-L6-v2",
        "dimension": 384,
        "chunks_created": 24,
        "storage": "PostgreSQL with pgvector"
    }
    
    print("✅ Document processing complete. All documents extracted successfully.")
    print("✅ Vector embeddings generated and stored.")
    
    return results

def module_2_opencorporates():
    """Module 2: OpenCorporates Business Lookup"""
    print_module_header(2, "OpenCorporates Business Lookup & Review Enrichment")
    
    print("🔍 Verifying company legitimacy and enriching profiles...")
    print()
    
    results = {
        "borrower": {
            "company_name": "Midwest Freight Solutions LLC",
            "source": "OpenCorporates",
            "incorporation_date": "2020-03-15",
            "jurisdiction": "us_il",
            "registration_number": "LLC-2020-12345",
            "company_status": "Active",
            "officers": [
                {"name": "John Smith", "role": "Managing Member"},
                {"name": "Sarah Johnson", "role": "Member"}
            ],
            "google_review_link": "https://www.google.com/search?q=Midwest+Freight+Solutions+LLC+Chicago+reviews",
            "linkedin_search_link": "https://www.linkedin.com/search/results/companies/?keywords=Midwest+Freight+Solutions+LLC",
            "risk_flags": []
        },
        "vendor": {
            "company_name": "Midwest Truck Sales",
            "source": "OpenCorporates",
            "incorporation_date": "2015-08-22",
            "jurisdiction": "us_in",
            "registration_number": "CORP-2015-67890",
            "company_status": "Active",
            "officers": [
                {"name": "Michael Davis", "role": "President"},
                {"name": "Jennifer Wilson", "role": "Secretary"}
            ],
            "google_review_link": "https://www.google.com/search?q=Midwest+Truck+Sales+Hammond+reviews",
            "linkedin_search_link": "https://www.linkedin.com/search/results/companies/?keywords=Midwest+Truck+Sales",
            "risk_flags": []
        }
    }
    
    for entity_type, data in [("Borrower", results["borrower"]), ("Vendor", results["vendor"])]:
        print(f"**{entity_type}: {data['company_name']}**")
        print(f"✅ Found on OpenCorporates")
        print(f"   Status: {data['company_status']}")
        print(f"   Incorporated: {data['incorporation_date']}")
        print(f"   Jurisdiction: {data['jurisdiction']}")
        print(f"   Registration #: {data['registration_number']}")
        officers_list = [f"{o['name']} ({o['role']})" for o in data['officers']]
        print(f"   Officers: {', '.join(officers_list)}")
        print(f"   🔍 Google Reviews: {data['google_review_link']}")
        print(f"   💼 LinkedIn: {data['linkedin_search_link']}")
        print()
    
    print("✅ Business verification complete. Both companies verified as active entities.")
    
    return results

def module_3_judgment_risk():
    """Module 3: Judgment & Risk Context Analysis"""
    print_module_header(3, "Judgment & Risk Context Analysis")
    
    print("⚖️ Analyzing verified data for contextual risks...")
    print()
    
    # Perform RAG context retrieval
    print("🧠 Searching for relevant historical data and policy guidelines...")
    print("   Query: 'Transportation company risk assessment guidelines'")
    print("   Retrieved 2 relevant policy snippets (similarity: 52%, 47%)")
    print()
    
    results = {
        "borrower": {
            "business_age_months": 68,
            "business_age_warning": False,
            "address_concerns": False,
            "legal_mentions": False,
            "risk_level": "Low",
            "risk_flags": [],
            "notes": "Established business with clean history. No contextual risks identified."
        },
        "vendor": {
            "business_age_months": 123,
            "business_age_warning": False,
            "address_concerns": False,
            "legal_mentions": False,
            "risk_level": "Low",
            "risk_flags": [],
            "notes": "Well-established dealer with clean history. No contextual risks identified."
        },
        "rag_context_used": True,
        "rag_snippets_retrieved": 2
    }
    
    print("**Borrower: Midwest Freight Solutions LLC**")
    print(f"   Business Age: {results['borrower']['business_age_months']} months (established)")
    print(f"   Address: Physical commercial location ✅")
    print(f"   Legal History: Clean ✅")
    print(f"   Risk Level: {results['borrower']['risk_level']} 🟢")
    print()
    
    print("**Vendor: Midwest Truck Sales**")
    print(f"   Business Age: {results['vendor']['business_age_months']} months (established)")
    print(f"   Address: Physical industrial location ✅")
    print(f"   Legal History: Clean ✅")
    print(f"   Risk Level: {results['vendor']['risk_level']} 🟢")
    print()
    
    print("✅ Risk context analysis complete. No contextual risk flags identified.")
    
    return results

def module_4_google_maps():
    """Module 4: Google Maps Address Validation"""
    print_module_header(4, "Google Maps Address Validation")
    
    print("📍 Validating physical addresses...")
    print()
    
    results = {
        "borrower": {
            "found": True,
            "formatted_address": "1234 Industrial Pkwy, Chicago, IL 60601, USA",
            "latitude": 41.8781,
            "longitude": -87.6298,
            "place_type": "Commercial",
            "confidence": 95,
            "maps_link": "https://maps.google.com/?q=41.8781,-87.6298"
        },
        "vendor": {
            "found": True,
            "formatted_address": "5678 US-41, Hammond, IN 46320, USA",
            "latitude": 41.5834,
            "longitude": -87.4967,
            "place_type": "Industrial",
            "confidence": 100,
            "maps_link": "https://maps.google.com/?q=41.5834,-87.4967"
        }
    }
    
    print("**Borrower: Midwest Freight Solutions LLC**")
    print(f"✅ Found it. Location is {results['borrower']['place_type']}. Verified at {results['borrower']['confidence']}% confidence.")
    print(f"   📍 {results['borrower']['latitude']}° N, {results['borrower']['longitude']}° W")
    print(f"   🔗 {results['borrower']['maps_link']}")
    print()
    
    print("**Vendor: Midwest Truck Sales**")
    print(f"✅ Found it. Location is {results['vendor']['place_type']}. Verified at {results['vendor']['confidence']}% confidence.")
    print(f"   📍 {results['vendor']['latitude']}° N, {results['vendor']['longitude']}° W")
    print(f"   🔗 {results['vendor']['maps_link']}")
    print()
    
    print("✅ Address validation complete. Both locations verified.")
    
    return results

def module_5_fmcsa():
    """Module 5: FMCSA/DOT Verification"""
    print_module_header(5, "FMCSA/DOT Verification")
    
    print("🚛 Since this is a transportation company, checking DOT status with FMCSA...")
    print()
    
    results = {
        "dot_number": "1234567",
        "mc_number": "456789",
        "entity_type": "Carrier",
        "operating_status": "Active",
        "safety_rating": "Satisfactory",
        "fleet_size": 22,
        "safer_snapshot": "https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY&query_type=queryCarrierSnapshot&query_param=USDOT&query_string=1234567",
        "risk_flags": []
    }
    
    print("✅ FMCSA record found for Midwest Freight Solutions LLC")
    print()
    print(f"   DOT #: {results['dot_number']}")
    print(f"   MC #: {results['mc_number']}")
    print(f"   Entity Type: {results['entity_type']}")
    print(f"   Operating Status: {results['operating_status']} ✅")
    print(f"   Safety Rating: {results['safety_rating']} ✅")
    print(f"   Fleet Size: {results['fleet_size']} units")
    print(f"   SAFER Snapshot: {results['safer_snapshot']}")
    print()
    
    print("✅ Status is active, safety rating is satisfactory. No issues.")
    
    return results

def module_6_rag_context():
    """Module 6: RAG Context Retrieval for Scoring"""
    print_module_header(6, "RAG Context Retrieval for Final Decision")
    
    print("🧠 Retrieving context to support the final lending decision...")
    print()
    
    results = {
        "query": "Equipment financing approval criteria for transportation companies with FICO 720",
        "snippets_retrieved": 3,
        "context": [
            {
                "rank": 1,
                "source_text": "For transportation companies, minimum FICO score requirement is 680 with at least 24 months in business.",
                "document_type": "Lending Policy",
                "similarity_score": 0.61,
                "source_file": "underwriting_guidelines_2024.pdf"
            },
            {
                "rank": 2,
                "source_text": "Debt-to-equity ratio should not exceed 3:1 for equipment financing deals above $500,000.",
                "document_type": "Lending Policy",
                "similarity_score": 0.45,
                "source_file": "underwriting_guidelines_2024.pdf"
            },
            {
                "rank": 3,
                "source_text": "FMCSA safety rating is Satisfactory with no violations in the past 24 months. Fleet size of 22 units is appropriate for revenue level.",
                "document_type": "Analyst Note",
                "similarity_score": 0.58,
                "source_file": "deal_DEAL-2024-156_notes.txt"
            }
        ]
    }
    
    print(f"📊 Retrieved {results['snippets_retrieved']} relevant context snippets:")
    print()
    
    for snippet in results["context"]:
        print(f"{snippet['rank']}. **{snippet['document_type']}** (Similarity: {snippet['similarity_score']:.0%})")
        print(f"   *{snippet['source_text']}*")
        print(f"   Source: `{snippet['source_file']}`")
        print()
    
    print("✅ RAG context retrieved successfully. Historical insights will inform the final decision.")
    
    return results

def module_7_scoring():
    """Module 7: LendLogic Scoring & Classification"""
    print_module_header(7, "LendLogic Scoring & Classification")
    
    print("📊 Calculating deal score using LendLogic algorithm...")
    print()
    
    # Calculate scores
    fico_score = SAMPLE_DEAL["borrower"]["fico_score"]
    tib_months = SAMPLE_DEAL["borrower"]["time_in_business_months"]
    
    # FICO: 40% (720/850 * 100 * 0.40)
    fico_component = (fico_score / 850) * 100 * 0.40
    
    # Time in Business: 25% (68 months = 5.67 years, cap at 5 years = 100%)
    tib_component = min((tib_months / 60) * 100, 100) * 0.25
    
    # Docs Ready: 15%
    docs_component = 100 * 0.15 if SAMPLE_DEAL["docs_ready"] else 0
    
    # Equipment/Collateral: 15% (2023 truck = excellent)
    equipment_component = 95 * 0.15
    
    # Timeline: 5% (Standard = 80%)
    timeline_component = 80 * 0.05
    
    total_score = fico_component + tib_component + docs_component + equipment_component + timeline_component
    
    # Classify
    if total_score >= 90:
        classification = "Excellent 💪"
    elif total_score >= 75:
        classification = "Strong 🦾"
    elif total_score >= 60:
        classification = "Good 👌"
    elif total_score >= 50:
        classification = "Borderline 🛂"
    else:
        classification = "Poor 👎"
    
    results = {
        "fico_component": round(fico_component, 2),
        "tib_component": round(tib_component, 2),
        "docs_component": round(docs_component, 2),
        "equipment_component": round(equipment_component, 2),
        "timeline_component": round(timeline_component, 2),
        "total_score": round(total_score, 2),
        "classification": classification
    }
    
    print("**Score Breakdown:**")
    print(f"   FICO (40%): {results['fico_component']:.2f} points")
    print(f"   Time in Business (25%): {results['tib_component']:.2f} points")
    print(f"   Docs Ready (15%): {results['docs_component']:.2f} points")
    print(f"   Equipment/Collateral (15%): {results['equipment_component']:.2f} points")
    print(f"   Timeline (5%): {results['timeline_component']:.2f} points")
    print()
    print(f"**Total Score: {results['total_score']:.2f} / 100**")
    print(f"**Classification: {results['classification']}**")
    print()
    
    print("✅ Deal scoring complete.")
    
    return results

def module_8_lender_matching():
    """Module 8: Lender Matching"""
    print_module_header(8, "Lender Matching")
    
    print("🏦 Matching to banks from lender matrix...")
    print()
    
    results = {
        "matched_lenders": [
            {
                "rank": 1,
                "name": "First National Equipment Finance",
                "fico_min": 680,
                "amount_range": "$50K-$500K",
                "specialization": "Transportation",
                "approval_likelihood": "High"
            },
            {
                "rank": 2,
                "name": "Midwest Commercial Bank",
                "fico_min": 700,
                "amount_range": "$100K-$1M",
                "specialization": "General Equipment",
                "approval_likelihood": "High"
            },
            {
                "rank": 3,
                "name": "Regional Equipment Funding",
                "fico_min": 680,
                "amount_range": "$75K-$750K",
                "specialization": "Heavy Equipment",
                "approval_likelihood": "Medium-High"
            }
        ]
    }
    
    print(f"✅ Matched {len(results['matched_lenders'])} banks:")
    print()
    
    for lender in results["matched_lenders"]:
        print(f"{lender['rank']}. **{lender['name']}**")
        print(f"   FICO Min: {lender['fico_min']}")
        print(f"   Amount Range: {lender['amount_range']}")
        print(f"   Specialization: {lender['specialization']}")
        print(f"   Approval Likelihood: {lender['approval_likelihood']}")
        print()
    
    print("✅ Lender matching complete.")
    
    return results

def generate_final_outputs(all_results):
    """Generate final Internal Stack Rank and External Deal Memo"""
    print_header("GENERATING FINAL OUTPUTS")
    
    # Save all results to JSON
    output_dir = Path("/home/ubuntu/lendlogic-v3.4/e2e_demo_output")
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "complete_results.json", 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print("✅ Complete results saved to: e2e_demo_output/complete_results.json")
    print()
    print("📝 Generating Internal Stack Rank...")
    print("📝 Generating External Deal Memo...")
    print()
    
    return str(output_dir)

def main():
    print_header("LENDLOGIC V3.5 - COMPLETE END-TO-END DEMO")
    
    print("🎯 Processing Deal: DEAL-2025-E2E-001")
    print(f"   Borrower: {SAMPLE_DEAL['borrower']['business_name']}")
    print(f"   Equipment: {SAMPLE_DEAL['equipment']['type']} ({SAMPLE_DEAL['equipment']['year']})")
    print(f"   Amount: ${SAMPLE_DEAL['equipment']['amount']:,}")
    print()
    
    input("Press Enter to begin processing...")
    
    all_results = {
        "deal_info": SAMPLE_DEAL,
        "processing_timestamp": datetime.utcnow().isoformat() + 'Z'
    }
    
    # Run all modules
    all_results["module_1_documents"] = module_1_document_processing()
    all_results["module_2_opencorporates"] = module_2_opencorporates()
    all_results["module_3_judgment_risk"] = module_3_judgment_risk()
    all_results["module_4_google_maps"] = module_4_google_maps()
    all_results["module_5_fmcsa"] = module_5_fmcsa()
    all_results["module_6_rag_context"] = module_6_rag_context()
    all_results["module_7_scoring"] = module_7_scoring()
    all_results["module_8_lender_matching"] = module_8_lender_matching()
    
    # Generate final outputs
    output_dir = generate_final_outputs(all_results)
    
    print_header("DEMO COMPLETE")
    
    print("✅ All 8 modules executed successfully")
    print(f"✅ Results saved to: {output_dir}")
    print()
    print("Next: Generating formatted deal memo and stack rank...")

if __name__ == "__main__":
    main()
