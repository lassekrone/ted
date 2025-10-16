# TED Contract Awards Dashboard

An interactive Streamlit dashboard for analyzing Swedish contract award notices from TED (Tenders Electronic Daily).

## Features

### Key Metrics
The dashboard displays the following key performance indicators:

1. **Unique Notices**: Total number of unique contract award notices
2. **Total Value (Notices)**: Sum of total values across all notices
3. **Unique Sub-Contracts**: Total number of unique tender lots/sub-contracts
4. **Total Value (Tenders)**: Sum of all tender values
5. **Avg Value per Notice**: Average total value per notice
6. **Unique Winners**: Number of unique companies that won contracts
7. **Avg Lots per Notice**: Average number of lots per notice
8. **Avg Tender Value**: Average value per tender/lot

### Filters

The dashboard provides powerful filtering capabilities in the sidebar:

- **CPV Code Filter**: Filter contracts by CPV (Common Procurement Vocabulary) codes
  - Searches both main CPV code and additional classifications
  - Supports multiple codes separated by commas
  
- **Keyword Search**: Search for specific terms in notice titles or descriptions
  - Case-insensitive search
  - Searches both title and description fields
  
- **Date Range**: Filter by publication date range

### Visualizations

The dashboard includes several interactive charts:

1. **Time Series**: Contract award notices over time
2. **Top Winners**: Companies that won the most contracts
3. **Top Buyers**: Organizations that issued the most notices
4. **CPV Distribution**: Most common CPV codes
5. **Value Distribution**: Histogram of notice values

### Data Table

- Browse detailed contract information
- Clickable links to official TED notices
- Download filtered data as CSV

## Installation

### Prerequisites

- Python 3.12 or higher
- uv package manager (or pip)

### Install Dependencies

Using uv (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -r pyproject.toml
```

## Usage

### Running the Dashboard

1. Navigate to the project directory:
```bash
cd /path/to/ted
```

2. Run the Streamlit app:
```bash
streamlit run dashboard.py
```

Or using uv:
```bash
uv run streamlit run dashboard.py
```

3. The dashboard will open in your default web browser at `http://localhost:8501`

### Using the Dashboard

1. **Apply Filters** (optional):
   - Enter CPV codes in the sidebar (e.g., `45000000` for construction)
   - Enter keywords to search (e.g., `IT services`, `construction`)
   - Select a date range

2. **View Metrics**: The top section displays key performance indicators that update based on your filters

3. **Explore Visualizations**: Scroll down to see interactive charts and graphs

4. **Browse Contracts**: View detailed contract information in the data table at the bottom

5. **Download Data**: Click the "Download Filtered Data as CSV" button to export your filtered results

## Data Structure

The dashboard expects a CSV file at `ted_winner_data/ted_swe_last_year_subcontracts_detailed.csv` with the following columns:

- `publication_number`: Unique identifier for each notice
- `publication_date`: Date when the notice was published
- `notice_title`: Title of the contract notice
- `notice_description`: Description of the contract
- `cpv_code`: Main industry classification code
- `additional_classification`: Additional CPV codes
- `tender_lot_identifier`: Identifier for sub-contracts within a notice
- `tender_value`: Value of individual lots/tenders
- `total_value`: Total value of the entire notice
- `buyer_name`: Name of the buying organization
- `buyer_country`: Country of the buyer
- `winner_name`: Name of the winning company
- `winner_country`: Country of the winner
- `winner_email`: Contact email of the winner
- `ted_link_eng`: Link to the official TED notice

## Tips

- **CPV Codes**: You can find CPV codes at the European Commission's CPV website
  - Use broader codes for wider searches (e.g., `45000000` for all construction)
  - Use specific codes for narrow searches (e.g., `45111200` for soil investigation)

- **Keyword Search**: Use specific terms for better results
  - Search is case-insensitive
  - Terms are searched in both title and description

- **Performance**: The dashboard uses caching to improve performance
  - Data is cached after first load
  - Refresh the page to reload data if the CSV file changes

## Troubleshooting

### Dashboard won't start
- Ensure all dependencies are installed: `uv sync`
- Check that Python 3.12+ is installed: `python --version`

### No data displayed
- Verify the CSV file exists at `ted_winner_data/ted_swe_last_year_subcontracts_detailed.csv`
- Check that filters aren't too restrictive
- Try resetting filters by clearing the input fields

### Charts not displaying
- Ensure Plotly is installed: `uv pip list | grep plotly`
- Check browser console for JavaScript errors
- Try a different browser

## License

This dashboard is part of the TED data analysis project.

