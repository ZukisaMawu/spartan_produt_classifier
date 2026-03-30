"""
Enhanced JSON Parser for SPARTAN AI responses
"""

import json
import re
from typing import Dict


class EnhancedJSONParser:
    """Robust JSON parsing with multiple fallback strategies"""
    
    @staticmethod
    def clean_and_parse(text: str) -> Dict:
        """Multiple strategies to extract and parse JSON from AI response"""
        
        # Strategy 1: Direct JSON parsing
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Remove markdown code blocks
        cleaned = text.strip()
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]
        
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        
        cleaned = cleaned.strip()
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        
        # Strategy 3: Extract JSON using regex
        json_patterns = [
            r'\{[^{}]*"mch_levels"[^{}]*\}',
            r'\{.*?"mch_levels".*?\}',
            r'\{(?:[^{}]|{[^{}]*})*\}'
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, cleaned, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    parsed = json.loads(match)
                    if 'mch_levels' in parsed:
                        return parsed
                except json.JSONDecodeError:
                    continue
        
        # Strategy 4: Manual extraction as last resort
        try:
            result = {}
            
            # Extract mch_levels
            mch_match = re.search(r'"mch_levels"\s*:\s*"([^"]*)"', cleaned, re.IGNORECASE)
            if mch_match:
                result['mch_levels'] = mch_match.group(1)
            
            # Extract confidence_score
            conf_match = re.search(r'"confidence_score"\s*:\s*([0-9.]+)', cleaned, re.IGNORECASE)
            if conf_match:
                result['confidence_score'] = float(conf_match.group(1))
            
            # Extract reasoning
            reason_match = re.search(r'"reasoning"\s*:\s*"([^"]*)"', cleaned, re.IGNORECASE)
            if reason_match:
                result['reasoning'] = reason_match.group(1)
            
            # Extract reference_match_found
            ref_match = re.search(r'"reference_match_found"\s*:\s*(true|false)', cleaned, re.IGNORECASE)
            if ref_match:
                result['reference_match_found'] = ref_match.group(1).lower() == 'true'
            
            # Extract product_type
            product_match = re.search(r'"product_type"\s*:\s*"([^"]*)"', cleaned, re.IGNORECASE)
            if product_match:
                result['product_type'] = product_match.group(1)
            
            # Extract barcode_lookup_used
            barcode_match = re.search(r'"barcode_lookup_used"\s*:\s*(true|false)', cleaned, re.IGNORECASE)
            if barcode_match:
                result['barcode_lookup_used'] = barcode_match.group(1).lower() == 'true'
            
            if 'mch_levels' in result:
                return result
                
        except Exception:
            pass
        
        # If all else fails, return error structure
        return {
            "mch_levels": "JSON_PARSE_ERROR",
            "confidence_score": 0.0,
            "reference_match_found": False,
            "reasoning": f"Failed to parse AI response: {cleaned[:200]}...",
            "raw_response": text
        }
    
    @staticmethod
    def validate_result(result: Dict) -> Dict:
        """Validate and ensure required fields exist"""
        validated = result.copy()
        
        # Ensure required fields exist
        if 'mch_levels' not in validated:
            validated['mch_levels'] = 'PARSE_ERROR'
        
        if 'confidence_score' not in validated:
            validated['confidence_score'] = 0.0
        
        if 'reasoning' not in validated:
            validated['reasoning'] = 'No reasoning provided'
        
        if 'reference_match_found' not in validated:
            validated['reference_match_found'] = False
        
        if 'product_type' not in validated:
            validated['product_type'] = 'Unknown'
        
        return validated
