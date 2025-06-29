import pandas as pd
import numpy as np
from fredapi import Fred
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Initialize FRED API
fred = Fred(api_key='YOUR_FRED_API_KEY')

def fetch_phillips_curve_data():
    """Fetch unemployment and inflation data from FRED API"""
    print("Fetching Phillips Curve data from FRED API...")
    
    try:
        # Fetch Unemployment Rate (UNRATE) - monthly data
        print("  - Fetching unemployment rate (UNRATE)...")
        unemployment = fred.get_series('UNRATE', start='1960-01-01')
        
        # Fetch Core CPI (CPILFESL) - monthly data, excludes food and energy
        print("  - Fetching core CPI (CPILFESL)...")
        core_cpi = fred.get_series('CPILFESL', start='1960-01-01')
        
        # Fetch Headline CPI (CPIAUCSL) for comparison
        print("  - Fetching headline CPI (CPIAUCSL)...")
        headline_cpi = fred.get_series('CPIAUCSL', start='1960-01-01')
        
        # Calculate year-over-year inflation rates
        print("  - Calculating inflation rates...")
        core_inflation = core_cpi.pct_change(periods=12) * 100
        headline_inflation = headline_cpi.pct_change(periods=12) * 100
        
        # Create comprehensive dataset with all variables
        phillips_data = pd.DataFrame({
            'date': unemployment.index,
            'unemployment_rate': unemployment.values,
            'core_cpi_level': core_cpi.reindex(unemployment.index).values,
            'headline_cpi_level': headline_cpi.reindex(unemployment.index).values,
            'core_inflation_rate': core_inflation.reindex(unemployment.index).values,
            'headline_inflation_rate': headline_inflation.reindex(unemployment.index).values
        })
        
        # Clean the data - remove rows with missing values
        phillips_data = phillips_data.dropna()
        
        # Add additional derived metrics
        phillips_data['inflation_differential'] = phillips_data['headline_inflation_rate'] - phillips_data['core_inflation_rate']
        phillips_data['unemployment_gap'] = phillips_data['unemployment_rate'] - phillips_data['unemployment_rate'].rolling(window=120, min_periods=60).mean()
        
        # Add decade and year columns for analysis
        phillips_data['year'] = phillips_data['date'].dt.year
        phillips_data['decade'] = (phillips_data['year'] // 10) * 10
        phillips_data['quarter'] = phillips_data['date'].dt.quarter
        phillips_data['month'] = phillips_data['date'].dt.month
        
        return phillips_data
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        print("\nTo fix this error:")
        print("1. Get a free FRED API key at: https://fred.stlouisfed.org/docs/api/api_key.html")
        print("2. Replace 'YOUR_FRED_API_KEY' in the script with your actual API key")
        return None

def save_data_to_csv(data, filename):
    """Save data to CSV with proper formatting"""
    if data is not None:
        # Format the data for better readability
        data_formatted = data.copy()
        
        # Round numerical columns to appropriate decimal places
        numerical_columns = ['unemployment_rate', 'core_inflation_rate', 'headline_inflation_rate', 
                           'inflation_differential', 'unemployment_gap']
        
        for col in numerical_columns:
            if col in data_formatted.columns:
                data_formatted[col] = data_formatted[col].round(2)
        
        # Format CPI levels to 1 decimal place
        cpi_columns = ['core_cpi_level', 'headline_cpi_level']
        for col in cpi_columns:
            if col in data_formatted.columns:
                data_formatted[col] = data_formatted[col].round(1)
        
        # Save to CSV
        data_formatted.to_csv(filename, index=False)
        print(f"\n✅ Data saved to: {filename}")
        print(f"   📊 Total records: {len(data_formatted)}")
        print(f"   📅 Date range: {data_formatted['date'].min()} to {data_formatted['date'].max()}")
        
        # Display sample of the data
        print(f"\n📋 Sample of the data:")
        print(data_formatted.head(10).to_string(index=False))
        
        # Display summary statistics
        print(f"\n📈 Summary Statistics:")
        summary_stats = data_formatted[numerical_columns].describe()
        print(summary_stats.round(2))
        
        return True
    else:
        print("❌ No data to save - please check your FRED API key")
        return False

def create_quarterly_summary(data):
    """Create quarterly averages for smoother analysis"""
    if data is not None:
        # Set date as index for resampling
        data_indexed = data.set_index('date')
        
        # Resample to quarterly averages
        quarterly_data = data_indexed.resample('Q').agg({
            'unemployment_rate': 'mean',
            'core_inflation_rate': 'mean',
            'headline_inflation_rate': 'mean',
            'inflation_differential': 'mean',
            'unemployment_gap': 'mean',
            'year': 'first',
            'decade': 'first'
        }).reset_index()
        
        # Add quarter information
        quarterly_data['quarter'] = quarterly_data['date'].dt.quarter
        quarterly_data['year_quarter'] = quarterly_data['year'].astype(str) + 'Q' + quarterly_data['quarter'].astype(str)
        
        return quarterly_data
    return None

def main():
    """Main function to fetch and save Phillips Curve data"""
    print("=" * 60)
    print("PHILLIPS CURVE DATA FETCHER")
    print("Fetching Unemployment and Inflation Data from FRED API")
    print("=" * 60)
    
    # Fetch the data
    phillips_data = fetch_phillips_curve_data()
    
    if phillips_data is not None:
        # Save monthly data
        monthly_filename = '/Users/chen/claude-code-projects/phillips_curve_monthly_data.csv'
        save_data_to_csv(phillips_data, monthly_filename)
        
        # Create and save quarterly summary
        print("\n" + "-" * 40)
        print("Creating quarterly summary...")
        quarterly_data = create_quarterly_summary(phillips_data)
        
        if quarterly_data is not None:
            quarterly_filename = '/Users/chen/claude-code-projects/phillips_curve_quarterly_data.csv'
            save_data_to_csv(quarterly_data, quarterly_filename)
        
        print("\n" + "=" * 60)
        print("DATA DOWNLOAD COMPLETE!")
        print("=" * 60)
        print("Files created:")
        print(f"📁 Monthly data: phillips_curve_monthly_data.csv")
        print(f"📁 Quarterly data: phillips_curve_quarterly_data.csv")
        print("\nData columns include:")
        print("  • date - timestamp")
        print("  • unemployment_rate - monthly unemployment rate (%)")
        print("  • core_inflation_rate - year-over-year core CPI inflation (%)")
        print("  • headline_inflation_rate - year-over-year headline CPI inflation (%)")
        print("  • inflation_differential - headline minus core inflation")
        print("  • unemployment_gap - deviation from 10-year moving average")
        print("  • year, decade, quarter, month - time period identifiers")
        
    else:
        print("\n❌ Data fetch failed. Please:")
        print("1. Get a FRED API key at: https://fred.stlouisfed.org/docs/api/api_key.html")
        print("2. Replace 'YOUR_FRED_API_KEY' with your actual key")
        print("3. Run the script again")

if __name__ == "__main__":
    main()