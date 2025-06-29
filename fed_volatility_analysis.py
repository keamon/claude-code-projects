import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from fredapi import Fred
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Initialize FRED API (requires API key)
fred = Fred(api_key='YOUR_FRED_API_KEY')

def fetch_fed_data():
    """Fetch Federal Reserve policy data from FRED"""
    print("Fetching Federal Reserve data...")
    
    # Federal Funds Rate
    fed_funds = fred.get_series('FEDFUNDS', start='1990-01-01')
    
    # 10-Year Treasury Rate (policy indicator)
    treasury_10y = fred.get_series('GS10', start='1990-01-01')
    
    # Real GDP Growth (economic context)
    gdp_growth = fred.get_series('A191RL1Q225SBEA', start='1990-01-01')
    
    return fed_funds, treasury_10y, gdp_growth

def fetch_volatility_data():
    """Fetch market volatility data from FRED"""
    print("Fetching volatility data...")
    
    # VIX Volatility Index
    vix = fred.get_series('VIXCLS', start='1990-01-01')
    
    # S&P 500 for context
    sp500 = fred.get_series('SP500', start='1990-01-01')
    
    return vix, sp500

def calculate_policy_changes(fed_funds):
    """Identify significant Fed policy changes"""
    # Calculate month-over-month changes
    policy_changes = fed_funds.diff()
    
    # Identify significant changes (>= 0.25% or <= -0.25%)
    significant_changes = policy_changes[abs(policy_changes) >= 0.25]
    
    return significant_changes

def analyze_volatility_response(vix, policy_changes, window_days=30):
    """Analyze VIX response to Fed policy changes"""
    results = []
    
    for date, change in policy_changes.items():
        # Get VIX before and after policy change
        start_date = date - timedelta(days=window_days)
        end_date = date + timedelta(days=window_days)
        
        # Filter VIX data around policy change
        vix_window = vix[(vix.index >= start_date) & (vix.index <= end_date)]
        
        if len(vix_window) > 0:
            vix_before = vix_window[vix_window.index <= date].mean()
            vix_after = vix_window[vix_window.index > date].mean()
            
            results.append({
                'date': date,
                'policy_change': change,
                'vix_before': vix_before,
                'vix_after': vix_after,
                'vix_change': vix_after - vix_before,
                'vix_pct_change': (vix_after - vix_before) / vix_before * 100
            })
    
    return pd.DataFrame(results)

def calculate_correlations(fed_funds, vix):
    """Calculate correlations between Fed rates and volatility"""
    # Align data by date
    combined = pd.DataFrame({
        'fed_funds': fed_funds,
        'vix': vix
    }).dropna()
    
    # Calculate correlations
    correlation = combined['fed_funds'].corr(combined['vix'])
    
    # Rolling correlation (1-year window)
    rolling_corr = combined['fed_funds'].rolling(window=252).corr(combined['vix'])
    
    return correlation, rolling_corr, combined

def generate_portfolio_insights(analysis_df):
    """Generate portfolio strategy insights"""
    insights = {
        'rate_hikes_avg_vix_increase': analysis_df[analysis_df['policy_change'] > 0]['vix_pct_change'].mean(),
        'rate_cuts_avg_vix_change': analysis_df[analysis_df['policy_change'] < 0]['vix_pct_change'].mean(),
        'volatility_predictive_power': abs(analysis_df['vix_pct_change'].mean()),
        'risk_management_threshold': analysis_df['vix_change'].std() * 2
    }
    
    return insights

