"""
Streamlit dashboard for analyzing Swedish TED contract award notices.

This dashboard provides insights into contract awards from the past year,
with filtering capabilities by CPV code and keyword search.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# Page configuration
st.set_page_config(
    page_title="TED Contract Awards Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and prepare the contract awards dataset."""
    df = pd.read_csv("ted_winner_data/ted_swe_last_year_subcontracts_detailed.csv")
    
    # Convert publication_date to datetime (already in YYYY-MM-DD format from post_process.py)
    df['publication_date'] = pd.to_datetime(df['publication_date'], format='%Y-%m-%d', errors='coerce')
    
    # Note: total_value and tender_value are already cleaned and converted to integers in post_process.py
    # Values below 500,000 have been filtered out at source
    
    # Fill NaN values for text columns
    df['notice_title'] = df['notice_title'].fillna('')
    df['notice_description'] = df['notice_description'].fillna('')
    df['cpv_code'] = df['cpv_code'].fillna('')
    df['additional_classification'] = df['additional_classification'].fillna('')
    df['winner_name'] = df['winner_name'].fillna('')
    
    return df


def filter_by_cpv_code(df: pd.DataFrame, cpv_codes: list) -> pd.DataFrame:
    """Filter dataframe by CPV codes (searches both cpv_code and additional_classification)."""
    if not cpv_codes:
        return df
    
    # Convert CPV codes to strings for comparison
    cpv_codes_str = [str(code) for code in cpv_codes]
    
    # Create boolean mask for filtering
    mask = pd.Series([False] * len(df), index=df.index)
    
    for code in cpv_codes_str:
        # Check main cpv_code column
        mask |= df['cpv_code'].astype(str).str.contains(code, case=False, na=False)
        # Check additional_classification column
        mask |= df['additional_classification'].astype(str).str.contains(code, case=False, na=False)
    
    return df[mask]


def filter_by_keywords(df: pd.DataFrame, keywords: str, match_all: bool = False) -> pd.DataFrame:
    """
    Filter dataframe by multiple keywords in title or description.
    
    Args:
        df: DataFrame to filter
        keywords: Comma-separated keywords to search for
        match_all: If True, all keywords must be present (AND). If False, any keyword matches (OR)
    
    Returns:
        Filtered DataFrame
    """
    if not keywords:
        return df
    
    # Split keywords by comma and strip whitespace
    keyword_list = [k.strip().lower() for k in keywords.split(',') if k.strip()]
    
    if not keyword_list:
        return df
    
    if match_all:
        # AND logic: All keywords must be present
        mask = pd.Series([True] * len(df), index=df.index)
        for keyword in keyword_list:
            keyword_mask = (
                df['notice_title'].str.lower().str.contains(keyword, na=False) |
                df['notice_description'].str.lower().str.contains(keyword, na=False)
            )
            mask &= keyword_mask
    else:
        # OR logic: Any keyword can be present
        mask = pd.Series([False] * len(df), index=df.index)
        for keyword in keyword_list:
            keyword_mask = (
                df['notice_title'].str.lower().str.contains(keyword, na=False) |
                df['notice_description'].str.lower().str.contains(keyword, na=False)
            )
            mask |= keyword_mask
    
    return df[mask]


def calculate_metrics(df: pd.DataFrame) -> dict:
    """Calculate key metrics from the filtered dataset."""
    metrics = {}
    
    # Number of unique notices
    metrics['unique_notices'] = df['publication_number'].nunique()
    
    # Total value per notice (sum of distinct total_value for each unique notice)
    # Each notice's total_value is repeated across its lots, so we take the first non-null value per notice
    notice_total_values = df.groupby('publication_number')['total_value'].first()
    # Remove any null values before summing
    notice_total_values = notice_total_values.dropna()
    metrics['total_value_sum'] = notice_total_values.sum()
    metrics['avg_value_per_notice'] = notice_total_values.mean() if len(notice_total_values) > 0 else 0
    
    # Number of unique sub contracts (using uid column)
    # uid is publication_number + '-' + subcontract_index, uniquely identifying each subcontract
    metrics['unique_subcontracts'] = df['uid'].nunique()
    
    # Total value from tender_value
    metrics['total_tender_value'] = df['tender_value'].sum()
    
    # Number of unique winners
    valid_winners = df[df['winner_name'] != '']
    metrics['unique_winners'] = valid_winners['winner_name'].nunique()
    
    return metrics


