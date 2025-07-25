# 📊 Income Summary Generator

> **Streamline your school's financial reporting with automated income summary generation from ZOHO Books exports**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🌟 Overview

The **Income Summary Generator** is a powerful tool designed for Excel Group of Schools to automate the generation of monthly income summaries from ZOHO Books data. It processes student contacts, invoices, and payment records to create comprehensive financial reports with just a few clicks.

### ✨ Key Features

- 📤 **Easy Data Upload** - Drag and drop CSV files directly from ZOHO Books
- 🔍 **Smart Filtering** - Filter by month, year, and school
- 📊 **Visual Analytics** - Interactive charts and graphs for data visualization
- 💾 **Export Ready** - Download summaries as CSV for further analysis
- 🌐 **Web-Based** - Access from any device with a browser
- 🚀 **Fast Processing** - Handle thousands of records in seconds

## 🖥️ Live Demo

Try the live web application: [Income Summary Generator](https://your-app-name.streamlit.app)

## 📸 Screenshots

### Main Interface
<img src="https://via.placeholder.com/800x400?text=Income+Summary+Generator+Interface" alt="Main Interface" />

### Data Visualization
<img src="https://via.placeholder.com/800x400?text=Charts+and+Analytics" alt="Charts" />

## 🛠️ Installation & Setup

### Option 1: Use the Web App (Recommended)
No installation required! Simply visit the [web application](https://your-app-name.streamlit.app) and start using it immediately.

### Option 2: Run Locally

#### Prerequisites
- Python 3.8 or higher
- Git

#### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/income-summary-generator.git
   cd income-summary-generator
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Activate on Windows
   venv\Scripts\activate
   
   # Activate on macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   
   **For Web Interface (Streamlit):**
   ```bash
   streamlit run streamlit_app.py
   ```
   
   **For Command Line Interface:**
   ```bash
   python src/income_summary_cli.py
   ```

### Option 3: Desktop Application

#### Windows
1. Download the latest release from [Releases](https://github.com/yourusername/income-summary-generator/releases)
2. Extract `IncomeSummaryGenerator.exe`
3. Double-click to run (no installation needed)

#### macOS
1. Download `IncomeSummaryGenerator.app` from [Releases](https://github.com/yourusername/income-summary-generator/releases)
2. Drag to Applications folder
3. Right-click and select "Open" on first launch

## 📁 Required Data Files

The application requires three CSV files exported from ZOHO Books:

1. **`student_contacts.csv`** - Student and parent information
   - Contains: Student names, grades, sections, contact details
   
2. **`student_invoices.csv`** - Invoice records
   - Contains: Invoice numbers, amounts, fee types, dates
   
3. **`student_payment.csv`** - Payment records
   - Contains: Payment amounts, dates, invoice references

### Data File Structure

```
data/
├── input/
│   ├── student_contacts.csv
│   ├── student_invoices.csv
│   └── student_payment.csv
├── reference/
│   └── fee_items.csv
└── output/
    └── (generated summaries)
```

## 🚀 Usage Guide

### Using the Web App

1. **Upload Files**
   - Click on the file upload areas
   - Select your CSV files from ZOHO Books
   - Files are automatically validated

2. **Configure Options**
   - Select Month (or "All Months")
   - Select Year (or "All Years")
   - Choose School filter if needed

3. **Generate Summary**
   - Click "🚀 Generate Income Summary"
   - View real-time progress
   - See summary statistics instantly

4. **Analyze Results**
   - Review the data table
   - Explore interactive charts
   - Check different analysis tabs

5. **Download Report**
   - Click "📥 Download Summary as CSV"
   - File is saved with timestamp

### Understanding the Output

The summary includes:
- **Grade** - Student grade level
- **Section** - Class section
- **School** - School name
- **Opening Balance** - Carried forward amounts
- **Initial Fee** - One-time admission/annual fees
- **Month** - Payment month
- **Term/Monthly Fee** - Regular fee payments

## 📊 Features in Detail

### Data Processing
- Automatic payment categorization
- Proportional allocation for partial payments
- Smart date parsing and month extraction
- Duplicate detection and handling

### Visualizations
- 📊 **School Comparison** - Bar charts comparing schools
- 📈 **Grade Analysis** - Grade-wise collection breakdown
- 📅 **Monthly Trends** - Line charts for time analysis
- 🥧 **Distribution** - Pie charts for fee proportions

### Filters & Options
- Month selection (individual or all)
- Year filtering
- School-specific reports
- Export with custom filenames

## 🏗️ Project Structure

```
income-summary-generator/
├── streamlit_app.py          # Web application
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── src/
│   ├── income_summary_processor_v2.py    # Core processing logic
│   ├── income_summary_cli.py             # CLI interface
│   └── income_summary_gui.py             # Desktop GUI
├── data/
│   ├── input/               # Input CSV files
│   ├── reference/           # Reference data
│   └── output/              # Generated reports
└── README.md               # This file
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🐛 Troubleshooting

### Common Issues

**"File upload failed"**
- Ensure CSV files are properly formatted
- Check file encoding (should be UTF-8)
- Verify column names match expected format

**"No data generated"**
- Confirm payment dates are within selected range
- Check if invoices have corresponding payments
- Verify customer IDs match across files

**Performance issues**
- For large files (>50MB), processing may take longer
- Consider filtering by specific month/year
- Use Chrome or Firefox for best performance

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Excel Group IT Team** - *Initial development*
- **Contributors** - See [contributors](https://github.com/yourusername/income-summary-generator/contributors)

## 🙏 Acknowledgments

- Excel Group of Schools for requirements and testing
- ZOHO Books for data export capabilities
- Streamlit for the amazing web framework

## 📞 Support

For support, please contact:
- Email: it@excelschools.edu.in
- Issues: [GitHub Issues](https://github.com/yourusername/income-summary-generator/issues)

---

<p align="center">
  Made with ❤️ for Excel Group of Schools
</p>
