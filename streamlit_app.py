"""
Excel Group Income Summary Generator - Web App
Streamlit-based web interface for generating income summaries
"""

import streamlit as st
import pandas as pd
import io
from datetime import datetime
import calendar
from pathlib import Path
import sys
import matplotlib.pyplot as plt

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

from src.income_summary_processor_v2 import IncomeSummaryProcessorV2

# Page configuration
st.set_page_config(
    page_title="Income Summary Generator - Excel Group",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stButton > button {
        background-color: #0068C9;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #0051A2;
        transform: translateY(-2px);
    }
    .upload-text {
        font-size: 1.1rem;
        color: #0068C9;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'processor' not in st.session_state:
    st.session_state.processor = None
if 'summary_generated' not in st.session_state:
    st.session_state.summary_generated = False

# Header
st.title("📊 Income Summary Generator")
st.markdown("### Excel Group of Schools - ZOHO Books Data Processor")
st.markdown("---")

# Sidebar for instructions
with st.sidebar:
    st.header("📋 Instructions")
    st.markdown("""
    1. **Upload Files**: Upload the three required CSV files
    2. **Select Options**: Choose month, year, and school filters
    3. **Generate**: Click 'Generate Summary' to process
    4. **Download**: Download the generated summary
    
    ### Required Files:
    - 📁 **student_contacts.csv** - Student information
    - 📁 **student_invoices.csv** - Invoice records  
    - 📁 **student_payment.csv** - Payment records
    
    ### Optional:
    - 📁 **fee_items.csv** - Fee reference (uses default if not provided)
    """)
    
    st.markdown("---")
    st.info("💡 **Tip**: The app saves your uploaded files temporarily. Refresh the page to start over.")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📤 Upload Data Files")
    
    # File uploaders
    uploaded_files = {}
    
    uploaded_files['contacts'] = st.file_uploader(
        "Choose student_contacts.csv file",
        type=['csv'],
        key='contacts',
        help="Upload the student contacts CSV file from ZOHO Books"
    )
    
    uploaded_files['invoices'] = st.file_uploader(
        "Choose student_invoices.csv file",
        type=['csv'],
        key='invoices',
        help="Upload the invoices CSV file from ZOHO Books"
    )
    
    uploaded_files['payments'] = st.file_uploader(
        "Choose student_payment.csv file",
        type=['csv'],
        key='payments',
        help="Upload the payments CSV file from ZOHO Books"
    )
    
    # Optional fee items file
    with st.expander("Advanced Options"):
        uploaded_files['fee_items'] = st.file_uploader(
            "Choose fee_items.csv file (optional)",
            type=['csv'],
            key='fee_items',
            help="Upload custom fee items reference file"
        )

with col2:
    st.header("⚙️ Report Options")
    
    # Month selection
    month_options = ['All Months'] + list(calendar.month_name)[1:]
    selected_month = st.selectbox(
        "Select Month",
        month_options,
        index=0,
        help="Choose a specific month or all months"
    )
    
    # Year selection
    current_year = datetime.now().year
    year_options = ['All Years'] + list(range(current_year - 2, current_year + 2))
    selected_year = st.selectbox(
        "Select Year",
        year_options,
        index=year_options.index(current_year) if current_year in year_options else 0,
        help="Choose a specific year or all years"
    )
    
    # School selection
    school_options = ['All Schools', 'Excel Global School', 'Excel Central School', 'Excel Pathway School']
    selected_school = st.selectbox(
        "Select School",
        school_options,
        index=0,
        help="Filter by specific school"
    )

# Generate button
st.markdown("---")

if st.button("🚀 Generate Income Summary", type="primary", use_container_width=True):
    # Validate file uploads
    if not all([uploaded_files['contacts'], uploaded_files['invoices'], uploaded_files['payments']]):
        st.error("❌ Please upload all three required files!")
    else:
        try:
            # Create processor
            processor = IncomeSummaryProcessorV2()
            
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Load data from uploaded files
            status_text.text("Loading student contacts...")
            progress_bar.progress(20)
            processor.contacts_df = pd.read_csv(
                uploaded_files['contacts'],
                encoding='utf-8-sig',
                dtype={'Contact ID': str, 'Customer ID': str}
            )
            
            status_text.text("Loading invoices...")
            progress_bar.progress(40)
            processor.invoices_df = pd.read_csv(
                uploaded_files['invoices'],
                encoding='utf-8-sig',
                dtype={'Customer ID': str, 'Invoice Number': str},
                low_memory=False
            )
            
            status_text.text("Loading payments...")
            progress_bar.progress(60)
            processor.payments_df = pd.read_csv(
                uploaded_files['payments'],
                encoding='utf-8-sig',
                dtype={'CustomerID': str, 'Invoice Number': str}
            )
            
            # Load fee items if provided
            if uploaded_files['fee_items']:
                processor.fee_items_df = pd.read_csv(
                    uploaded_files['fee_items'],
                    encoding='utf-8-sig'
                )
            
            # Convert dates
            processor.payments_df['Date'] = pd.to_datetime(processor.payments_df['Date'])
            processor.invoices_df['Invoice Date'] = pd.to_datetime(processor.invoices_df['Invoice Date'])
            
            # Clean data
            processor._clean_data()
            
            # Process filters
            month_filter = None if selected_month == 'All Months' else selected_month
            year_filter = None if selected_year == 'All Years' else int(selected_year)
            
            # Generate summary
            status_text.text("Generating summary...")
            progress_bar.progress(80)
            
            summary_df = processor.generate_summary(month=month_filter, year=year_filter)
            
            # Apply school filter
            if selected_school != 'All Schools' and not summary_df.empty:
                summary_df = summary_df[summary_df['School'] == selected_school]
            
            progress_bar.progress(100)
            status_text.text("✅ Summary generated successfully!")
            
            # Store in session state
            st.session_state.summary_df = summary_df
            st.session_state.summary_generated = True
            
            # Success message
            st.success(f"✅ Generated summary with {len(summary_df)} rows")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)

# Display results
if st.session_state.summary_generated and 'summary_df' in st.session_state:
    st.markdown("---")
    st.header("📊 Summary Results")
    
    summary_df = st.session_state.summary_df
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Rows",
            f"{len(summary_df):,}"
        )
    
    with col2:
        st.metric(
            "Opening Balance",
            f"₹{summary_df['Opening Balance'].sum():,.2f}"
        )
    
    with col3:
        st.metric(
            "Initial Fee",
            f"₹{summary_df['Initial Fee'].sum():,.2f}"
        )
    
    with col4:
        st.metric(
            "Term/Monthly Fee",
            f"₹{summary_df['Term / Monthly Fee'].sum():,.2f}"
        )
    
    # Display data
    st.subheader("Summary Data")
    st.dataframe(
        summary_df,
        use_container_width=True,
        height=400
    )
    
    # Download section
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Generate CSV
        csv_buffer = io.StringIO()
        summary_df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        csv_data = csv_buffer.getvalue()
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"income_summary_{timestamp}.csv"
        
        # Download button
        st.download_button(
            label="📥 Download Summary as CSV",
            data=csv_data,
            file_name=filename,
            mime="text/csv",
            use_container_width=True
        )
    
    # Additional analysis
    with st.expander("📈 View Analysis & Charts", expanded=True):
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 School Analysis", "📈 Grade Analysis", "📅 Monthly Trends", "🥧 Distribution"])
        
        with tab1:
            # Group by school
            if len(summary_df['School'].unique()) > 1:
                st.subheader("Summary by School")
                school_summary = summary_df.groupby('School').agg({
                    'Opening Balance': 'sum',
                    'Initial Fee': 'sum',
                    'Term / Monthly Fee': 'sum'
                }).round(2)
                
                # Display table
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.dataframe(school_summary, use_container_width=True)
                
                with col2:
                    # Create bar chart
                    school_chart_data = school_summary.reset_index()
                    school_chart_data = school_chart_data.melt(
                        id_vars=['School'],
                        value_vars=['Opening Balance', 'Initial Fee', 'Term / Monthly Fee'],
                        var_name='Fee Type',
                        value_name='Amount'
                    )
                    
                    st.bar_chart(
                        data=school_chart_data.pivot(index='School', columns='Fee Type', values='Amount'),
                        use_container_width=True,
                        height=400
                    )
            else:
                st.info("📌 Single school selected - no comparison available")
        
        with tab2:
            # Group by grade
            st.subheader("Summary by Grade")
            grade_summary = summary_df.groupby('Grade').agg({
                'Opening Balance': 'sum',
                'Initial Fee': 'sum',
                'Term / Monthly Fee': 'sum'
            }).round(2)
            
            # Create columns for better layout
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.dataframe(grade_summary, use_container_width=True)
            
            with col2:
                # Create bar chart for grades
                grade_chart_data = grade_summary.reset_index()
                grade_chart_data = grade_chart_data.melt(
                    id_vars=['Grade'],
                    value_vars=['Opening Balance', 'Initial Fee', 'Term / Monthly Fee'],
                    var_name='Fee Type',
                    value_name='Amount'
                )
                
                # Sort grades properly
                grade_order = ['Pre-KG', 'LKG', 'UKG'] + [f'Grade {i:02d}' for i in range(1, 13)]
                grade_chart_data['Grade'] = pd.Categorical(
                    grade_chart_data['Grade'], 
                    categories=[g for g in grade_order if g in grade_chart_data['Grade'].unique()],
                    ordered=True
                )
                grade_chart_data = grade_chart_data.sort_values('Grade')
                
                st.bar_chart(
                    data=grade_chart_data.pivot(index='Grade', columns='Fee Type', values='Amount'),
                    use_container_width=True,
                    height=400
                )
        
        with tab3:
            # Monthly trends if multiple months
            if 'Month' in summary_df.columns and len(summary_df['Month'].unique()) > 1:
                st.subheader("Monthly Collection Trends")
                
                monthly_summary = summary_df.groupby('Month').agg({
                    'Opening Balance': 'sum',
                    'Initial Fee': 'sum',
                    'Term / Monthly Fee': 'sum'
                }).round(2)
                
                # Create line chart
                monthly_summary['Total Collection'] = monthly_summary.sum(axis=1)
                
                st.line_chart(
                    data=monthly_summary[['Opening Balance', 'Initial Fee', 'Term / Monthly Fee', 'Total Collection']],
                    use_container_width=True,
                    height=400
                )
                
                # Show monthly breakdown
                st.dataframe(monthly_summary, use_container_width=True)
            else:
                st.info("📌 Single month selected - no trend analysis available")
        
        with tab4:
            # Distribution charts
            st.subheader("Fee Distribution")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Pie chart for total fee distribution
                fee_totals = {
                    'Opening Balance': summary_df['Opening Balance'].sum(),
                    'Initial Fee': summary_df['Initial Fee'].sum(),
                    'Term/Monthly Fee': summary_df['Term / Monthly Fee'].sum()
                }
                
                # Create pie chart using matplotlib
                
                fig, ax = plt.subplots(figsize=(8, 6))
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
                
                # Filter out zero values
                non_zero_fees = {k: v for k, v in fee_totals.items() if v > 0}
                
                if non_zero_fees:
                    wedges, texts, autotexts = ax.pie(
                        non_zero_fees.values(),
                        labels=non_zero_fees.keys(),
                        autopct='%1.1f%%',
                        colors=colors[:len(non_zero_fees)],
                        startangle=90
                    )
                    
                    # Enhance text
                    for text in texts:
                        text.set_fontsize(12)
                    for autotext in autotexts:
                        autotext.set_color('white')
                        autotext.set_fontsize(10)
                        autotext.set_weight('bold')
                    
                    ax.set_title('Total Fee Distribution', fontsize=14, fontweight='bold')
                    st.pyplot(fig)
                else:
                    st.info("No fee data to display")
            
            with col2:
                # Top sections by collection
                section_summary = summary_df.groupby('Section').agg({
                    'Opening Balance': 'sum',
                    'Initial Fee': 'sum',
                    'Term / Monthly Fee': 'sum'
                })
                section_summary['Total'] = section_summary.sum(axis=1)
                section_summary = section_summary.sort_values('Total', ascending=False).head(10)
                
                if not section_summary.empty:
                    st.subheader("Top 10 Sections by Collection")
                    
                    # Horizontal bar chart
                    fig2, ax2 = plt.subplots(figsize=(8, 6))
                    section_summary['Total'].plot(kind='barh', ax=ax2, color='#0068C9')
                    ax2.set_xlabel('Total Collection (₹)')
                    ax2.set_title('Top Sections by Total Collection', fontsize=14, fontweight='bold')
                    
                    # Format x-axis labels
                    ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))
                    
                    plt.tight_layout()
                    st.pyplot(fig2)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Income Summary Generator v1.0 | Excel Group of Schools</p>
        <p>For support, contact the IT department</p>
    </div>
    """,
    unsafe_allow_html=True
)