def create_visualizations(fed_funds, vix, analysis_df, rolling_corr):
    """Create visualizations for presentation"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Fed Funds Rate and VIX over time
    ax1 = axes[0, 0]
    ax1_twin = ax1.twinx()
    
    ax1.plot(fed_funds.index, fed_funds.values, 'b-', label='Fed Funds Rate', linewidth=2)
    ax1_twin.plot(vix.index, vix.values, 'r-', label='VIX', alpha=0.7)
    
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Fed Funds Rate (%)', color='b')
    ax1_twin.set_ylabel('VIX', color='r')
    ax1.set_title('Federal Funds Rate vs VIX Over Time')
    ax1.legend(loc='upper left')
    ax1_twin.legend(loc='upper right')
    
    # Policy change impact on VIX
    ax2 = axes[0, 1]
    rate_hikes = analysis_df[analysis_df['policy_change'] > 0]
    rate_cuts = analysis_df[analysis_df['policy_change'] < 0]
    
    ax2.scatter(rate_hikes['policy_change'], rate_hikes['vix_pct_change'], 
               color='red', alpha=0.7, label='Rate Hikes', s=60)
    ax2.scatter(rate_cuts['policy_change'], rate_cuts['vix_pct_change'], 
               color='green', alpha=0.7, label='Rate Cuts', s=60)
    
    ax2.set_xlabel('Policy Change (%)')
    ax2.set_ylabel('VIX Change (%)')
    ax2.set_title('Policy Changes vs VIX Response')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Rolling correlation
    ax3 = axes[1, 0]
    ax3.plot(rolling_corr.index, rolling_corr.values, 'purple', linewidth=2)
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Correlation')
    ax3.set_title('1-Year Rolling Correlation: Fed Funds vs VIX')
    ax3.grid(True, alpha=0.3)
    ax3.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    # VIX distribution around policy changes
    ax4 = axes[1, 1]
    ax4.hist(analysis_df['vix_pct_change'], bins=20, alpha=0.7, color='orange', edgecolor='black')
    ax4.set_xlabel('VIX Percentage Change (%)')
    ax4.set_ylabel('Frequency')
    ax4.set_title('Distribution of VIX Changes After Policy Changes')
    ax4.axvline(x=analysis_df['vix_pct_change'].mean(), color='red', 
               linestyle='--', label=f'Mean: {analysis_df["vix_pct_change"].mean():.1f}%')
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig('/Users/chen/claude-code-projects/fed_volatility_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """Main analysis function"""
    print("Starting Federal Reserve Policy & Market Volatility Analysis")
    print("=" * 60)
    
    try:
        # Fetch data
        fed_funds, treasury_10y, gdp_growth = fetch_fed_data()
        vix, sp500 = fetch_volatility_data()
        
        print(f"Data periods:")
        print(f"Fed Funds Rate: {fed_funds.index[0]} to {fed_funds.index[-1]}")
        print(f"VIX: {vix.index[0]} to {vix.index[-1]}")
        
        # Analyze policy changes
        policy_changes = calculate_policy_changes(fed_funds)
        print(f"\nIdentified {len(policy_changes)} significant policy changes")
        
        # Analyze volatility response
        analysis_df = analyze_volatility_response(vix, policy_changes)
        
        # Calculate correlations
        correlation, rolling_corr, combined_data = calculate_correlations(fed_funds, vix)
        
        # Generate insights
        insights = generate_portfolio_insights(analysis_df)
        
        # Print key findings
        print("\nKEY FINDINGS FOR PORTFOLIO STRATEGY:")
        print("=" * 40)
        print(f"Overall Fed Funds-VIX Correlation: {correlation:.3f}")
        print(f"Rate Hikes → Avg VIX Increase: {insights['rate_hikes_avg_vix_increase']:.1f}%")
        print(f"Rate Cuts → Avg VIX Change: {insights['rate_cuts_avg_vix_change']:.1f}%")
        print(f"Risk Management Threshold: ±{insights['risk_management_threshold']:.1f} VIX points")
        
        # Portfolio recommendations
        print("\nPORTFOLIO STRATEGY RECOMMENDATIONS:")
        print("=" * 35)
        if insights['rate_hikes_avg_vix_increase'] > 5:
            print("• DEFENSIVE POSITIONING: Rate hikes typically increase volatility")
            print("• Consider increasing cash/bond allocation before Fed meetings")
            print("• Hedge equity exposure with VIX calls or protective puts")
        
        if insights['rate_cuts_avg_vix_change'] < -5:
            print("• OPPORTUNISTIC POSITIONING: Rate cuts may reduce volatility")
            print("• Consider increasing equity allocation on rate cut expectations")
            print("• Sell volatility (VIX puts) in rate-cutting cycles")
        
        print(f"• Monitor VIX > {vix.mean() + insights['risk_management_threshold']:.0f} for defensive triggers")
        
        # Create visualizations
        create_visualizations(fed_funds, vix, analysis_df, rolling_corr)
        
        # Save detailed analysis
        analysis_df.to_csv('/Users/chen/claude-code-projects/fed_policy_volatility_analysis.csv', index=False)
        
        print(f"\nAnalysis complete! Charts saved to: fed_volatility_analysis.png")
        print(f"Detailed data saved to: fed_policy_volatility_analysis.csv")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Note: You need a FRED API key. Get one free at: https://fred.stlouisfed.org/docs/api/api_key.html")

if __name__ == "__main__":
    main()