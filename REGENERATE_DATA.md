# Regenerate CSV with Clean Data

## What Changed

The `post_process.py` script now performs comprehensive data cleaning:

### 1. Date Cleaning
- **Before**: `2024-10-16+02:00` (ISO 8601 with timezone)
- **After**: `2024-10-16` (Simple YYYY-MM-DD format)
- Fixes the NaT (Not a Time) error in the dashboard

### 2. Value Filtering
- **Filters out**: Records where BOTH `tender_value` AND `total_value` are below 500,000 SEK or NA
- **Keeps**: Records where EITHER value is >= 500,000 SEK
- **Converts**: Values to integers (removing decimals)

This ensures the dashboard only shows significant contracts worth at least 500,000 SEK.

## How to Regenerate the CSV

Run the post-processing script to regenerate the CSV file:

```bash
uv run python post_process.py
```

This will:
1. Read the original JSON data: `ted_winner_data/ted_swe_last_year.json`
2. Process and clean all dates
3. Overwrite the CSV file: `ted_winner_data/ted_swe_last_year_subcontracts_detailed.csv`

## After Regeneration

Once the CSV is regenerated with clean dates, run the dashboard:

```bash
./run_dashboard.sh
```

The dashboard should now load without any date-related errors!

## Expected Output

When you run the script, you'll see:
```
Cleaning and standardizing dates...
Cleaning value fields...
Filtered out X records with values below 500,000 or NA
Remaining records: Y
```

The number of records will be reduced to only include significant contracts.

## Changes Made

### post_process.py
- **Date cleaning** (lines 359-368): Converts dates from ISO 8601 with timezone to simple YYYY-MM-DD format
- **Value filtering** (lines 370-395): 
  - Converts tender_value and total_value to numeric
  - Filters out records where both values are < 500,000 or NA
  - Converts remaining values to integers
  - Reports filtering statistics

### dashboard.py
- Simplified date parsing (uses explicit format='%Y-%m-%d')
- Removed numeric conversion for values (already done in post_process.py)
- Added fallback for cases with no valid dates
- Values are now integers instead of floats

