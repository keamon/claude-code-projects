# Claude Code Project Configuration

## Project: Federal Reserve Policy Analysis

### Key Commands
- Run Fed policy analyzer: `python3 fed_policy_analyzer.py`
- Run interactive dashboard: `streamlit run fred_dashboard.py`
- Install dependencies: `pip install -r requirements.txt`

### FRED API Setup
- Get free API key: https://fred.stlouisfed.org/docs/api/api_key.html
- Set environment variable: `export FRED_API_KEY=your_key_here`
- Script runs in demo mode without API key
- Always use the FRED API key from environment variable. Do not explicitly show API key in any coding script or in the messages to me.

### Output Files
- `fed_policy_dashboard.png` - Visual dashboard for presentations
- `fed_policy_insights.txt` - Written portfolio analysis
- Demo data reflects current economic conditions (2024)

### Key Economic Indicators Tracked
- Federal Funds Rate
- 10-Year Treasury Yield
- 2-Year Treasury Yield
- Unemployment Rate
- Core CPI Inflation
- Core PCE
- Inflation Rate (CPI)
- YoY Inflation Rate (calculated)
- GDP Growth
- VIX Volatility Index
- Consumer Sentiment
- Dollar Index

### Portfolio Analysis Features
- Interest rate environment assessment
- Inflation trend analysis
- Employment situation review
- Market sentiment indicators
- Sector allocation recommendations
- Fed policy regime detection