def create_time_series_chart(df: pd.DataFrame) -> go.Figure:
    """Create a time series chart of contract publications over time."""
    # Group by date and count publications
    daily_counts = df.groupby(df['publication_date'].dt.date)['publication_number'].nunique().reset_index()
    daily_counts.columns = ['Date', 'Number of Notices']
    
    fig = px.line(
        daily_counts,
        x='Date',
        y='Number of Notices',
        title='Contract Award Notices Over Time',
        labels={'Number of Notices': 'Number of Unique Notices'}
    )
    fig.update_traces(line_color='#1f77b4')
    fig.update_layout(hovermode='x unified')
    
    return fig


def create_top_winners_chart(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Create a bar chart of top winners by number of contracts."""
    # Filter valid winners
    valid_winners = df[df['winner_name'] != '']
    
    # Count unique lots per winner
    winner_counts = valid_winners.groupby('winner_name')['tender_lot_identifier'].nunique()
    winner_counts = winner_counts.sort_values(ascending=False).head(top_n)
    
    fig = px.bar(
        x=winner_counts.values,
        y=winner_counts.index,
        orientation='h',
        title=f'Top {top_n} Winners by Number of Contracts',
        labels={'x': 'Number of Contracts', 'y': 'Winner'}
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    
    return fig


def create_top_buyers_chart(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Create a bar chart of top buyers by number of notices."""
    buyer_counts = df.groupby('buyer_name')['publication_number'].nunique()
    buyer_counts = buyer_counts.sort_values(ascending=False).head(top_n)
    
    fig = px.bar(
        x=buyer_counts.values,
        y=buyer_counts.index,
        orientation='h',
        title=f'Top {top_n} Buyers by Number of Notices',
        labels={'x': 'Number of Notices', 'y': 'Buyer'}
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    
    return fig


def format_currency(value: float, currency: str = "SEK") -> str:
    """Format currency values with thousands separators."""
    if pd.isna(value):
        return "N/A"
    return f"{value:,.0f} {currency}"


def main():
    """Main application function."""
    
    # Header
    st.title("📊 TED Contract Awards Dashboard")
    st.markdown("### Analysis of Swedish Contract Award Notices - Past Year")
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading data..."):
        df = load_data()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    st.sidebar.markdown("Apply filters to refine the analysis")
    
    # CPV Code filter
    st.sidebar.subheader("CPV Code Filter")
    cpv_input = st.sidebar.text_input(
        "Enter CPV code(s)",
        placeholder="e.g., 45000000",
        help="Enter one or more CPV codes separated by commas. Searches both main CPV code and additional classifications."
    )
    
    # Parse CPV codes
    cpv_codes = []
    if cpv_input:
        cpv_codes = [code.strip() for code in cpv_input.split(',') if code.strip()]
    
    # Keyword search filter
    st.sidebar.subheader("Keyword Search")
    keyword = st.sidebar.text_input(
        "Search in title or description",
        placeholder="e.g., construction, IT services, healthcare",
        help="Enter one or more keywords separated by commas. Searches in both title and description."
    )
    
    # Match mode for multiple keywords
    if keyword and ',' in keyword:
        match_all = st.sidebar.checkbox(
            "Match ALL keywords (AND)",
            value=False,
            help="When checked, only show results containing all keywords. When unchecked, show results with any keyword."
        )
    else:
        match_all = False
    
    # Date range filter
    st.sidebar.subheader("Date Range")
    
    # Filter out NaT values to get valid date range
    valid_dates = df['publication_date'].dropna()
    
    if len(valid_dates) > 0:
        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()
        
        date_range = st.sidebar.date_input(
            "Select date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    else:
        # Fallback if no valid dates
        st.sidebar.warning("⚠️ No valid dates found in dataset")
        date_range = []
    
    # Apply filters
    filtered_df = df.copy()
    
    # Apply date filter
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['publication_date'].dt.date >= start_date) &
            (filtered_df['publication_date'].dt.date <= end_date)
        ]
    
    # Apply CPV code filter
    if cpv_codes:
        filtered_df = filter_by_cpv_code(filtered_df, cpv_codes)
    
    # Apply keyword filter
    if keyword:
        filtered_df = filter_by_keywords(filtered_df, keyword, match_all)
    
    # Show filter summary
    if cpv_codes or keyword or len(date_range) == 2:
        st.sidebar.markdown("---")
        st.sidebar.success(f"✅ Filters applied: {len(filtered_df)} records match")
    
    # Calculate metrics
    metrics = calculate_metrics(filtered_df)
    
    # Display key metrics
    st.subheader("📈 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Unique Notices",
            value=f"{metrics['unique_notices']:,}",
            help="Total number of unique contract award notices"
        )
    
    with col2:
        st.metric(
            label="Unique Sub-Contracts",
            value=f"{metrics['unique_subcontracts']:,}",
            help="Total number of unique tender lots/sub-contracts"
        )
    
    with col3:
        st.metric(
            label="Total Value (Tenders)",
            value=format_currency(metrics['total_tender_value']),
            help="Sum of all tender values"
        )
    
    with col4:
        st.metric(
            label="Unique Winners",
            value=f"{metrics['unique_winners']:,}",
            help="Number of unique companies that won contracts"
        )
    
    st.markdown("---")
    
    # Visualizations
    st.subheader("📊 Visualizations")
    
    # Time series chart
    if len(filtered_df) > 0:
        st.plotly_chart(create_time_series_chart(filtered_df), use_container_width=True)
        
        # Two columns for charts
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.plotly_chart(create_top_winners_chart(filtered_df), use_container_width=True)
        
        with col_right:
            st.plotly_chart(create_top_buyers_chart(filtered_df), use_container_width=True)
    else:
        st.warning("⚠️ No data matches the current filters. Please adjust your filter criteria.")
    
    st.markdown("---")
    
    # Data table
    st.subheader("📋 Contract Award Details")
    
    if len(filtered_df) > 0:
        # Select relevant columns for display
        display_columns = [
            'publication_number',
            'publication_date',
            'notice_title',
            'buyer_name',
            'winner_name',
            'total_value',
            'tender_value',
            'cpv_code',
            'ted_link_eng'
        ]
        
        # Get unique notices (one row per publication_number)
        display_df = filtered_df.drop_duplicates(subset=['publication_number'])[display_columns].copy()
        
        # Format the display dataframe
        display_df['publication_date'] = display_df['publication_date'].dt.strftime('%Y-%m-%d')
        display_df['total_value'] = display_df['total_value'].apply(lambda x: format_currency(x) if pd.notna(x) else 'N/A')
        display_df['tender_value'] = display_df['tender_value'].apply(lambda x: format_currency(x) if pd.notna(x) else 'N/A')
        
        # Rename columns for better readability
        display_df = display_df.rename(columns={
            'publication_number': 'Notice ID',
            'publication_date': 'Date',
            'notice_title': 'Title',
            'buyer_name': 'Buyer',
            'winner_name': 'Winner',
            'total_value': 'Total Value',
            'tender_value': 'Tender Value',
            'cpv_code': 'CPV Code',
            'ted_link_eng': 'TED Link'
        })
        
        # Show number of records
        st.info(f"Showing {len(display_df)} unique notices")
        
        # Display the dataframe with links
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "TED Link": st.column_config.LinkColumn("TED Link", display_text="View Notice")
            }
        )
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name="filtered_contract_awards.csv",
            mime="text/csv",
            help="Download the complete filtered dataset including all sub-contracts"
        )
    else:
        st.info("No data to display. Adjust filters to see results.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
        <p>Data source: TED (Tenders Electronic Daily) - Swedish Contract Awards</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

