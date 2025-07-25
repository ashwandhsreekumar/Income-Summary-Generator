#!/usr/bin/env python3
"""
Test script for Income Summary Processor
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.income_summary_processor import IncomeSummaryProcessor
import pandas as pd

def test_data_loading():
    """Test if data files load correctly"""
    print("Testing data loading...")
    processor = IncomeSummaryProcessor(base_path=Path(__file__).parent.parent)
    
    if processor.load_data():
        print("✓ Data loaded successfully")
        print(f"  - Contacts: {len(processor.contacts_df)} records")
        print(f"  - Invoices: {len(processor.invoices_df)} records")
        print(f"  - Payments: {len(processor.payments_df)} records")
        print(f"  - Fee Items: {len(processor.fee_items_df)} records")
        return True
    else:
        print("✗ Failed to load data")
        return False

def test_opening_balances():
    """Test opening balance processing"""
    print("\nTesting opening balance processing...")
    processor = IncomeSummaryProcessor(base_path=Path(__file__).parent.parent)
    processor.load_data()
    
    opening_balances = processor.process_opening_balances()
    print(f"✓ Found {len(opening_balances)} opening balance payments")
    
    if len(opening_balances) > 0:
        print("\nSample opening balance payments:")
        print(opening_balances[['Display Name', 'Amount', 'Month', 'School', 'Grade', 'Section']].head())
    
    return True

def test_fee_payments():
    """Test fee payment processing"""
    print("\nTesting fee payment processing...")
    processor = IncomeSummaryProcessor(base_path=Path(__file__).parent.parent)
    processor.load_data()
    
    fee_payments = processor.process_fee_payments()
    print(f"✓ Found {len(fee_payments)} fee payments")
    
    # Check fee categorization
    fee_type_counts = fee_payments['Fee Type'].value_counts()
    print("\nFee type distribution:")
    print(fee_type_counts)
    
    return True

def test_summary_generation():
    """Test summary generation"""
    print("\nTesting summary generation...")
    processor = IncomeSummaryProcessor(base_path=Path(__file__).parent.parent)
    processor.load_data()
    
    # Generate summary for May 2025 as a test
    summary = processor.generate_summary(month='May', year=2025)
    print(f"✓ Generated summary with {len(summary)} rows")
    
    if len(summary) > 0:
        print("\nSample summary rows:")
        print(summary.head())
        
        # Check totals
        print("\nSummary totals:")
        print(f"Total Opening Balance: ₹{summary['Opening Balance'].sum():,.2f}")
        print(f"Total Initial Fee: ₹{summary['Initial Fee'].sum():,.2f}")
        print(f"Total Term/Monthly Fee: ₹{summary['Term / Monthly Fee'].sum():,.2f}")
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("Income Summary Processor Test Suite")
    print("=" * 60)
    
    tests = [
        test_data_loading,
        test_opening_balances,
        test_fee_payments,
        test_summary_generation
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ Test failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Tests completed!")

if __name__ == "__main__":
    main()