# Phillips Curve Data Fetcher Setup

## Quick Setup (2 minutes)

### 1. Get your FREE FRED API Key
- Go to: https://fred.stlouisfed.org/docs/api/api_key.html
- Click "Request API Key"
- Fill out the simple form (name, email, intended use)
- You'll receive your API key immediately

### 2. Update the Script
- Open `fetch_phillips_data.py`
- Replace `YOUR_FRED_API_KEY` with your actual API key
- Save the file

### 3. Run the Data Fetcher
```bash
python3 fetch_phillips_data.py
```

## What You'll Get

### Two CSV Files:
1. **phillips_curve_monthly_data.csv** - Monthly data from 1960-2025
2. **phillips_curve_quarterly_data.csv** - Quarterly averages for analysis

### Data Columns:
- `date` - Timestamp
- `unemployment_rate` - Monthly unemployment rate (%)
- `core_inflation_rate` - Year-over-year core CPI inflation (%)
- `headline_inflation_rate` - Year-over-year headline CPI inflation (%)
- `inflation_differential` - Headline minus core inflation
- `unemployment_gap` - Deviation from 10-year moving average
- `year`, `decade`, `quarter`, `month` - Time identifiers

### Sample Output:
```
Date         Unemployment  Core Inflation  Headline Inflation
1961-01-01   6.6          1.0             1.0
1961-02-01   6.9          1.0             1.0
1961-03-01   6.9          1.0             0.9
...
```

## Data Sources (FRED API):
- **UNRATE**: Unemployment Rate
- **CPILFESL**: Consumer Price Index for All Urban Consumers: All Items Less Food and Energy
- **CPIAUCSL**: Consumer Price Index for All Urban Consumers: All Items

Ready to demonstrate Phillips Curve flattening with real Federal Reserve data!