#!/usr/bin/env python3
"""
Income Summary Generator GUI
User-friendly interface for Excel Group of Schools accounting team
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
from datetime import datetime
import calendar
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.income_summary_processor_v2 import IncomeSummaryProcessorV2


class IncomeSummaryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel Group - Income Summary Generator")
        self.root.geometry("800x600")
        
        # Set style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Initialize processor
        self.processor = IncomeSummaryProcessorV2()
        
        # File paths
        self.contacts_path = None
        self.invoices_path = None
        self.payments_path = None
        self.output_path = None
        
        # Create GUI
        self.create_widgets()
        
        # Set default paths if running from expected directory
        self.set_default_paths()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Income Summary Generator", 
                               font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File Selection Section
        file_frame = ttk.LabelFrame(main_frame, text="Data Files", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        file_frame.columnconfigure(1, weight=1)
        
        # Student Contacts
        ttk.Label(file_frame, text="Student Contacts:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.contacts_var = tk.StringVar()
        self.contacts_entry = ttk.Entry(file_frame, textvariable=self.contacts_var, state='readonly')
        self.contacts_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        ttk.Button(file_frame, text="Browse", command=lambda: self.browse_file('contacts')).grid(row=0, column=2, pady=5)
        
        # Invoices
        ttk.Label(file_frame, text="Invoices:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.invoices_var = tk.StringVar()
        self.invoices_entry = ttk.Entry(file_frame, textvariable=self.invoices_var, state='readonly')
        self.invoices_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        ttk.Button(file_frame, text="Browse", command=lambda: self.browse_file('invoices')).grid(row=1, column=2, pady=5)
        
        # Payments
        ttk.Label(file_frame, text="Payments:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.payments_var = tk.StringVar()
        self.payments_entry = ttk.Entry(file_frame, textvariable=self.payments_var, state='readonly')
        self.payments_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        ttk.Button(file_frame, text="Browse", command=lambda: self.browse_file('payments')).grid(row=2, column=2, pady=5)
        
        # Output Directory
        ttk.Label(file_frame, text="Output Directory:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.output_var = tk.StringVar()
        self.output_entry = ttk.Entry(file_frame, textvariable=self.output_var, state='readonly')
        self.output_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_output_dir).grid(row=3, column=2, pady=5)
        
        # Filter Section
        filter_frame = ttk.LabelFrame(main_frame, text="Report Options", padding="10")
        filter_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        filter_frame.columnconfigure(1, weight=1)
        filter_frame.columnconfigure(3, weight=1)
        
        # Month selection
        ttk.Label(filter_frame, text="Month:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.month_var = tk.StringVar()
        self.month_combo = ttk.Combobox(filter_frame, textvariable=self.month_var, state='readonly', width=15)
        self.month_combo['values'] = ['All Months'] + list(calendar.month_name)[1:]
        self.month_combo.set('All Months')
        self.month_combo.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Year selection
        ttk.Label(filter_frame, text="Year:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        self.year_var = tk.StringVar()
        self.year_combo = ttk.Combobox(filter_frame, textvariable=self.year_var, state='readonly', width=15)
        current_year = datetime.now().year
        self.year_combo['values'] = ['All Years'] + list(range(current_year - 2, current_year + 2))
        self.year_combo.set(str(current_year))
        self.year_combo.grid(row=0, column=3, sticky=tk.W, padx=10, pady=5)
        
        # School filter
        ttk.Label(filter_frame, text="School:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.school_var = tk.StringVar()
        self.school_combo = ttk.Combobox(filter_frame, textvariable=self.school_var, state='readonly', width=25)
        self.school_combo['values'] = ['All Schools', 'Excel Global School', 'Excel Central School', 'Excel Pathway School']
        self.school_combo.set('All Schools')
        self.school_combo.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=10, pady=5)
        
        # Generate Button
        self.generate_btn = ttk.Button(main_frame, text="Generate Income Summary", 
                                      command=self.generate_summary, style='Accent.TButton')
        self.generate_btn.grid(row=3, column=0, columnspan=3, pady=20)
        
        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Status Text
        self.status_text = tk.Text(main_frame, height=10, width=70)
        self.status_text.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Scrollbar for status text
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=self.status_text.yview)
        scrollbar.grid(row=5, column=3, sticky=(tk.N, tk.S), pady=10)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        # Configure row weights
        main_frame.rowconfigure(5, weight=1)
        
    def set_default_paths(self):
        """Set default paths if files exist in expected locations"""
        base_path = Path.cwd()
        data_path = base_path / 'data'
        
        # Check for input files
        contacts_file = data_path / 'input' / 'student_contacts.csv'
        if contacts_file.exists():
            self.contacts_path = contacts_file
            self.contacts_var.set(str(contacts_file))
            
        invoices_file = data_path / 'input' / 'student_invoices.csv'
        if invoices_file.exists():
            self.invoices_path = invoices_file
            self.invoices_var.set(str(invoices_file))
            
        payments_file = data_path / 'input' / 'student_payment.csv'
        if payments_file.exists():
            self.payments_path = payments_file
            self.payments_var.set(str(payments_file))
            
        # Set output directory
        output_dir = data_path / 'output'
        if output_dir.exists():
            self.output_path = output_dir
            self.output_var.set(str(output_dir))
            
    def browse_file(self, file_type):
        """Browse for input files"""
        filename = filedialog.askopenfilename(
            title=f"Select {file_type} file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            if file_type == 'contacts':
                self.contacts_path = Path(filename)
                self.contacts_var.set(filename)
            elif file_type == 'invoices':
                self.invoices_path = Path(filename)
                self.invoices_var.set(filename)
            elif file_type == 'payments':
                self.payments_path = Path(filename)
                self.payments_var.set(filename)
                
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.output_path = Path(directory)
            self.output_var.set(directory)
            
    def log_message(self, message):
        """Add message to status text"""
        self.status_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.status_text.see(tk.END)
        self.root.update()
        
    def generate_summary(self):
        """Generate income summary in a separate thread"""
        # Validate inputs
        if not all([self.contacts_path, self.invoices_path, self.payments_path, self.output_path]):
            messagebox.showerror("Error", "Please select all required files and output directory")
            return
            
        # Disable button and start progress
        self.generate_btn.config(state='disabled')
        self.progress.start()
        self.status_text.delete(1.0, tk.END)
        
        # Run in separate thread
        thread = threading.Thread(target=self._generate_summary_thread)
        thread.start()
        
    def _generate_summary_thread(self):
        """Generate summary in background thread"""
        try:
            # Copy files to expected locations if different
            self.log_message("Preparing data files...")
            
            # Create a new processor with custom paths
            processor = IncomeSummaryProcessorV2()
            
            # Override the default paths
            processor.contacts_df = None
            processor.invoices_df = None
            processor.payments_df = None
            
            # Load data with custom paths
            import pandas as pd
            self.log_message("Loading student contacts...")
            processor.contacts_df = pd.read_csv(self.contacts_path, encoding='utf-8-sig', 
                                              dtype={'Contact ID': str, 'Customer ID': str})
            
            self.log_message("Loading invoices...")
            processor.invoices_df = pd.read_csv(self.invoices_path, encoding='utf-8-sig',
                                              dtype={'Customer ID': str, 'Invoice Number': str},
                                              low_memory=False)
            
            self.log_message("Loading payments...")
            processor.payments_df = pd.read_csv(self.payments_path, encoding='utf-8-sig',
                                              dtype={'CustomerID': str, 'Invoice Number': str})
            
            # Convert dates
            processor.payments_df['Date'] = pd.to_datetime(processor.payments_df['Date'])
            processor.invoices_df['Invoice Date'] = pd.to_datetime(processor.invoices_df['Invoice Date'])
            
            # Clean data
            processor._clean_data()
            
            # Get filter values
            month = self.month_var.get()
            year = self.year_var.get()
            school = self.school_var.get()
            
            # Process filters
            month_filter = None if month == 'All Months' else month
            year_filter = None if year == 'All Years' else int(year)
            
            self.log_message(f"Generating summary for {month} {year}...")
            
            # Generate summary
            summary_df = processor.generate_summary(month=month_filter, year=year_filter)
            
            # Apply school filter if needed
            if school != 'All Schools' and not summary_df.empty:
                summary_df = summary_df[summary_df['School'] == school]
            
            # Save output
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"income_summary_{timestamp}.csv"
            output_file = self.output_path / filename
            
            summary_df.to_csv(output_file, index=False, encoding='utf-8-sig')
            
            # Log results
            self.log_message(f"\n✓ Summary generated successfully!")
            self.log_message(f"✓ Output saved to: {output_file}")
            self.log_message(f"\nSummary Statistics:")
            self.log_message(f"- Total rows: {len(summary_df)}")
            self.log_message(f"- Total Opening Balance: ₹{summary_df['Opening Balance'].sum():,.2f}")
            self.log_message(f"- Total Initial Fee: ₹{summary_df['Initial Fee'].sum():,.2f}")
            self.log_message(f"- Total Term/Monthly Fee: ₹{summary_df['Term / Monthly Fee'].sum():,.2f}")
            
            # Show success message
            self.root.after(0, lambda: messagebox.showinfo("Success", 
                f"Income summary generated successfully!\n\nSaved to:\n{output_file}"))
            
        except Exception as e:
            self.log_message(f"ERROR: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to generate summary:\n{str(e)}"))
            
        finally:
            # Re-enable button and stop progress
            self.root.after(0, lambda: self.generate_btn.config(state='normal'))
            self.root.after(0, self.progress.stop)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = IncomeSummaryGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()