# ⚡ SPARTAN - AI-Powered Item Placement & Classification System

SPARTAN is an intelligent retail item classification system that uses AWS Bedrock (Claude AI) to automatically categorize products into appropriate MCH (Merchandise Category Hierarchy) levels.

## 🌟 Features

- **AI-Powered Classification**: Leverages Claude 3.5 Sonnet/Haiku for intelligent item categorization
- **Barcode Lookup Integration**: Automatic product information retrieval from UPC databases and OpenFoodFacts
- **Reference Database Matching**: Uses historical data to improve accuracy
- **Multi-Level Optimization**: Choose between budget, balanced, or performance modes
- **Batch Processing**: Process multiple items efficiently with progress tracking
- **Cost Estimation**: Real-time cost calculation for processing batches

## 📋 Prerequisites

- Python 3.8 or higher
- AWS Account with Bedrock access
- AWS credentials configured (access key and secret key)
- Bedrock model access enabled for Claude models in your AWS account

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/spartan-app.git
cd spartan-app
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure AWS Credentials

Set up your AWS credentials using one of these methods:

**Option A: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

**Option B: AWS CLI Configuration**
```bash
aws configure
```

**Option C: For Streamlit Cloud**
Add your credentials in the Streamlit Cloud secrets management:
```toml
[default]
AWS_ACCESS_KEY_ID = "your_access_key"
AWS_SECRET_ACCESS_KEY = "your_secret_key"
AWS_DEFAULT_REGION = "us-east-1"
```

### 4. Run the Application

```bash
streamlit run main.py
```

## 📁 Project Structure

```
spartan-app/
├── main.py                 # Main Streamlit application
├── requirements.txt        # Python dependencies
├── config/
│   ├── __init__.py
│   └── settings.py        # Configuration settings
├── core/
│   ├── __init__.py
│   ├── ai_assistant.py    # AI processing engine
│   ├── barcode_lookup.py  # Barcode lookup utilities
│   └── json_parser.py     # JSON parsing utilities
└── utils/
    ├── __init__.py
    ├── aws_utils.py       # AWS Bedrock utilities
    └── ui_helpers.py      # UI helper functions
```

## 📊 Input File Format

SPARTAN requires three CSV/Excel files:

### 1. MCH Bible File
Contains the allowed MCH category levels:
```csv
mch_level
Electronics > Laptops > Gaming
Home & Garden > Furniture > Sofas
...
```

### 2. Reference Data File
Historical categorization data (optional but recommended):
```csv
description,manufacturer,barcode,mch_levels
Product A,Brand X,123456789,Category > Subcategory
...
```

### 3. Items to Process File
Items to be classified:
```csv
description,manufacturer,barcode
New Product,Brand Y,987654321
...
```

**Required Columns**: `description`  
**Optional Columns**: `manufacturer`, `barcode`, `barcode_number`, `ean`, `upc`

## 💰 Cost Optimization Modes

- **Budget Mode**: ~$0.45 per 1,000 items (uses Claude Haiku)
- **Balanced Mode**: ~$2.00 per 1,000 items (mixed models)
- **Performance Mode**: ~$5.40 per 1,000 items (uses Claude Sonnet)

## 🔧 Configuration

Edit `config/settings.py` to customize:
- AWS regions
- Model preferences
- Processing parameters
- Cost estimates
- API endpoints

## 🌐 Deployment to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set up secrets (AWS credentials) in the Streamlit Cloud dashboard
5. Deploy!

### Streamlit Cloud Secrets Format

In your Streamlit Cloud app settings, add:

```toml
AWS_ACCESS_KEY_ID = "your_access_key_here"
AWS_SECRET_ACCESS_KEY = "your_secret_key_here"
AWS_DEFAULT_REGION = "us-east-1"
```

## 🔐 Security Notes

- Never commit AWS credentials to GitHub
- Use environment variables or Streamlit secrets for credentials
- Add `.env` and `secrets.toml` to `.gitignore`
- Regularly rotate your AWS access keys

## 📝 Usage

1. **Test Connection**: Click "Test Connection" in the sidebar to verify AWS Bedrock access
2. **Upload Files**: Upload your MCH Bible, Reference Data, and Items files
3. **Configure Settings**: Select optimization mode and AWS region
4. **Process Items**: Click "PROCESS ITEMS" to start classification
5. **Download Results**: Export results as CSV

## 🛠️ Troubleshooting

**Connection Issues**
- Verify AWS credentials are correctly configured
- Ensure Bedrock service is enabled in your AWS account
- Check that Claude models are enabled in your Bedrock console

**Model Access Errors**
- Request model access in AWS Bedrock console
- Wait for approval (usually instant for Claude models)
- Try a different AWS region

**Rate Limiting**
- SPARTAN includes automatic retry logic
- Reduce batch size if experiencing throttling
- Consider upgrading AWS account limits

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on GitHub.

## ⚠️ Disclaimer

This application uses AWS Bedrock services which incur costs. Monitor your AWS usage and set up billing alerts.
