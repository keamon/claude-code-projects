import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import sqlite3
from scipy import stats
import os

def fetch_unemployment_data(api_key, start_date=None, end_date=None):
    """Fetch unemployment rate data from FRED API"""
    base_url = "https://api.stlouisfed.org/fred/series/observations"
    
    params = {
        'series_id': 'UNRATE',  # Unemployment Rate
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
        
        df = pd.DataFrame(observations)
        df['date'] = pd.to_datetime(df['date'])
        df['unemployment_rate'] = pd.to_numeric(df['value'], errors='coerce')
        df = df.dropna(subset=['unemployment_rate'])
        df = df[['date', 'unemployment_rate']].sort_values('date')
        
        return df
        
    except Exception as e:
        print(f"Error fetching unemployment data: {e}")
        return None

def load_inflation_data():
    """Load inflation data from SQLite database"""
    try:
        conn = sqlite3.connect('inflation_data.db')
        query = """
        SELECT date, inflation_rate 
        FROM cpi_data 
        WHERE inflation_rate IS NOT NULL
        ORDER BY date
        """
        df = pd.read_sql_query(query, conn)
        df['date'] = pd.to_datetime(df['date'])
        conn.close()
        return df
    except Exception as e:
        print(f"Error loading inflation data: {e}")
        return None

def combine_data(inflation_df, unemployment_df):
    """Combine inflation and unemployment data"""
    # Merge on date
    combined = pd.merge(inflation_df, unemployment_df, on='date', how='inner')
    combined = combined.sort_values('date')
    return combined

def calculate_rolling_correlation(df, window=36):
    """Calculate rolling correlation between inflation and unemployment"""
    df['rolling_corr'] = df['inflation_rate'].rolling(window=window).corr(df['unemployment_rate'])
    return df

def analyze_phillips_curve_periods(df):
    """Analyze Phillips Curve for different time periods"""
    periods = {
        '2020-2021 Pandemic': ('2020-01-01', '2021-12-31'),
        '2022 High Inflation': ('2022-01-01', '2022-12-31'),
        '2023-2024 Normalization': ('2023-01-01', '2024-12-31'),
        '2025 Current': ('2025-01-01', '2025-12-31')
    }
    
    results = {}
    
    for period_name, (start, end) in periods.items():
        period_data = df[(df['date'] >= start) & (df['date'] <= end)]
        
        if len(period_data) > 5:  # Need minimum data points
            corr, p_value = stats.pearsonr(period_data['inflation_rate'], 
                                         period_data['unemployment_rate'])
            
            # Linear regression for slope
            slope, intercept, r_value, p_val, std_err = stats.linregress(
                period_data['unemployment_rate'], period_data['inflation_rate']
            )
            
            results[period_name] = {
                'correlation': corr,
                'p_value': p_value,
                'slope': slope,
                'r_squared': r_value**2,
                'n_observations': len(period_data),
                'data': period_data
            }
    
    return results

def create_phillips_curve_visualization(results):
    """Create comprehensive Phillips Curve visualization"""
    
    # Set up the plotting style
    plt.style.use('seaborn-v0_8')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Evolution of the Phillips Curve: Demonstrating Flattening Over Time', 
                 fontsize=16, fontweight='bold')
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    # Plot each period
    for i, (period_name, data) in enumerate(results.items()):
        row, col = divmod(i, 2)
        ax = axes[row, col]
        
        period_data = data['data']
        
        # Scatter plot
        ax.scatter(period_data['unemployment_rate'], period_data['inflation_rate'], 
                  alpha=0.7, color=colors[i], s=30)
        
        # Trend line
        x = period_data['unemployment_rate']
        y = period_data['inflation_rate']
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        ax.plot(x, p(x), color=colors[i], linewidth=2, linestyle='--')
        
        # Formatting
        ax.set_xlabel('Unemployment Rate (%)')
        ax.set_ylabel('Inflation Rate (%)')
        ax.set_title(f'{period_name}\nCorr: {data["correlation"]:.3f}, Slope: {data["slope"]:.3f}')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('phillips_curve_evolution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create summary correlation plot
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    
    periods = list(results.keys())
    correlations = [results[p]['correlation'] for p in periods]
    slopes = [abs(results[p]['slope']) for p in periods]
    
    x = range(len(periods))
    
    # Plot correlations and slopes
    ax2 = ax.twinx()
    
    bars1 = ax.bar([i - 0.2 for i in x], correlations, 0.4, 
                   label='Correlation', alpha=0.7, color='blue')
    bars2 = ax2.bar([i + 0.2 for i in x], slopes, 0.4, 
                    label='Absolute Slope', alpha=0.7, color='red')
    
    ax.set_xlabel('Time Period')
    ax.set_ylabel('Correlation Coefficient', color='blue')
    ax2.set_ylabel('Absolute Slope', color='red')
    ax.set_title('Phillips Curve Flattening: Declining Correlation and Slope Over Time')
    
    ax.set_xticks(x)
    ax.set_xticklabels(periods, rotation=45, ha='right')
    
    # Add value labels on bars
    for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
        height1 = bar1.get_height()
        height2 = bar2.get_height()
        ax.text(bar1.get_x() + bar1.get_width()/2., height1 + 0.01,
                f'{height1:.3f}', ha='center', va='bottom')
        ax2.text(bar2.get_x() + bar2.get_width()/2., height2 + 0.01,
                f'{height2:.3f}', ha='center', va='bottom')
    
    ax.legend(loc='upper left')
    ax2.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('phillips_curve_flattening_summary.png', dpi=300, bbox_inches='tight')
    plt.close()

def print_analysis_summary(results):
    """Print detailed analysis summary"""
    print("\n" + "="*80)
    print("PHILLIPS CURVE FLATTENING ANALYSIS")
    print("="*80)
    
    print("\nThe Phillips Curve shows the relationship between inflation and unemployment.")
    print("A 'flattening' curve indicates weakening correlation over time.\n")
    
    for period_name, data in results.items():
        print(f"{period_name}:")
        print(f"  Correlation: {data['correlation']:.4f}")
        print(f"  P-value: {data['p_value']:.4f}")
        print(f"  Slope: {data['slope']:.4f}")
        print(f"  R-squared: {data['r_squared']:.4f}")
        print(f"  Observations: {data['n_observations']}")
        
        # Interpretation
        if abs(data['correlation']) > 0.5:
            strength = "Strong"
        elif abs(data['correlation']) > 0.3:
            strength = "Moderate"
        else:
            strength = "Weak"
        
        direction = "negative" if data['correlation'] < 0 else "positive"
        print(f"  Interpretation: {strength} {direction} relationship")
        print()
    
    # Calculate flattening metrics
    correlations = [abs(data['correlation']) for data in results.values()]
    slopes = [abs(data['slope']) for data in results.values()]
    
    corr_decline = correlations[0] - correlations[-1] if len(correlations) > 1 else 0
    slope_decline = slopes[0] - slopes[-1] if len(slopes) > 1 else 0
    
    print("FLATTENING EVIDENCE:")
    print(f"  Correlation decline from first to last period: {corr_decline:.4f}")
    print(f"  Slope decline from first to last period: {slope_decline:.4f}")
    
    if corr_decline > 0.1 and slope_decline > 0.1:
        print("  CONCLUSION: Strong evidence of Phillips Curve flattening")
    elif corr_decline > 0.05 or slope_decline > 0.05:
        print("  CONCLUSION: Moderate evidence of Phillips Curve flattening")
    else:
        print("  CONCLUSION: Limited evidence of Phillips Curve flattening")

def main():
    # Get API key
    api_key = os.environ.get('FRED_API_KEY')
    if not api_key:
        api_key = input("Enter your FRED API key: ").strip()
    
    if not api_key:
        print("API key required. Exiting.")
        return
    
    print("Fetching unemployment data from FRED...")
    
    # Fetch data for recent period to match our inflation data
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = '2020-01-01'  # Match our inflation data period
    
    unemployment_df = fetch_unemployment_data(api_key, start_date, end_date)
    if unemployment_df is None:
        print("Failed to fetch unemployment data")
        return
    
    print("Loading inflation data from database...")
    inflation_df = load_inflation_data()
    if inflation_df is None:
        print("Failed to load inflation data")
        return
    
    print("Combining and analyzing data...")
    combined_df = combine_data(inflation_df, unemployment_df)
    
    if len(combined_df) < 20:
        print("Insufficient overlapping data for analysis")
        return
    
    print(f"Analyzing {len(combined_df)} overlapping observations...")
    
    # Analyze different periods
    results = analyze_phillips_curve_periods(combined_df)
    
    # Print summary
    print_analysis_summary(results)
    
    # Create visualizations
    print("\nCreating visualizations...")
    create_phillips_curve_visualization(results)
    
    # Save combined data to database
    print("\nSaving combined data to database...")
    conn = sqlite3.connect('inflation_data.db')
    combined_df.to_sql('phillips_curve_data', conn, if_exists='replace', index=False)
    conn.close()
    
    print("Analysis complete! Check the generated PNG files for visualizations.")

if __name__ == "__main__":
    main()