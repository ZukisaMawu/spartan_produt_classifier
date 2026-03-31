"""
Barcode Product Lookup System for SPARTAN
"""

import requests
from typing import Dict
from config.settings import BARCODE_APIS, API_TIMEOUT
import streamlit as st


class BarcodeProductLookup:
    """Enhanced barcode lookup with multiple services"""
    
    def __init__(self):
        self.timeout = API_TIMEOUT
    
    def lookup_barcode(self, barcode: str) -> Dict:
        """Try multiple services to lookup barcode information"""
        if not barcode or len(barcode) < 8:
            return {"found": False, "source": "invalid_barcode"}
        
        # Try UPC Database API first
        upc_result = self._try_upcitemdb(barcode)
        if upc_result["found"]:
            return upc_result
        
        # Try OpenFoodFacts for food items
        food_result = self._try_openfoodfacts(barcode)
        if food_result["found"]:
            return food_result
        
        return {"found": False, "source": "not_found"}
    
    def _try_upcitemdb(self, barcode: str) -> Dict:
        """Try UPC Database API (free tier available)"""
        try:
            url = f"{BARCODE_APIS['upcitemdb']}{barcode}"
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('items') and len(data['items']) > 0:
                    item = data['items'][0]
                    return {
                        "found": True,
                        "source": "upcitemdb",
                        "title": item.get('title', ''),
                        "brand": item.get('brand', ''),
                        "category": item.get('category', ''),
                        "description": item.get('description', ''),
                        "raw_data": item
                    }
        except Exception as e:
            st.warning(f"UPC lookup failed: {str(e)}")
        
        return {"found": False, "source": "upcitemdb_failed"}
    
    def _try_openfoodfacts(self, barcode: str) -> Dict:
        """Try OpenFoodFacts for food items"""
        try:
            url = f"{BARCODE_APIS['openfoodfacts']}{barcode}.json"
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 1 and data.get('product'):
                    product = data['product']
                    return {
                        "found": True,
                        "source": "openfoodfacts",
                        "title": product.get('product_name', ''),
                        "brand": product.get('brands', ''),
                        "category": product.get('categories', ''),
                        "description": f"{product.get('product_name', '')} {product.get('generic_name', '')}".strip(),
                        "raw_data": product
                    }
        except Exception as e:
            st.warning(f"OpenFoodFacts lookup failed: {str(e)}")
        
        return {"found": False, "source": "openfoodfacts_failed"}
    
    @staticmethod
    def analyze_barcode_type(barcode: str) -> Dict:
        """Analyze barcode type and characteristics"""
        barcode_info = {
            "type": "unknown",
            "is_book": False,
            "is_inhouse": False,
            "analysis": ""
        }
        
        if not barcode:
            return barcode_info
        
        # Clean barcode
        barcode = str(barcode).strip()
        
        # Determine barcode type
        if barcode.startswith(('978', '979')) and len(barcode) >= 10:
            barcode_info.update({
                "type": "ISBN (Book)",
                "is_book": True,
                "analysis": "Book product - ISBN format detected"
            })
        elif barcode.startswith('2') and len(barcode) < 10:
            barcode_info.update({
                "type": "In-house product",
                "is_inhouse": True,
                "analysis": "Internal/in-house product - focus on description"
            })
        elif len(barcode) in [12, 13]:
            barcode_info.update({
                "type": "EAN/UPC",
                "analysis": "Standard retail product barcode"
            })
        elif len(barcode) == 8:
            barcode_info.update({
                "type": "EAN-8",
                "analysis": "Short European Article Number"
            })
        else:
            barcode_info.update({
                "analysis": f"Unknown barcode format (length: {len(barcode)})"
            })
        
        return barcode_info
