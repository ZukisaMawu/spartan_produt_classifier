# ⚡ SPARTAN - AI-Powered Item Classification System (Simplified)

SPARTAN is an intelligent retail item classification system that uses AWS Bedrock (Claude AI) to automatically categorize products into appropriate MCH (Merchandise Category Hierarchy) levels.

## 🌟 Key Features

- **Simplified Workflow**: Just upload your items file and go! 🚀
- **Pre-loaded Data**: MCH Bible and reference data are built-in
- **AI-Powered Classification**: Leverages Claude 3.5 Sonnet/Haiku
- **Barcode Lookup Integration**: Automatic product information retrieval
- **Works Without Reference Data**: Can run on AI alone or with reference matching
- **Multi-Level Optimization**: Choose between budget, balanced, or performance modes
- **Batch Processing**: Process multiple items efficiently
- **Cost Estimation**: Real-time cost calculation

## 📋 Prerequisites

- Python 3.8 or higher
- AWS Account with Bedrock access
- AWS credentials configured (access key and secret key)
- Bedrock model access enabled for Claude models

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

**For Streamlit Cloud** (Add in Streamlit secrets):
```toml
AWS_ACCESS_KEY_ID = "your_access_key"
AWS_SECRET_ACCESS_KEY = "your_secret_key"
AWS_DEFAULT_REGION = "us-east-1"
```

**For Local Development**:
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

### 4. Run the Application

```bash
streamlit run main.py
```

## 📁 Project Structure

```
spartan-app/
├── main.py                 # Main Streamlit application (SIMPLIFIED!)
├── requirements.txt        # Python dependencies
├── data/                   # Built-in data files
│   ├── mch_bible.csv      # Pre-loaded MCH categories (80+ levels)
│   └── reference_data.csv # Pre-loaded reference items (40+ examples)
├── config/
│   └── settings.py        # Configuration settings
├── core/
│   ├── ai_assistant.py    # AI processing engine
│   ├── barcode_lookup.py  # Barcode lookup utilities
│   └── json_parser.py     # JSON parsing utilities
└── utils/
    ├── aws_utils.py       # AWS Bedrock utilities
    └── ui_helpers.py      # UI helper functions
```

## 📊 How It Works

### Simple 3-Step Process:

1. **Upload Your Items File** (CSV or Excel)
   - Required: `description` column
   - Optional: `manufacturer`, `barcode`, `barcode_number`, `ean`, `upc`

2. **Click Process**
   - SPARTAN loads built-in MCH Bible (80+ categories)
   - Optionally uses reference database (40+ examples)
   - AI analyzes each item
   - Returns classification with confidence scores

3. **Download Results**
   - Get CSV with all classifications
   - View detailed reasoning
   - See confidence scores

### Example Input File

```csv
description,manufacturer,barcode
Dell XPS Gaming Laptop,Dell,1111111111
Samsung Galaxy S23,Samsung,2222222222
Harry Potter Book Set,Scholastic,9780545162074
```

### Example Output

```csv
description,mch_levels,confidence_score,reasoning
Dell XPS Gaming Laptop,Electronics > Laptops > Gaming,0.95,Gaming laptop identified...
Samsung Galaxy S23,Electronics > Smartphones > Android,0.98,Samsung Android device...
Harry Potter Book Set,Books > Fiction > Science Fiction,0.92,ISBN detected, book series...
```

## 💰 Cost Optimization Modes

- **Budget Mode**: ~$0.45 per 1,000 items (uses Claude Haiku)
- **Balanced Mode**: ~$2.00 per 1,000 items (mixed models)
- **Performance Mode**: ~$5.40 per 1,000 items (uses Claude Sonnet)

## 🔧 Built-in Data

### MCH Bible (80+ Categories)
Pre-loaded categories include:
- Electronics (Laptops, Smartphones, Tablets, Accessories)
- Books (Fiction, Non-Fiction, Children)
- Home & Garden (Furniture, Kitchen, Decor)
- Clothing (Men, Women, Children)
- Food & Beverage (Deli, Grab&Go, Bakery)
- Toys (Action Figures, Board Games, Educational)
- Health & Beauty (Skincare, Makeup, Haircare)
- Sports (Fitness, Outdoor, Team Sports)
- And more!

### Reference Database (40+ Examples)
Pre-populated with common items to improve accuracy:
- Consumer electronics
- Books and media
- Furniture and home goods
- Food items (sandwiches, drinks, baked goods)
- Toys and games
- Health and beauty products
- Sports equipment
- And more!

## 🌐 Deployment to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set main file: `main.py`
5. Add AWS credentials in Streamlit secrets
6. Deploy!

**Important**: The `data/` folder must be included in your repository!

## 📝 Usage

1. **Test Connection**: Click "Test Connection" in sidebar
2. **Check Data Status**: Verify MCH Bible and Reference Data loaded
3. **Upload Items**: Upload your CSV/Excel file
4. **Configure Settings**: Select optimization mode
5. **Process Items**: Click "PROCESS ITEMS"
6. **Download Results**: Export as CSV

## 🛠️ Customizing Built-in Data

### Update MCH Bible

Edit `data/mch_bible.csv`:
```csv
mch_level
Your > Custom > Category
Another > Category > Path
```

### Update Reference Data

Edit `data/reference_data.csv`:
```csv
description,manufacturer,barcode,mch_levels
Your Product,Brand,123456,Your > Custom > Category
```

## 🔐 Security Notes

- Never commit AWS credentials to GitHub
- Use environment variables or Streamlit secrets
- Add `.env` and `secrets.toml` to `.gitignore`
- Regularly rotate your AWS access keys

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚠️ Important Notes

### Data Files Required
The `data/` directory with `mch_bible.csv` and `reference_data.csv` must be present in your deployment. These files are included in the repository.

### Reference Data is Optional
The app will work without reference data, relying entirely on AI classification. However, having reference data significantly improves accuracy for similar items.

### Adding Your Own Data
You can customize the built-in data files to match your specific business needs. Just edit the CSV files in the `data/` folder.

## 🎉 What's New in This Version

- ✅ **Simplified UI**: Only one file upload needed
- ✅ **Pre-loaded Data**: MCH Bible and reference data built-in
- ✅ **Optional Reference**: Works with or without reference database
- ✅ **Easier Deployment**: Fewer files to manage
- ✅ **Better UX**: Clearer status indicators and data previews

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

**Ready to classify at lightning speed?** ⚡

Upload your items file and let SPARTAN do the work!
