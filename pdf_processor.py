import pdfplumber
import fitz  # PyMuPDF
import re
from typing import Dict, List, Tuple, Any
import os

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts all text from a PDF file using pdfplumber.
    Args:
        file_path (str): Path to the PDF file.
    Returns:
        str: The full extracted text from the PDF.
    """
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        print(text)
        return text.strip()
    except Exception as e:
        print(f"❌ Error reading PDF '{file_path}': {e}")
        return ""

def detect_signatures_multiple_methods(file_path: str) -> Dict[str, Any]:
    """
    Detect signatures using multiple methods and return comprehensive results.
    Args:
        file_path (str): Path to the PDF file.
    Returns:
        Dict: Results from all detection methods.
    """
    results = {
        'has_signatures': False,
        'signature_methods': {
            'digital_signature_fields': False,
            'form_fields': False,
            'text_indicators': False,
            'annotations': False
        },
        'details': {},
        'confidence': 'low'
    }
    
    # Method 1: Check for digital signature fields using PyMuPDF
    digital_sigs = detect_digital_signatures(file_path)
    print(digital_sigs)
    if digital_sigs['found']:
        results['has_signatures'] = True
        results['signature_methods']['digital_signature_fields'] = True
        results['details']['digital_signatures'] = digital_sigs
    
    # Method 2: Check form fields for signature widgets
    form_fields = detect_signature_form_fields(file_path)
    print('method 2')
    if form_fields['found']:
        results['has_signatures'] = True
        results['signature_methods']['form_fields'] = True
        results['details']['form_fields'] = form_fields
    
    # Method 3: Text-based detection
    text_indicators = detect_signature_text_indicators(file_path)
    print('method 3')
    if text_indicators['found']:
        results['has_signatures'] = True
        results['signature_methods']['text_indicators'] = True
        results['details']['text_indicators'] = text_indicators
    
    # Method 4: Check annotations
    annotations = detect_signature_annotations(file_path)
    print('method 4')
    if annotations['found']:
        results['has_signatures'] = True
        results['signature_methods']['annotations'] = True
        results['details']['annotations'] = annotations
    
    # Determine confidence level
    detection_count = sum(results['signature_methods'].values())
    if detection_count >= 2:
        results['confidence'] = 'high'
    elif detection_count == 1:
        results['confidence'] = 'medium'
    
    return results

def detect_digital_signatures(file_path: str) -> Dict[str, Any]:
    """
    Detect digital signatures using PyMuPDF.
    Args:
        file_path (str): Path to the PDF file.
    Returns:
        Dict: Information about digital signatures found.
    """
    result = {'found': False, 'signatures': [], 'count': 0}
    
    try:
        doc = fitz.open(file_path)
        
        # Check if document has signature flags
        sig_flags = doc.get_sigflags()
        if sig_flags > 0:
            print(f"found sig flags: {sig_flags}")
            result['found'] = True
            result['sig_flags'] = sig_flags
        
        # Look for signature fields
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            for widget in widgets:
                if widget.field_type == fitz.PDF_WIDGET_TYPE_SIGNATURE:
                    result['found'] = True
                    result['signatures'].append({
                        'page': page_num + 1,
                        'field_name': widget.field_name,
                        'field_value': widget.field_value,
                        'rect': widget.rect
                    })
        
        result['count'] = len(result['signatures'])
        doc.close()
        
    except Exception as e:
        print(f"❌ Error detecting digital signatures: {e}")
    
    return result

def detect_signature_form_fields(file_path: str) -> Dict[str, Any]:
    """
    Detect signature-related form fields.
    Args:
        file_path (str): Path to the PDF file.
    Returns:
        Dict: Information about signature form fields found.
    """
    result = {'found': False, 'fields': [], 'count': 0}
    
    try:
        doc = fitz.open(file_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()
            
            for widget in widgets:
                field_name = widget.field_name or ""
                field_value = widget.field_value or ""

                
                # Look for signature-related field names
                signature_keywords = [
                    'signature', 'sign', 'signatory', 'signed', 'signer',
                    'docusign', 'adobe sign', 'hellosign', 'esignature',
                    'digital signature', 'electronic signature'
                ]
                
                if any(keyword in field_name.lower() for keyword in signature_keywords):
                    result['found'] = True
                    result['fields'].append({
                        'page': page_num + 1,
                        'field_name': field_name,
                        'field_value': field_value,
                        'field_type': widget.field_type_string,
                        'rect': widget.rect
                    })
        
        result['count'] = len(result['fields'])
        doc.close()
        
    except Exception as e:
        print(f"❌ Error detecting signature form fields: {e}")
    
    return result

def detect_signature_text_indicators(file_path: str) -> Dict[str, Any]:
    """
    Detect signatures based on text patterns commonly found in signed documents.
    Args:
        file_path (str): Path to the PDF file.
    Returns:
        Dict: Information about text-based signature indicators.
    """
    result = {'found': False, 'indicators': [], 'patterns': []}
    
    try:
        text = extract_text_from_pdf(file_path)
        if not text:
            return result
        
        # Common signature text patterns
        signature_patterns = [
            r'digitally signed by',
            r'electronically signed',
            r'signed on \d{1,2}/\d{1,2}/\d{4}',
            r'docusign envelope id',
            r'certificate information',
            r'/s/\s*[A-Za-z\s]+',  # Common e-signature format
            r'this document was signed',
            r'signature valid',
            r'signed with adobe sign',
            r'hellosign',
            r'signatory:',
            r'signature date:',
            r'digital signature',
            r'electronic signature'
        ]
        
        for pattern in signature_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                result['found'] = True
                result['indicators'].append({
                    'pattern': pattern,
                    'match': match.group(),
                    'position': match.span()
                })
        
        # Look for date patterns near signature keywords
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{1,2}-\d{1,2}-\d{4}',
            r'\w+\s+\d{1,2},\s+\d{4}'
        ]
        
        signature_keywords = ['sign', 'signature', 'signed', 'date']
        
        for keyword in signature_keywords:
            keyword_positions = [m.start() for m in re.finditer(keyword, text, re.IGNORECASE)]
            
            for pos in keyword_positions:
                # Look for dates within 100 characters of signature keywords
                nearby_text = text[max(0, pos-50):pos+50]
                for date_pattern in date_patterns:
                    date_matches = re.finditer(date_pattern, nearby_text)
                    for date_match in date_matches:
                        result['found'] = True
                        result['patterns'].append({
                            'keyword': keyword,
                            'date_pattern': date_match.group(),
                            'context': nearby_text.strip()
                        })
        
    except Exception as e:
        print(f"❌ Error detecting signature text indicators: {e}")
    
    return result

def detect_signature_annotations(file_path: str) -> Dict[str, Any]:
    """
    Detect signature-related annotations.
    Args:
        file_path (str): Path to the PDF file.
    Returns:
        Dict: Information about signature annotations found.
    """
    result = {'found': False, 'annotations': [], 'count': 0}
    
    try:
        doc = fitz.open(file_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            annotations = page.annots()
            
            for annot in annotations:
                annot_type = annot.type[1]  # Get annotation type name
                content = annot.info.get("content", "").lower()
                title = annot.info.get("title", "").lower()
                
                # Look for signature-related annotations
                signature_indicators = [
                    'signature', 'sign', 'signed', 'docusign', 'adobe sign',
                    'electronic', 'digital', 'certificate'
                ]
                
                if (annot_type in ['Stamp', 'FreeText', 'Text'] and 
                    any(indicator in content or indicator in title 
                        for indicator in signature_indicators)):
                    
                    result['found'] = True
                    result['annotations'].append({
                        'page': page_num + 1,
                        'type': annot_type,
                        'content': annot.info.get("content", ""),
                        'title': annot.info.get("title", ""),
                        'rect': annot.rect
                    })
        
        result['count'] = len(result['annotations'])
        doc.close()
        
    except Exception as e:
        print(f"❌ Error detecting signature annotations: {e}")
    
    return result

def analyze_pdf_signatures(file_path: str) -> None:
    """
    Comprehensive analysis of PDF signatures with detailed output.
    Args:
        file_path (str): Path to the PDF file.
    """
    print(f"🔍 Analyzing PDF: {os.path.basename(file_path)}")
    print("=" * 60)
    
    # Run comprehensive signature detection
    results = detect_signatures_multiple_methods(file_path)
    
    # Display results
    if results['has_signatures']:
        print(f"✅ SIGNATURES DETECTED (Confidence: {results['confidence'].upper()})")
        print(f"📊 Detection Methods Used: {sum(results['signature_methods'].values())}/4")
        print()
        
        # Show which methods detected signatures
        for method, detected in results['signature_methods'].items():
            status = "✅" if detected else "❌"
            print(f"{status} {method.replace('_', ' ').title()}")
        
        print("\n" + "="*40 + " DETAILS " + "="*40)
        
        # Show detailed results for each method
        for method, data in results['details'].items():
            if data.get('found', False):
                print(f"\n🔎 {method.replace('_', ' ').title()}:")
                print("-" * 30)
                
                if method == 'digital_signatures':
                    if data.get('sig_flags'):
                        print(f"   Signature flags: {data['sig_flags']}")
                    if data.get('signatures'):
                        for i, sig in enumerate(data['signatures'], 1):
                            print(f"   Signature {i}:")
                            print(f"     - Page: {sig['page']}")
                            print(f"     - Field: {sig.get('field_name', 'N/A')}")
                            print(f"     - Value: {sig.get('field_value', 'N/A')}")
                
                elif method == 'form_fields':
                    for i, field in enumerate(data.get('fields', []), 1):
                        print(f"   Field {i}:")
                        print(f"     - Page: {field['page']}")
                        print(f"     - Name: {field['field_name']}")
                        print(f"     - Type: {field['field_type']}")
                        print(f"     - Value: {field.get('field_value', 'N/A')}")
                
                elif method == 'text_indicators':
                    indicators = data.get('indicators', [])
                    patterns = data.get('patterns', [])
                    
                    if indicators:
                        print(f"   Text indicators found: {len(indicators)}")
                        for indicator in indicators[:3]:  # Show first 3
                            print(f"     - Pattern: {indicator['pattern']}")
                            print(f"     - Match: '{indicator['match']}'")
                    
                    if patterns:
                        print(f"   Date patterns near signatures: {len(patterns)}")
                        for pattern in patterns[:2]:  # Show first 2
                            print(f"     - Keyword: {pattern['keyword']}")
                            print(f"     - Date: {pattern['date_pattern']}")
                
                elif method == 'annotations':
                    for i, annot in enumerate(data.get('annotations', []), 1):
                        print(f"   Annotation {i}:")
                        print(f"     - Page: {annot['page']}")
                        print(f"     - Type: {annot['type']}")
                        print(f"     - Content: {annot.get('content', 'N/A')[:50]}...")
    
    else:
        print("❌ NO SIGNATURES DETECTED")
        print("This PDF does not appear to contain any signatures.")
    
    print("\n" + "="*60)

# # Test function
# if __name__ == "__main__":
#     # Test with your PDF files
#     test_files = [
#         #"/Users/xiaofeixue/pbsa_audit/uploads/prepared_docs/1.01 2024 MeridianLink Gap Letter.pdf",
#         #"/Users/xiaofeixue/pbsa_audit/uploads/prepared_docs/1.01 2024 MeridianLink Penetration Test Letter.pdf"
#         "/Users/xiaofeixue/pbsa_audit/uploads/prepared_docs/Verified.ID New Customer Intake.pdf",
#         "/Users/xiaofeixue/pbsa_audit/uploads/prepared_docs/Verified.ID New Customer Intake 1.pdf"
#     ]
    
#     print("🚀 Starting PDF Signature Analysis")
#     print("="*80)
    
#     for file_path in test_files:
#         if os.path.exists(file_path):
#             analyze_pdf_signatures(file_path)
#             print("\n" + "🔄"*20 + " NEXT FILE " + "🔄"*20 + "\n")
#         else:
#             print(f"❌ File not found: {file_path}")
    
#     print("✅ Analysis complete!")
