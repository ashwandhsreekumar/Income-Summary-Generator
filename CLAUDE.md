# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository manages income summary generation for Excel Group of Schools using data exported from ZOHO Books. The system processes student contacts, invoices, and payment data to generate comprehensive income summaries. Excel Group of Schools consists of Excel Central School, Excel Global School and Excel Pathway School. Data for Excel Pathway School will be entered shortly.

## Key Data Files

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

4. **income_summary-template.csv** - Template structure for generating income summaries with columns for:
   - Grade, Section, School
   - Opening Balance, Initial Fee, Month, Term/Monthly Fee

5. **fee_items.csv** - Master list of fee items with:
   - Item codes (SKU) and descriptions
   - Rates per grade level
   - Fee categories (Initial Fee, Term Fee)
   - Grades: Pre-KG, LKG, UKG, Grade 01-12

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
- **Term Fees**: Three terms per year (June, September, January)
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
- Group by Grade and Section
- Calculate Opening Balance from unpaid invoices
- Separate Initial Fee and Term Fee totals
- Format currency values consistently