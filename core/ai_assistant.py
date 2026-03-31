"""
SPARTAN AI Assistant - Main AI processing engine
"""

import boto3
import json
import time
import pandas as pd
from typing import Dict, Optional, Callable
import streamlit as st

from config.settings import (
    MODELS_BY_OPTIMIZATION, MAX_RETRIES, MAX_REFERENCE_SAMPLE_SIZE,
    DEFAULT_MAX_TOKENS, RATE_LIMIT_DELAY, ERROR_RATE_LIMIT_DELAY
)
from core.barcode_lookup import BarcodeProductLookup
from core.json_parser import EnhancedJSONParser


class ItemPlacementAI:
    """SPARTAN AI Assistant for item placement and classification"""
    
    def __init__(self, region_name: str = "us-east-1", model_id: str = None, cost_optimization: str = "balanced"):
        """Initialize the AI assistant with AWS Bedrock client"""
        try:
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=region_name
            )
            
            # Set model priority based on cost optimization
            self.available_models = MODELS_BY_OPTIMIZATION[cost_optimization]
            self.model_id = model_id if model_id else self.available_models[0]
            self.cost_optimization = cost_optimization
            
            # Initialize components
            self.bible_df = None
            self.reference_df = None
            self.region = region_name
            self.barcode_lookup = BarcodeProductLookup()
            self.json_parser = EnhancedJSONParser()
            
        except Exception as e:
            st.error(f"Failed to initialize AWS Bedrock client: {e}")
            raise e
    
    def load_bible(self, bible_data: pd.DataFrame) -> None:
        """Load the MCH levels bible data"""
        self.bible_df = bible_data
        
    def load_reference_file(self, reference_data: pd.DataFrame) -> None:
        """Load the historical reference data"""
        self.reference_df = reference_data
    
    def analyze_barcode(self, barcode: str) -> Dict:
        """Enhanced barcode analysis with online lookup"""
        # Get barcode type analysis
        barcode_info = self.barcode_lookup.analyze_barcode_type(barcode)
        
        # Try online lookup for non-inhouse products
        if not barcode_info["is_inhouse"] and barcode:
            lookup_result = self.barcode_lookup.lookup_barcode(barcode)
            barcode_info["lookup_result"] = lookup_result
        else:
            barcode_info["lookup_result"] = {"found": False, "source": "skipped_inhouse"}
        
        return barcode_info
    
    def create_placement_prompt(self, item_description: str, manufacturer: str = "", barcode: str = "") -> str:
        """Create the detailed prompt for AI classification"""
        bible_categories = self.bible_df.to_string(index=False) if self.bible_df is not None else "No bible loaded"
        
        # Analyze barcode first
        barcode_analysis = self.analyze_barcode(barcode) if barcode else None
        
        # Build enhanced product information
        product_info_parts = [f"Description: {item_description}"]
        
        if manufacturer:
            product_info_parts.append(f"Manufacturer: {manufacturer}")
        
        if barcode:
            product_info_parts.append(f"Barcode: {barcode}")
            
        if barcode_analysis:
            product_info_parts.append(f"Barcode Type: {barcode_analysis['type']}")
            product_info_parts.append(f"Analysis: {barcode_analysis['analysis']}")
            
            if barcode_analysis.get("lookup_result", {}).get("found"):
                lookup = barcode_analysis["lookup_result"]
                product_info_parts.extend([
                    f"Online Lookup: SUCCESS",
                    f"Product Name: {lookup.get('title', 'N/A')}",
                    f"Brand: {lookup.get('brand', 'N/A')}",
                    f"Category: {lookup.get('category', 'N/A')}",
                    f"Source: {lookup.get('source', 'N/A')}"
                ])
            else:
                product_info_parts.append("Online Lookup: NOT FOUND")
        
        product_info = "\\n".join(product_info_parts)
        
        # Include reference data sample (if available)
        reference_data = ""
        reference_available = False
        if self.reference_df is not None and len(self.reference_df) > 0:
            sample_size = min(MAX_REFERENCE_SAMPLE_SIZE, len(self.reference_df))
            reference_sample = self.reference_df.head(sample_size)
            reference_data = reference_sample.to_string(index=False)
            reference_available = True
        
        prompt = f"""You are SPARTAN AI - a precise retail categorizer for South African stores. You have access to a bible of allowed MCH levels{' and a reference database of previously categorized items' if reference_available else ''}.

=== BIBLE STRUCTURE (ONLY ALLOWED MCH LEVELS) ===
{bible_categories}

{f'''=== REFERENCE DATABASE (PREVIOUSLY CATEGORIZED ITEMS) ===
{reference_data}
''' if reference_available else '=== NOTE: NO REFERENCE DATABASE AVAILABLE ===
You will need to rely entirely on the product information and your understanding to classify items.
'}

=== ITEM TO CATEGORIZE ===
{product_info}

=== SPARTAN CLASSIFICATION PROTOCOL ===

1. PRIORITY 1 - BARCODE LOOKUP VERIFICATION:
   - If online lookup found product info, verify it matches the description
   - If conflict exists, note this in reasoning and prioritize description
   - Use lookup data to enhance understanding of product type
   - Food items are sold at the in store Deli. this may include cooked food, pastries, sandwiches, etc. Check description and 
     place accordingly with MCH in deli category name or 'grab&go' product class name in the mch levels.

{f'''2. PRIORITY 2 - REFERENCE DATABASE MATCHING:
   - Search for IDENTICAL or VERY SIMILAR descriptions
   - If exact match found, copy the MCH levels classification exactly
   - Prioritize exact matches over partial matches
''' if reference_available else '2. PRIORITY 2 - DIRECT ANALYSIS:
   - No reference database available
   - Analyze product type from description and available information
   - Match to appropriate MCH level based on product characteristics
'}

3. PRIORITY 3 - BARCODE TYPE ANALYSIS:
   - ISBN (978/979 + 10+ digits) = Books → Look for book categories
   - In-house (starts with 2, <10 digits) = Use description only
   - Standard barcodes = Use all available information

4. PRIORITY 4 - MCH CLASSIFICATION:
   - ONLY use MCH levels that exist EXACTLY in the bible
   - If no appropriate match, use "UNCERTAIN"
   - NEVER create or modify MCH levels

5. VALIDATION:
   - Double-check selected MCH levels exists in bible
   - Ensure reasoning includes all decision factors

=== RESPONSE FORMAT (VALID JSON ONLY) ===
{{
    "mch_levels": "EXACT_MCH_LEVELS_FROM_BIBLE_OR_UNCERTAIN",
    "confidence_score": 0.95,
    "reference_match_found": {'true' if reference_available else 'false'},
    "product_type": "Brief product description",
    "barcode_lookup_used": true,
    "reasoning": "Detailed explanation including barcode analysis{'and reference matching' if reference_available else ''}"
}}

CRITICAL: Response must be valid JSON only. Use exact MCH levels from bible. Include all analysis in reasoning."""
        
        return prompt
    
    def categorize_item(self, item_description: str, manufacturer: str = "", barcode: str = "") -> Dict:
        """Categorize a single item with retry logic"""
        for attempt in range(MAX_RETRIES):
            try:
                prompt = self.create_placement_prompt(item_description, manufacturer, barcode)
                
                body = json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": DEFAULT_MAX_TOKENS,
                    "temperature": 0.0,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                })
                
                response = self.bedrock_client.invoke_model(
                    modelId=self.model_id,
                    body=body
                )
                
                response_body = json.loads(response['body'].read())
                claude_response = response_body['content'][0]['text']
                
                # Parse response using enhanced parser
                result = self.json_parser.clean_and_parse(claude_response)
                result = self.json_parser.validate_result(result)
                
                result['status'] = 'success'
                result['attempt'] = attempt + 1
                return result
                
            except Exception as e:
                error_msg = str(e)
                
                # Handle throttling with exponential backoff
                if "ThrottlingException" in error_msg or "Too many requests" in error_msg:
                    wait_time = (attempt + 1) * 2
                    time.sleep(wait_time)
                    continue
                
                # If last attempt, return error
                if attempt == MAX_RETRIES - 1:
                    return {
                        "mch_levels": "API_ERROR",
                        "confidence_score": 0.0,
                        "reference_match_found": False,
                        "reasoning": f"API Error after {MAX_RETRIES} attempts: {error_msg}",
                        "status": "error",
                        "attempt": attempt + 1
                    }
        
        return {
            "mch_levels": "MAX_RETRIES_EXCEEDED",
            "confidence_score": 0.0,
            "reference_match_found": False,
            "reasoning": "Maximum retry attempts exceeded",
            "status": "error"
        }
    
    def process_batch(self, items_df: pd.DataFrame, progress_callback: Optional[Callable] = None) -> pd.DataFrame:
        """Process a batch of items"""
        results = []
        total_items = len(items_df)
        
        for idx, row in items_df.iterrows():
            if progress_callback:
                progress_callback(idx + 1, total_items)
            
            # Extract item data
            item_desc = row.get('description', '')
            manufacturer = row.get('manufacturer', '')
            barcode = str(row.get('barcode', '') or row.get('barcode_number', '') or 
                         row.get('ean', '') or row.get('upc', '') or '').strip()
            
            # Process item
            result = self.categorize_item(item_desc, manufacturer, barcode)
            
            # Get barcode analysis for additional info
            barcode_analysis = self.analyze_barcode(barcode) if barcode else {}
            
            # Build result row
            result_row = {
                'original_description': item_desc,
                'original_manufacturer': manufacturer,
                'original_barcode': barcode,
                'barcode_type': barcode_analysis.get('type', 'N/A'),
                'online_lookup_found': barcode_analysis.get('lookup_result', {}).get('found', False),
                'lookup_product_name': barcode_analysis.get('lookup_result', {}).get('title', ''),
                'mch_levels': result['mch_levels'],
                'confidence_score': result['confidence_score'],
                'reference_match_found': result.get('reference_match_found', False),
                'product_type': result.get('product_type', 'Unknown'),
                'reasoning': result.get('reasoning', 'NO REASONING PROVIDED'),
                'status': result['status'],
                'attempts': result.get('attempt', 1)
            }
            
            results.append(result_row)
            
            # Dynamic rate limiting
            if result['status'] == 'success':
                time.sleep(RATE_LIMIT_DELAY)
            else:
                time.sleep(ERROR_RATE_LIMIT_DELAY)
        
        return pd.DataFrame(results)
