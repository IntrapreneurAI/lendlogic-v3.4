#!/usr/bin/env python3.11
"""
Tesseract OCR Document Processing & Risk Review Demo for LendLogic v3.5
Demonstrates automated text extraction and risk analysis from financial documents
"""

import json
import re
import os
from datetime import datetime
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

# Sample documents to process
DOCUMENTS = [
    "/home/ubuntu/lendlogic-v3.4/test_inputs/sample_invoice_clean.pdf",
    "/home/ubuntu/lendlogic-v3.4/test_inputs/sample_application_risky.pdf"
]

def extract_text_from_pdf(pdf_path, language='eng'):
    """
    Extract text from PDF using Tesseract OCR
    """
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path)
        
        # Extract text from each page
        full_text = ""
        page_confidences = []
        
        for i, image in enumerate(images):
            # Get OCR data with confidence scores
            ocr_data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
            
            # Extract text
            page_text = pytesseract.image_to_string(image, lang=language)
            full_text += f"\n--- Page {i+1} ---\n{page_text}"
            
            # Calculate average confidence for this page
            confidences = [int(conf) for conf in ocr_data['conf'] if conf != '-1']
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
                page_confidences.append(avg_confidence)
        
        # Calculate overall confidence
        overall_confidence = sum(page_confidences) / len(page_confidences) if page_confidences else 0
        
        return {
            "status": "success",
            "text": full_text.strip(),
            "page_count": len(images),
            "confidence_score": round(overall_confidence, 2)
        }
    
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "text": None,
            "page_count": 0,
            "confidence_score": 0
        }

def check_missing_fields(text):
    """Check for missing required fields in the document"""
    missing_patterns = [
        r"Date:\s*_{3,}",
        r"Signature:\s*_{3,}",
        r"Amount:\s*_{3,}",
        r":\s*N/A",
        r"Not Provided"
    ]
    
    findings = []
    for pattern in missing_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            findings.append(f"Pattern detected: {pattern}")
    
    if findings:
        return {
            "triggered": True,
            "details": findings,
            "comment": "Document may be missing required fields (e.g., signature, date, amount)."
        }
    
    return {"triggered": False, "details": [], "comment": None}

def check_adverse_financial(text):
    """Check for adverse financial language"""
    keywords = [
        "delinquency", "delinquent", "unpaid taxes", "overdue", 
        "past due", "collection notice", "lien", "defaulted"
    ]
    
    findings = []
    for keyword in keywords:
        if re.search(rf"\b{keyword}\b", text, re.IGNORECASE):
            findings.append(keyword.title())
    
    if findings:
        return {
            "triggered": True,
            "keywords_found": findings,
            "comment": "Adverse financial language detected (e.g., delinquency, overdue balances)."
        }
    
    return {"triggered": False, "keywords_found": [], "comment": None}

def check_legal_issues(text):
    """Check for legal red flags"""
    keywords = [
        "bankruptcy", "court order", "judgment", "lawsuit", 
        "regulatory action", "foreclosure", "repossession"
    ]
    
    findings = []
    for keyword in keywords:
        if re.search(rf"\b{keyword}\b", text, re.IGNORECASE):
            findings.append(keyword.title())
    
    if findings:
        return {
            "triggered": True,
            "keywords_found": findings,
            "comment": "Potential legal issues mentioned (e.g., bankruptcy, court orders)."
        }
    
    return {"triggered": False, "keywords_found": [], "comment": None}

def check_alterations(text):
    """Check for potential document alterations"""
    keywords = [
        "corrected copy", "amended", "revised", "duplicate"
    ]
    
    findings = []
    for keyword in keywords:
        if re.search(rf"\b{keyword}\b", text, re.IGNORECASE):
            findings.append(keyword.title())
    
    if findings:
        return {
            "triggered": True,
            "indicators": findings,
            "comment": "Potential document alteration detected (e.g., duplicate entries, corrected copy markers)."
        }
    
    return {"triggered": False, "indicators": [], "comment": None}

def perform_risk_review(ocr_text, document_name):
    """Perform comprehensive risk review on OCR-extracted text"""
    
    print(f"\n{'='*70}")
    print(f"DOCUMENT RISK REVIEW: {document_name}")
    print(f"{'='*70}\n")
    
    # Run all checks
    missing_fields = check_missing_fields(ocr_text)
    adverse_financial = check_adverse_financial(ocr_text)
    legal_issues = check_legal_issues(ocr_text)
    alterations = check_alterations(ocr_text)
    
    # Compile findings
    risk_flags = {}
    triggered_count = 0
    
    if missing_fields["triggered"]:
        risk_flags["missing_fields"] = missing_fields["comment"]
        triggered_count += 1
        print(f"⚠️  Missing Fields Detected")
        print(f"   {missing_fields['comment']}\n")
    
    if adverse_financial["triggered"]:
        risk_flags["adverse_financial"] = adverse_financial["comment"]
        triggered_count += 1
        print(f"⚠️  Adverse Financial Language Detected")
        print(f"   Keywords: {', '.join(adverse_financial['keywords_found'])}")
        print(f"   {adverse_financial['comment']}\n")
    
    if legal_issues["triggered"]:
        risk_flags["legal_issues"] = legal_issues["comment"]
        triggered_count += 1
        print(f"⚠️  Legal Issues Mentioned")
        print(f"   Keywords: {', '.join(legal_issues['keywords_found'])}")
        print(f"   {legal_issues['comment']}\n")
    
    if alterations["triggered"]:
        risk_flags["alterations"] = alterations["comment"]
        triggered_count += 1
        print(f"⚠️  Potential Alterations Detected")
        print(f"   Indicators: {', '.join(alterations['indicators'])}")
        print(f"   {alterations['comment']}\n")
    
    if triggered_count == 0:
        print("✅ No document risk flags detected\n")
    
    return {
        "document_name": document_name,
        "risk_flags": risk_flags if risk_flags else None,
        "risk_count": triggered_count,
        "risk_level": "High" if triggered_count >= 3 else ("Medium" if triggered_count >= 1 else "Low"),
        "detailed_checks": {
            "missing_fields": missing_fields,
            "adverse_financial": adverse_financial,
            "legal_issues": legal_issues,
            "alterations": alterations
        }
    }

