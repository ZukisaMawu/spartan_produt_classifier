"""
SPARTAN Configuration Settings
"""

# AWS Configuration
AWS_REGIONS = [
    "us-east-1", 
    "us-west-2", 
    "eu-west-1", 
    "eu-central-1", 
    "ap-southeast-1", 
    "ap-northeast-1", 
    "ap-southeast-2"
]

# Model Configuration
MODELS_BY_OPTIMIZATION = {
    "budget": [
        "anthropic.claude-3-haiku-20240307-v1:0",
        "anthropic.claude-3-5-sonnet-20240620-v1:0",
        "anthropic.claude-3-sonnet-20240229-v1:0",
        "anthropic.claude-3-5-sonnet-20241022-v2:0"
    ],
    "performance": [
        "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "anthropic.claude-3-5-sonnet-20240620-v1:0",
        "anthropic.claude-3-sonnet-20240229-v1:0",
        "anthropic.claude-3-haiku-20240307-v1:0"
    ],
    "balanced": [
        "anthropic.claude-3-5-sonnet-20240620-v1:0",
        "anthropic.claude-3-haiku-20240307-v1:0",
        "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "anthropic.claude-3-sonnet-20240229-v1:0"
    ]
}

# Cost Estimation (per item)
COST_PER_ITEM = {
    "budget": 0.0008,
    "balanced": 0.002,
    "performance": 0.004
}

# Cost Mode Information
COST_MODE_INFO = {
    "budget": ("Using Haiku - Maximum cost efficiency"),
    "performance": ("Using Sonnet - Maximum accuracy"),
    "balanced": ("Balanced cost/performance ratio")
}

# Processing Configuration
MAX_RETRIES = 3
MAX_REFERENCE_SAMPLE_SIZE = 500
DEFAULT_MAX_TOKENS = 800
RATE_LIMIT_DELAY = 0.5
ERROR_RATE_LIMIT_DELAY = 1.0

# File Configuration
SUPPORTED_FILE_TYPES = ['csv', 'xlsx']
REQUIRED_COLUMNS = ['description']
OPTIONAL_COLUMNS = ['manufacturer', 'barcode', 'barcode_number', 'ean', 'upc']

# UI Configuration
SPARTAN_THEME = {
    "purple": "#8B5CF6",
    "pink": "#EC4899", 
    "black": "#1F2937",
    "white": "#FFFFFF"
}

# Barcode Configuration
BARCODE_APIS = {
    "upcitemdb": "https://api.upcitemdb.com/prod/trial/lookup?upc=",
    "openfoodfacts": "https://world.openfoodfacts.org/api/v0/product/"
}

API_TIMEOUT = 10  # seconds
