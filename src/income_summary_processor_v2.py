#!/usr/bin/env python3
"""
Income Summary Processor V2 for Excel Group of Schools
Improved version with better payment-invoice linking
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional
import warnings

# Suppress pandas warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IncomeSummaryProcessorV2:
    """Improved processor with accurate payment-invoice linking"""
    
    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path.cwd()
        self.data_path = self.base_path / 'data'
        
        # Initialize dataframes
        self.contacts_df = None
        self.invoices_df = None
        self.payments_df = None
        self.fee_items_df = None
        
        # Create logs directory if it doesn't exist
        (self.base_path / 'logs').mkdir(exist_ok=True)
        
    def load_data(self) -> bool:
        """Load all required CSV files"""
        try:
            logger.info("Loading data files...")
            
            # Load with proper data types to avoid warnings
            dtype_spec = {
                'Customer ID': str,
                'Contact ID': str,
                'CustomerID': str,
                'Invoice Number': str
            }
            
            # Load student contacts
            contacts_path = self.data_path / 'input' / 'student_contacts.csv'
            self.contacts_df = pd.read_csv(contacts_path, encoding='utf-8-sig', dtype=dtype_spec)
            logger.info(f"Loaded {len(self.contacts_df)} student contacts")
            
            # Load invoices with low_memory=False to avoid dtype warnings
            invoices_path = self.data_path / 'input' / 'student_invoices.csv'
            self.invoices_df = pd.read_csv(invoices_path, encoding='utf-8-sig', 
                                          dtype=dtype_spec, low_memory=False)
            logger.info(f"Loaded {len(self.invoices_df)} invoice records")
            
            # Load payments
            payments_path = self.data_path / 'input' / 'student_payment.csv'
            self.payments_df = pd.read_csv(payments_path, encoding='utf-8-sig', dtype=dtype_spec)
            logger.info(f"Loaded {len(self.payments_df)} payment records")
            
            # Load fee items reference
            fee_items_path = self.data_path / 'reference' / 'fee_items.csv'
            self.fee_items_df = pd.read_csv(fee_items_path, encoding='utf-8-sig')
            logger.info(f"Loaded {len(self.fee_items_df)} fee items")
            
            # Convert date columns
            self.payments_df['Date'] = pd.to_datetime(self.payments_df['Date'])
            self.invoices_df['Invoice Date'] = pd.to_datetime(self.invoices_df['Invoice Date'])
            
            # Clean and prepare data
            self._clean_data()
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return False
    
    def _clean_data(self):
        """Clean and prepare data for processing"""
        # Ensure numeric columns are properly typed
        if 'Amount' in self.payments_df.columns:
            self.payments_df['Amount'] = pd.to_numeric(self.payments_df['Amount'], errors='coerce')
        if 'Item Total' in self.invoices_df.columns:
            self.invoices_df['Item Total'] = pd.to_numeric(self.invoices_df['Item Total'], errors='coerce')
        
        # Remove any duplicate entries
        self.payments_df = self.payments_df.drop_duplicates()
        
        # Ensure consistent naming for school field
        if 'School' in self.contacts_df.columns:
            self.contacts_df['School'] = self.contacts_df['School'].fillna('Unknown')
        if 'Location Name' in self.contacts_df.columns and 'School' not in self.contacts_df.columns:
            self.contacts_df['School'] = self.contacts_df['Location Name']
            
    def generate_summary(self, month: Optional[str] = None, year: Optional[int] = None) -> pd.DataFrame:
        """Generate income summary with improved logic"""
        logger.info(f"Generating summary for {month or 'all months'} {year or ''}")
        
        # Initialize summary dictionary
        summary_dict = {}
        
        # Process opening balance payments
        opening_payments = self.payments_df[
            self.payments_df['Invoice Number'] == 'Customer opening balance'
        ].copy()
        
        # Add month and year
        opening_payments['Month'] = opening_payments['Date'].dt.month_name()
        opening_payments['Year'] = opening_payments['Date'].dt.year
        
        # Apply filters
        if month:
            opening_payments = opening_payments[opening_payments['Month'] == month]
        if year:
            opening_payments = opening_payments[opening_payments['Year'] == year]
            
        # Merge with contacts to get student info
        opening_payments = opening_payments.merge(
            self.contacts_df[['Contact ID', 'School', 'Grade', 'Section']],
            left_on='CustomerID',
            right_on='Contact ID',
            how='left'
        )
        
        # Process opening balances
        for _, row in opening_payments.iterrows():
            key = (
                row.get('Grade', 'Unknown'),
                row.get('Section', '-'),
                row.get('School', 'Unknown'),
                row.get('Month', 'Unknown')
            )
            
            if key not in summary_dict:
                summary_dict[key] = {
                    'Opening Balance': 0,
                    'Initial Fee': 0,
                    'Term / Monthly Fee': 0
                }
            
            summary_dict[key]['Opening Balance'] += row.get('Amount', 0)
        
        # Process regular payments
        regular_payments = self.payments_df[
            self.payments_df['Invoice Number'] != 'Customer opening balance'
        ].copy()
        
        # Add month and year
        regular_payments['Month'] = regular_payments['Date'].dt.month_name()
        regular_payments['Year'] = regular_payments['Date'].dt.year
        
        # Apply filters
        if month:
            regular_payments = regular_payments[regular_payments['Month'] == month]
        if year:
            regular_payments = regular_payments[regular_payments['Year'] == year]
        
        # For each payment, we need to find which invoice items it pays for
        for _, payment in regular_payments.iterrows():
            # Get invoice items for this invoice
            invoice_items = self.invoices_df[
                self.invoices_df['Invoice Number'] == payment['Invoice Number']
            ]
            
            if invoice_items.empty:
                logger.warning(f"No invoice found for payment: {payment['Invoice Number']}")
                continue
                
            # Get customer info
            customer_id = invoice_items.iloc[0]['Customer ID']
            customer_info = self.contacts_df[self.contacts_df['Contact ID'] == customer_id]
            
            if customer_info.empty:
                logger.warning(f"No customer found for ID: {customer_id}")
                continue
                
            customer = customer_info.iloc[0]
            
            # Allocate payment proportionally to invoice items
            total_invoice_amount = invoice_items['Item Total'].sum()
            if total_invoice_amount == 0:
                continue
                
            payment_amount = payment['Amount']
            
            # Process each invoice item
            for _, item in invoice_items.iterrows():
                # Calculate proportional payment for this item
                item_proportion = item['Item Total'] / total_invoice_amount
                allocated_amount = payment_amount * item_proportion
                
                # Determine fee type
                item_name = str(item.get('Item Name', '')).lower()
                if 'initial academic fee' in item_name:
                    fee_type = 'Initial Fee'
                elif 'term' in item_name or 'monthly fee' in item_name:
                    fee_type = 'Term / Monthly Fee'
                else:
                    continue  # Skip other fee types
                
                # Create summary key
                key = (
                    customer.get('Grade', 'Unknown'),
                    customer.get('Section', '-'),
                    customer.get('School', 'Unknown'),
                    payment.get('Month', 'Unknown')
                )
                
                if key not in summary_dict:
                    summary_dict[key] = {
                        'Opening Balance': 0,
                        'Initial Fee': 0,
                        'Term / Monthly Fee': 0
                    }
                
                summary_dict[key][fee_type] += allocated_amount
        
        # Convert to DataFrame
        summary_rows = []
        for (grade, section, school, month), amounts in summary_dict.items():
            summary_rows.append({
                'Grade': grade,
                'Section': section if section else '-',
                'School': school,
                'Opening Balance': round(amounts['Opening Balance'], 2),
                'Initial Fee': round(amounts['Initial Fee'], 2),
                'Month': month,
                'Term / Monthly Fee': round(amounts['Term / Monthly Fee'], 2)
            })
        
        summary_df = pd.DataFrame(summary_rows)
        
        # Sort by School, Grade, Section, Month
        if not summary_df.empty:
            summary_df = summary_df.sort_values(['School', 'Grade', 'Section', 'Month'])
        
        logger.info(f"Generated summary with {len(summary_df)} rows")
        
        return summary_df
    
    def save_summary(self, summary_df: pd.DataFrame, filename: str = None) -> Path:
        """Save summary to CSV file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"income_summary_{timestamp}.csv"
        
        output_path = self.data_path / 'output' / filename
        output_path.parent.mkdir(exist_ok=True)
        
        # Save with proper formatting
        summary_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info(f"Summary saved to {output_path}")
        
        return output_path
    
    def generate_monthly_report(self, month: str, year: int) -> pd.DataFrame:
        """Generate report for a specific month"""
        logger.info(f"Generating report for {month} {year}")
        return self.generate_summary(month=month, year=year)


def main():
    """Main execution function"""
    processor = IncomeSummaryProcessorV2()
    
    if not processor.load_data():
        logger.error("Failed to load data")
        return
    
    # Generate summary for all data
    print("\nGenerating complete income summary...")
    summary = processor.generate_summary()
    
    # Save the summary
    output_path = processor.save_summary(summary)
    
    print(f"\n✓ Summary generated successfully!")
    print(f"✓ Output saved to: {output_path}")
    
    # Show summary statistics
    if not summary.empty:
        print(f"\nSummary Statistics:")
        print(f"- Total rows: {len(summary)}")
        print(f"- Schools: {summary['School'].nunique()}")
        print(f"- Grades: {summary['Grade'].nunique()}")
        print(f"- Total Opening Balance: ₹{summary['Opening Balance'].sum():,.2f}")
        print(f"- Total Initial Fee: ₹{summary['Initial Fee'].sum():,.2f}")
        print(f"- Total Term/Monthly Fee: ₹{summary['Term / Monthly Fee'].sum():,.2f}")
        
        print(f"\nSample rows:")
        print(summary.head(10).to_string())


if __name__ == "__main__":
    main()