def process_document(file_path, deal_id="DEAL-2025-001"):
    """Process a single document with OCR and risk review"""
    
    document_name = os.path.basename(file_path)
    
    print(f"\n{'='*70}")
    print(f"PROCESSING DOCUMENT: {document_name}")
    print(f"{'='*70}\n")
    
    # Step 1: OCR Extraction
    print("📄 Running Tesseract OCR...")
    ocr_result = extract_text_from_pdf(file_path, language='eng')
    
    if ocr_result["status"] == "failed":
        print(f"❌ OCR Failed: {ocr_result['error']}\n")
        return {
            "document_name": document_name,
            "ocr_status": "failed",
            "ocr_error": ocr_result["error"],
            "deal_id": deal_id
        }
    
    print(f"✅ OCR Complete")
    print(f"   Pages: {ocr_result['page_count']}")
    print(f"   Confidence: {ocr_result['confidence_score']}%")
    print(f"   Text Length: {len(ocr_result['text'])} characters\n")
    
    # Step 2: Risk Review
    print("🔍 Performing risk review...")
    risk_review = perform_risk_review(ocr_result["text"], document_name)
    
    # Compile final result
    return {
        "document_name": document_name,
        "deal_id": deal_id,
        "ocr_status": "success",
        "ocr_metadata": {
            "page_count": ocr_result["page_count"],
            "confidence_score": ocr_result["confidence_score"],
            "detected_language": "eng",
            "text_length": len(ocr_result["text"])
        },
        "ocr_text_raw": ocr_result["text"],
        "document_risk_review": risk_review["risk_flags"],
        "risk_count": risk_review["risk_count"],
        "risk_level": risk_review["risk_level"],
        "processed_at": datetime.utcnow().isoformat() + 'Z'
    }

def format_report_section(document_results):
    """Format the Document Risk Review section for the underwriting report"""
    
    output = "\n## Document Risk Review\n\n"
    output += f"**Documents Processed:** {len(document_results)}\n\n"
    
    for result in document_results:
        output += f"### {result['document_name']}\n\n"
        output += f"**OCR Status:** {result['ocr_status'].title()}\n"
        
        if result['ocr_status'] == 'success':
            output += f"**Risk Level:** {result['risk_level']}\n"
            output += f"**Confidence Score:** {result['ocr_metadata']['confidence_score']}%\n\n"
            
            if result['document_risk_review']:
                output += "**Identified Risks:**\n\n"
                for key, comment in result['document_risk_review'].items():
                    output += f"- {comment}\n"
            else:
                output += "✅ No risk flags detected.\n"
        else:
            output += f"**Error:** {result.get('ocr_error', 'Unknown error')}\n"
            output += "⚠️ Manual review required.\n"
        
        output += "\n"
    
    return output

def main():
    print("=" * 70)
    print("TESSERACT OCR DOCUMENT PROCESSING - LendLogic v3.5")
    print("=" * 70)
    print()
    print("This module extracts text from documents and performs automated risk review.")
    print()
    
    results = []
    
    for doc_path in DOCUMENTS:
        if os.path.exists(doc_path):
            result = process_document(doc_path)
            results.append(result)
        else:
            print(f"⚠️  Document not found: {doc_path}\n")
    
    # Create Supabase payload
    print("\n" + "=" * 70)
    print("SUPABASE LOGGING PAYLOAD")
    print("=" * 70)
    print()
    
    supabase_payload = {
        "deal_id": "DEAL-2025-001",
        "documents": results,
        "total_documents": len(results),
        "documents_with_risks": sum(1 for r in results if r.get('risk_count', 0) > 0),
        "processing_timestamp": datetime.utcnow().isoformat() + 'Z'
    }
    
    print(json.dumps(supabase_payload, indent=2))
    
    # Save to file
    output_file = "/home/ubuntu/lendlogic-v3.4/ocr_processing_result.json"
    with open(output_file, 'w') as f:
        json.dump(supabase_payload, f, indent=2)
    
    print()
    print(f"✅ Results saved to: {output_file}")
    
    # Generate report section
    print("\n" + "=" * 70)
    print("UNDERWRITING REPORT SECTION")
    print("=" * 70)
    
    report_section = format_report_section(results)
    print(report_section)
    
    # Save report section
    report_file = "/home/ubuntu/lendlogic-v3.4/ocr_report_section.md"
    with open(report_file, 'w') as f:
        f.write(report_section)
    
    print(f"\n✅ Report section saved to: {report_file}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"Total Documents Processed: {len(results)}")
    print(f"Documents with Risk Flags: {sum(1 for r in results if r.get('risk_count', 0) > 0)}")
    print(f"OCR Failures: {sum(1 for r in results if r.get('ocr_status') == 'failed')}")
    print()
    
    if any(r.get('risk_count', 0) > 0 for r in results):
        print("⚠️  Document risks identified - review recommended")
    else:
        print("✅ No document risks identified")

if __name__ == "__main__":
    main()
