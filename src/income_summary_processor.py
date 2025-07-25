#!/usr/bin/env python3
"""
Income Summary Processor for Excel Group of Schools
Processes ZOHO Books exports to generate monthly income summaries
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional
import warnings

# Suppress pandas warnings
warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/income_summary.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class IncomeSummaryProcessor:
    """Main processor for generating income summaries from ZOHO Books data"""
    
    def __init__(self, base_path: Path = None):
        """
        Initialize the processor with base path
        
        Args:
            base_path: Base directory path, defaults to current directory
        """
        self.base_path = base_path or Path.cwd()
        self.data_path = self.base_path / 'data'
        
        # Initialize dataframes
        self.contacts_df = None
        self.invoices_df = None
        self.payments_df = None
        self.fee_items_df = None
        
        # Summary data
        self.summary_data = []
        
    def load_data(self) -> bool:
        """
        Load all required CSV files
        
        Returns:
            bool: True if all files loaded successfully
        """
        try:
            logger.info("Loading data files...")
            
            # Load student contacts
            contacts_path = self.data_path / 'input' / 'student_contacts.csv'
            self.contacts_df = pd.read_csv(contacts_path, encoding='utf-8-sig')
            logger.info(f"Loaded {len(self.contacts_df)} student contacts")
            
            # Load invoices
            invoices_path = self.data_path / 'input' / 'student_invoices.csv'
            self.invoices_df = pd.read_csv(invoices_path, encoding='utf-8-sig')
            logger.info(f"Loaded {len(self.invoices_df)} invoice records")
            
            # Load payments
            payments_path = self.data_path / 'input' / 'student_payment.csv'
            self.payments_df = pd.read_csv(payments_path, encoding='utf-8-sig')
            logger.info(f"Loaded {len(self.payments_df)} payment records")
            
            # Load fee items reference
            fee_items_path = self.data_path / 'reference' / 'fee_items.csv'
            self.fee_items_df = pd.read_csv(fee_items_path, encoding='utf-8-sig')
            logger.info(f"Loaded {len(self.fee_items_df)} fee items")
            
            # Convert date columns
            self.payments_df['Date'] = pd.to_datetime(self.payments_df['Date'])
            self.invoices_df['Invoice Date'] = pd.to_datetime(self.invoices_df['Invoice Date'])
            
            # Optimize data types
            self._optimize_dtypes()
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return False
    
    def _optimize_dtypes(self):
        """Optimize data types for memory efficiency"""
        # Convert categorical columns
        if 'School' in self.contacts_df.columns:
            self.contacts_df['School'] = self.contacts_df['School'].astype('category')
        if 'Grade' in self.contacts_df.columns:
            self.contacts_df['Grade'] = self.contacts_df['Grade'].astype('category')
        if 'Section' in self.contacts_df.columns:
            self.contacts_df['Section'] = self.contacts_df['Section'].astype('category')
            
    def process_opening_balances(self, month: Optional[str] = None, year: Optional[int] = None) -> pd.DataFrame:
        """
        Process opening balance payments
        
        Args:
            month: Optional month filter
            year: Optional year filter
            
        Returns:
            DataFrame with opening balance summary
        """
        logger.info("Processing opening balance payments...")
        
        # Filter opening balance payments
        opening_balance_payments = self.payments_df[
            self.payments_df['Invoice Number'] == 'Customer opening balance'
        ].copy()
        
        # Add month and year columns
        opening_balance_payments['Month'] = opening_balance_payments['Date'].dt.month_name()
        opening_balance_payments['Year'] = opening_balance_payments['Date'].dt.year
        
        # Apply filters if provided
        if month:
            opening_balance_payments = opening_balance_payments[
                opening_balance_payments['Month'] == month
            ]
        if year:
            opening_balance_payments = opening_balance_payments[
                opening_balance_payments['Year'] == year
            ]
        
        # Merge with customer data to get grade, section, school
        opening_balance_summary = opening_balance_payments.merge(
            self.contacts_df[['Contact ID', 'School', 'Grade', 'Section', 'Display Name']],
            left_on='CustomerID',
            right_on='Contact ID',
            how='left'
        )
        
        logger.info(f"Found {len(opening_balance_summary)} opening balance payments")
        
        return opening_balance_summary
    
    def process_fee_payments(self, month: Optional[str] = None, year: Optional[int] = None) -> pd.DataFrame:
        """
        Process regular fee payments (Initial and Term/Monthly fees)
        
        Args:
            month: Optional month filter
            year: Optional year filter
            
        Returns:
            DataFrame with fee payment details
        """
        logger.info("Processing fee payments...")
        
        # Filter out opening balance payments
        fee_payments = self.payments_df[
            self.payments_df['Invoice Number'] != 'Customer opening balance'
        ].copy()
        
        # Add month and year columns
        fee_payments['Month'] = fee_payments['Date'].dt.month_name()
        fee_payments['Year'] = fee_payments['Date'].dt.year
        
        # Apply filters if provided
        if month:
            fee_payments = fee_payments[fee_payments['Month'] == month]
        if year:
            fee_payments = fee_payments[fee_payments['Year'] == year]
        
        # Merge with invoice data to get fee details
        fee_payment_details = fee_payments.merge(
            self.invoices_df[['Invoice Number', 'Customer ID', 'Item Name', 'Item Total']],
            on='Invoice Number',
            how='left'
        )
        
        # Categorize fees
        fee_payment_details['Fee Type'] = fee_payment_details['Item Name'].apply(self._categorize_fee)
        
        # Merge with customer data
        fee_payment_summary = fee_payment_details.merge(
            self.contacts_df[['Contact ID', 'School', 'Grade', 'Section', 'Display Name']],
            left_on='Customer ID',
            right_on='Contact ID',
            how='left'
        )
        
        logger.info(f"Processed {len(fee_payment_summary)} fee payments")
        
        return fee_payment_summary
    
    def _categorize_fee(self, item_name: str) -> str:
        """
        Categorize fee based on item name
        
        Args:
            item_name: Name of the fee item
            
        Returns:
            Fee category: 'Initial Fee' or 'Term/Monthly Fee'
        """
        if pd.isna(item_name):
            return 'Unknown'
        
        item_name_lower = str(item_name).lower()
        
        if 'initial academic fee' in item_name_lower:
            return 'Initial Fee'
        elif 'term' in item_name_lower or 'monthly fee' in item_name_lower:
            return 'Term/Monthly Fee'
        else:
            return 'Other'
    
    def generate_summary(self, month: Optional[str] = None, year: Optional[int] = None) -> pd.DataFrame:
        """
        Generate the income summary report
        
        Args:
            month: Optional month filter
            year: Optional year filter
            
        Returns:
            DataFrame matching the template structure
        """
        logger.info(f"Generating summary for {month or 'all months'} {year or 'all years'}")
        
        # Process different payment types
        opening_balances = self.process_opening_balances(month, year)
        fee_payments = self.process_fee_payments(month, year)
        
        # Initialize summary structure
        summary_dict = {}
        
        # Process opening balances
        for _, payment in opening_balances.iterrows():
            key = (
                payment.get('Grade', 'Unknown'),
                payment.get('Section', 'Unknown'),
                payment.get('School', 'Unknown'),
                payment.get('Month', 'Unknown')
            )
            
            if key not in summary_dict:
                summary_dict[key] = {
                    'Opening Balance': 0,
                    'Initial Fee': 0,
                    'Term / Monthly Fee': 0
                }
            
            summary_dict[key]['Opening Balance'] += payment.get('Amount', 0)
        
        # Process fee payments
        for _, payment in fee_payments.iterrows():
            key = (
                payment.get('Grade', 'Unknown'),
                payment.get('Section', 'Unknown'), 
                payment.get('School', 'Unknown'),
                payment.get('Month', 'Unknown')
            )
            
            if key not in summary_dict:
                summary_dict[key] = {
                    'Opening Balance': 0,
                    'Initial Fee': 0,
                    'Term / Monthly Fee': 0
                }
            
            fee_type = payment.get('Fee Type', 'Other')
            amount = payment.get('Amount Applied to Invoice', 0)
            
            if fee_type == 'Initial Fee':
                summary_dict[key]['Initial Fee'] += amount
            elif fee_type == 'Term/Monthly Fee':
                summary_dict[key]['Term / Monthly Fee'] += amount
        
        # Convert to DataFrame
        summary_rows = []
        for (grade, section, school, month), amounts in summary_dict.items():
            summary_rows.append({
                'Grade': grade,
                'Section': section,
                'School': school,
                'Opening Balance': amounts['Opening Balance'],
                'Initial Fee': amounts['Initial Fee'],
                'Month': month,
                'Term / Monthly Fee': amounts['Term / Monthly Fee']
            })
        
        summary_df = pd.DataFrame(summary_rows)
        
        # Sort by School, Grade, Section, Month
        summary_df = summary_df.sort_values(['School', 'Grade', 'Section', 'Month'])
        
        logger.info(f"Generated summary with {len(summary_df)} rows")
        
        return summary_df
    
    def save_summary(self, summary_df: pd.DataFrame, filename: str = None):
        """
        Save summary to CSV file
        
        Args:
            summary_df: Summary DataFrame
            filename: Output filename (optional)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"income_summary_{timestamp}.csv"
        
        output_path = self.data_path / 'output' / filename
        
        # Ensure output directory exists
        output_path.parent.mkdir(exist_ok=True)
        
        # Save to CSV
        summary_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info(f"Summary saved to {output_path}")
        
        return output_path


def main():
    """Main execution function"""
    # Create processor instance
    processor = IncomeSummaryProcessor()
    
    # Load data
    if not processor.load_data():
        logger.error("Failed to load data files")
        return
    
    # Generate summary for current month
    current_month = datetime.now().strftime("%B")
    current_year = datetime.now().year
    
    summary_df = processor.generate_summary()  # Generate for all months initially
    
    # Save summary
    output_path = processor.save_summary(summary_df)
    
    print(f"\nSummary generated successfully!")
    print(f"Output saved to: {output_path}")
    print(f"\nSummary preview:")
    print(summary_df.head(10))


if __name__ == "__main__":
    main()