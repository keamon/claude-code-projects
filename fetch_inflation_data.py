import requests
import pandas as pd
from datetime import datetime, timedelta
import json

def fetch_fred_data(series_id, api_key=None, start_date=None, end_date=None):
    """
    Fetch data from FRED API
    
    Args:
        series_id: FRED series ID (e.g., 'CPIAUCSL' for CPI)
        api_key: FRED API key (required for API access)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    if not api_key:
        print("FRED API key is required. Get a free key at: https://research.stlouisfed.org/docs/api/api_key.html")
        return None
        
    base_url = "https://api.stlouisfed.org/fred/series/observations"
    
    params = {
        'series_id': series_id,
        'api_key': api_key,
        'file_type': 'json',
        'sort_order': 'asc'
    }
    
    if start_date:
        params['observation_start'] = start_date
    
    if end_date:
        params['observation_end'] = end_date
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        observations = data['observations']
        
        # Convert to DataFrame
        df = pd.DataFrame(observations)
        df['date'] = pd.to_datetime(df['date'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df = df.dropna(subset=['value'])
        df = df.sort_values('date')
        
        return df
        
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    except KeyError as e:
        print(f"Error parsing response: {e}")
        return None

def calculate_inflation_rate(cpi_data):
    """Calculate year-over-year inflation rate from CPI data"""
    cpi_data = cpi_data.copy()
    cpi_data['inflation_rate'] = cpi_data['value'].pct_change(periods=12) * 100
    return cpi_data

def main():
    print("Fetching Consumer Price Index (CPI) data from FRED...")
    
    # Get API key from user or environment
    api_key = input("Enter your FRED API key (or press Enter to skip): ").strip()
    if not api_key:
        import os
        api_key = os.environ.get('FRED_API_KEY')
    
    # Fetch CPI data (last 5 years)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=5*365)).strftime('%Y-%m-%d')
    
    # CPIAUCSL = Consumer Price Index for All Urban Consumers: All Items in U.S. City Average
    cpi_data = fetch_fred_data('CPIAUCSL', api_key=api_key, start_date=start_date, end_date=end_date)
    
    if cpi_data is not None:
        print(f"\nSuccessfully fetched {len(cpi_data)} observations")
        print(f"Date range: {cpi_data['date'].min()} to {cpi_data['date'].max()}")
        
        # Calculate inflation rate
        cpi_with_inflation = calculate_inflation_rate(cpi_data)
        
        print("\nLatest CPI and Inflation Data:")
        print("-" * 50)
        recent_data = cpi_with_inflation.tail(12)[['date', 'value', 'inflation_rate']]
        recent_data.columns = ['Date', 'CPI', 'Inflation Rate (%)']
        print(recent_data.to_string(index=False, float_format='%.2f'))
        
        # Save to CSV
        output_file = 'cpi_inflation_data.csv'
        cpi_with_inflation.to_csv(output_file, index=False)
        print(f"\nData saved to: {output_file}")
        
        # Current inflation rate
        latest_inflation = cpi_with_inflation['inflation_rate'].iloc[-1]
        if pd.notna(latest_inflation):
            print(f"\nCurrent annual inflation rate: {latest_inflation:.2f}%")
    
    else:
        print("Failed to fetch data.")
        print("\nTo use this script, you need a free FRED API key:")
        print("1. Go to: https://research.stlouisfed.org/docs/api/api_key.html")
        print("2. Create an account and get your API key")
        print("3. Run the script again and enter your API key when prompted")
        print("4. Or set the FRED_API_KEY environment variable")

if __name__ == "__main__":
    main()