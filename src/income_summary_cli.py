#!/usr/bin/env python3
"""
Income Summary Generator CLI
Command-line interface that works on all platforms
"""

import sys
from pathlib import Path
from datetime import datetime
import calendar

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.income_summary_processor_v2 import IncomeSummaryProcessorV2


def main():
    print("=" * 60)
    print("Excel Group - Income Summary Generator")
    print("=" * 60)
    
    processor = IncomeSummaryProcessorV2()
    
    # Check if default files exist
    data_path = Path.cwd() / 'data'
    default_files_exist = all([
        (data_path / 'input' / 'student_contacts.csv').exists(),
        (data_path / 'input' / 'student_invoices.csv').exists(),
        (data_path / 'input' / 'student_payment.csv').exists()
    ])
    
    if default_files_exist:
        print("\n✓ Found data files in default location")
        use_default = input("Use default data files? (y/n): ").lower() == 'y'
        
        if not use_default:
            print("\nPlease place your CSV files in:")
            print(f"  {data_path / 'input'}")
            return
    else:
        print("\n⚠️  Data files not found in default location")
        print("\nPlease place the following files in data/input/:")
        print("  - student_contacts.csv")
        print("  - student_invoices.csv")
        print("  - student_payment.csv")
        return
    
    # Load data
    print("\nLoading data files...")
    if not processor.load_data():
        print("Failed to load data files")
        return
    
    # Get filter options
    print("\n" + "-" * 40)
    print("Report Options")
    print("-" * 40)
    
    # Month selection
    print("\nSelect Month:")
    print("0. All Months")
    months = list(calendar.month_name)[1:]
    for i, month in enumerate(months, 1):
        print(f"{i}. {month}")
    
    month_choice = input("\nEnter choice (0-12): ")
    month_filter = None
    if month_choice.isdigit() and 1 <= int(month_choice) <= 12:
        month_filter = months[int(month_choice) - 1]
    
    # Year selection
    current_year = datetime.now().year
    print(f"\nSelect Year (or press Enter for all years):")
    year_input = input(f"Year [{current_year}]: ").strip()
    year_filter = None
    if year_input:
        try:
            year_filter = int(year_input)
        except ValueError:
            print("Invalid year, using all years")
    
    # School selection
    print("\nSelect School:")
    print("0. All Schools")
    print("1. Excel Global School")
    print("2. Excel Central School")
    print("3. Excel Pathway School")
    
    school_choice = input("Enter choice (0-3): ")
    school_filter = None
    school_map = {
        '1': 'Excel Global School',
        '2': 'Excel Central School', 
        '3': 'Excel Pathway School'
    }
    school_name = school_map.get(school_choice, 'All Schools')
    
    # Generate summary
    print("\n" + "-" * 40)
    print(f"Generating summary for {month_filter or 'all months'} {year_filter or ''}")
    if school_name != 'All Schools':
        print(f"School: {school_name}")
    print("-" * 40)
    
    summary_df = processor.generate_summary(month=month_filter, year=year_filter)
    
    # Apply school filter if needed
    if school_choice in school_map and not summary_df.empty:
        summary_df = summary_df[summary_df['School'] == school_map[school_choice]]
    
    # Save output
    output_path = processor.save_summary(summary_df)
    
    # Display results
    print(f"\n✓ Summary generated successfully!")
    print(f"✓ Output saved to: {output_path}")
    
    if not summary_df.empty:
        print(f"\nSummary Statistics:")
        print(f"- Total rows: {len(summary_df)}")
        print(f"- Total Opening Balance: ₹{summary_df['Opening Balance'].sum():,.2f}")
        print(f"- Total Initial Fee: ₹{summary_df['Initial Fee'].sum():,.2f}")
        print(f"- Total Term/Monthly Fee: ₹{summary_df['Term / Monthly Fee'].sum():,.2f}")
        
        print("\nView the full report in the CSV file.")
    else:
        print("\nNo data found for the selected filters.")
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()