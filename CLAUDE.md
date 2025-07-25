# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository manages income summary generation for Excel Group of Schools using data exported from ZOHO Books. The system processes student contacts, invoices, and payment data to generate comprehensive income summaries. Excel Group of Schools consists of Excel Central School, Excel Global School and Excel Pathway School. Data for Excel Pathway School will be entered shortly.

## Project Structure

```
Income Summary Generator/
├── CLAUDE.md              # Project guidance for Claude Code
├── README.md              # User documentation
├── data/
│   ├── input/            # Input CSV files from ZOHO Books
│   │   ├── student_contacts.csv
│   │   ├── student_invoices.csv
│   │   └── student_payment.csv
│   ├── reference/        # Reference data
│   │   └── fee_items.csv
│   ├── templates/        # Output templates
│   │   └── income_summary-template.csv
│   └── output/           # Generated reports
├── src/                  # Source code
├── logs/                 # Application logs
└── dist/                 # Compiled executables
```

## Key Data Files

### Input Files (data/input/)
1. **student_contacts.csv** - Student and parent contact information including:
   - Student details (name, grade, section, enrollment info)
   - Parent contact information
   - Custom fields for admission details
   - Key fields: Customer ID, Grade, Section, Display Name
   
2. **student_invoices.csv** - Invoice records containing:
   - Invoice amounts and status
   - Fee types (Initial Academic Fee, Term fees)
   - Customer references linking to student contacts
   - Key fields: Customer ID, Invoice Number, Item Name, Item Total, Balance
   
3. **student_payment.csv** - Payment records tracking:
   - Payment amounts and dates
   - Invoice associations
   - Payment modes
   - Key fields: CustomerID, Invoice Number, Amount, Date
   - Opening Balance: Identified by Invoice Number = "Customer opening balance"

### Reference Files (data/reference/)
4. **fee_items.csv** - Master list of fee items with:
   - Item codes (SKU) and descriptions
   - Rates per grade level
   - Fee categories (Initial Fee, Term Fee, Monthly Fee)
   - Schools: Excel Global School (EGS), Excel Central School (ECS)

### Template Files (data/templates/)
5. **income_summary-template.csv** - Output template with columns:
   - Grade, Section, School
   - Opening Balance, Initial Fee, Month, Term/Monthly Fee

## Data Architecture

### Primary Key Relationships
- **Customer ID**: Links student_contacts → student_invoices → student_payment
- **Invoice Number**: Links student_invoices → student_payment
- **SKU**: Links student_invoices (Item Name) → fee_items for fee categorization

### Data Processing Flow
1. **Student Identification**: Use Customer ID to get student details from student_contacts
2. **Invoice Aggregation**: Group invoices by Customer ID and fee type
3. **Payment Reconciliation**: Match payments to invoices via Invoice Number
4. **Summary Generation**: Aggregate by Grade/Section using the template structure

### Fee Structure
- **Initial Academic Fee**: One-time annual fee (varies by grade)
- **Excel Global School**: Term-based fees (Term I: June, Term II: September, Term III: January)
- **Excel Central School**: Monthly fees (June through March)
- **Excel Pathway School**: Term-based pattern (to be implemented)
- **Discounts**: Applied at entity level, reflected in Item Total calculations

## Technical Implementation Notes

### CSV Processing Requirements
- Parse dates in format: YYYY-MM-DD
- Handle decimal amounts with up to 3 decimal places
- Account for entity-level discounts in invoice calculations
- Consider invoice status (Closed, Paid, etc.) for accurate reporting

### Data Validation Points
- Verify Customer ID exists in contacts before processing invoices
- Check Invoice Number exists before applying payments
- Validate grade/section data consistency across records
- Handle missing or null values appropriately

### Output Format
Generate summaries matching income_summary-template.csv structure:
- Group by Grade, Section, and School
- Month field based on payment date
- Opening Balance: From payments with Invoice Number = "Customer opening balance"
- Initial Fee: Payments allocated to Initial Academic Fee invoices
- Term/Monthly Fee: Payments allocated to term or monthly fee invoices
- All amounts as numeric values (no INR prefix)

## Implementation Plan

### Payment Processing Algorithm
1. **Month Assignment**: Extract month from payment date for all allocations
2. **Opening Balance**: Payments where Invoice Number = "Customer opening balance"
3. **Fee Allocation Priority**:
   - Initial Academic Fee takes priority
   - Then Term/Monthly fees
   - Use InvoicePayment ID to track specific allocations

### Section Naming Conventions
- **Excel Global School**: Blue, Green, Yellow, Red, "-" (single section)
- **Excel Central School**: A, B, C, D
- **Excel Pathway School**: TBD (term-based pattern)

### Windows Application Structure
- GUI with file selectors for input CSVs
- Month/Year filter for report generation
- School filter options
- Progress tracking and error logging
- Output to data/output/ directory

### Error Handling
- Log edge cases to logs/summary_log.txt
- Track missing customer IDs
- Report unmatched payments
- Handle data inconsistencies gracefully

## Technical Stack

### Core Libraries
- **pandas**: Primary data processing and CSV manipulation
- **numpy**: Numerical operations and data aggregation
- **datetime**: Date parsing and month extraction
- **pathlib**: Cross-platform file path handling
- **logging**: Structured error and audit logging

### GUI Framework
- **tkinter**: Built-in Python GUI library (no additional dependencies)
- **tkinter.filedialog**: File selection dialogs
- **tkinter.ttk**: Modern themed widgets

### Data Processing Architecture

```python
# Core data structures using pandas
contacts_df = pd.read_csv('data/input/student_contacts.csv')
invoices_df = pd.read_csv('data/input/student_invoices.csv')
payments_df = pd.read_csv('data/input/student_payment.csv')
fee_items_df = pd.read_csv('data/reference/fee_items.csv')

# Key operations:
# 1. Merge operations using Customer ID
# 2. Group by operations for aggregation
# 3. Pivot tables for summary generation
# 4. Date parsing for month extraction
```

### Performance Considerations
- Use pandas vectorized operations instead of loops
- Implement chunking for large datasets (>100k records)
- Use categorical data types for Grade, Section, School columns
- Memory optimization with appropriate dtypes

### Packaging
- **PyInstaller**: Create standalone Windows executable
- Bundle fee_items.csv as embedded resource
- Include pandas and dependencies in executable
- Target file size: ~50-100MB

### Development Workflow
1. Develop core processing logic in Jupyter notebooks for testing
2. Refactor into modular Python scripts
3. Create GUI wrapper
4. Test with sample data
5. Package as Windows executable