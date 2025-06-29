#!/usr/bin/env python3
"""
Federal Reserve Policy Data Analyzer
Fetches key economic indicators from FRED API for portfolio strategy analysis
"""

import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

class FREDAnalyzer:
    """Fetch and analyze Federal Reserve economic data from FRED API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.stlouisfed.org/fred"
        self.session = requests.Session()
        
    def fetch_series(self, series_id: str, start_date: str = None, 
                    end_date: str = None) -> pd.DataFrame:
        """Fetch time series data from FRED API"""
        
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365*5)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        url = f"{self.base_url}/series/observations"
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json',
            'observation_start': start_date,
            'observation_end': end_date
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'observations' not in data:
                print(f"No data found for series {series_id}")
                return pd.DataFrame()
                
            df = pd.DataFrame(data['observations'])
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df = df.dropna(subset=['value'])
            df = df.set_index('date').sort_index()
            
            return df[['value']].rename(columns={'value': series_id})
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {series_id}: {e}")
            return pd.DataFrame()
    
    def get_fed_policy_data(self) -> Dict[str, pd.DataFrame]:
        """Fetch key Federal Reserve policy indicators"""
        
        # Key economic indicators for portfolio analysis
        indicators = {
            'Federal Funds Rate': 'FEDFUNDS',
            '10-Year Treasury': 'GS10', 
            '2-Year Treasury': 'GS2',
            'Unemployment Rate': 'UNRATE',
            'Core CPI': 'CPILFESL',
            'Core PCE': 'PCEPILFE',
            'GDP Growth': 'GDPC1',
            'Consumer Sentiment': 'UMCSENT',
            'VIX': 'VIXCLS',
            'DXY Dollar Index': 'DEXUSEU'
        }
        
        print("Fetching Federal Reserve policy indicators...")
        data = {}
        
        for name, series_id in indicators.items():
            print(f"  Fetching {name} ({series_id})...")
            df = self.fetch_series(series_id)
            if not df.empty:
                data[name] = df
                print(f"    ✓ Got {len(df)} observations")
            else:
                print(f"    ✗ No data available")
                
        return data
    
    def analyze_policy_trends(self, data: Dict[str, pd.DataFrame]) -> Dict:
        """Analyze recent trends in policy indicators"""
        
        analysis = {}
        
        for indicator, df in data.items():
            if df.empty:
                continue
                
            recent_data = df.last('90D')  # Last 90 days
            year_data = df.last('365D')   # Last year
            
            if len(recent_data) > 1 and len(year_data) > 1:
                recent_change = ((recent_data.iloc[-1].values[0] - recent_data.iloc[0].values[0]) 
                               / recent_data.iloc[0].values[0] * 100)
                year_change = ((year_data.iloc[-1].values[0] - year_data.iloc[0].values[0]) 
                             / year_data.iloc[0].values[0] * 100)
                
                analysis[indicator] = {
                    'current_value': round(df.iloc[-1].values[0], 2),
                    'recent_change_pct': round(recent_change, 2),
                    'year_change_pct': round(year_change, 2),
                    'last_updated': df.index[-1].strftime('%Y-%m-%d')
                }
        
        return analysis
    
    def create_policy_dashboard(self, data: Dict[str, pd.DataFrame], 
                              save_path: str = 'fed_policy_dashboard.png'):
        """Create visualization dashboard for client presentation"""
        
        fig, axes = plt.subplots(3, 2, figsize=(15, 12))
        fig.suptitle('Federal Reserve Policy Indicators Dashboard', fontsize=16, fontweight='bold')
        
        # Plot key indicators
        plot_configs = [
            ('Federal Funds Rate', 0, 0, 'Interest Rate %'),
            ('10-Year Treasury', 0, 1, 'Yield %'),
            ('Unemployment Rate', 1, 0, 'Rate %'),
            ('Core CPI', 1, 1, 'YoY % Change'),
            ('Consumer Sentiment', 2, 0, 'Index'),
            ('VIX', 2, 1, 'Volatility Index')
        ]
        
        for indicator, row, col, ylabel in plot_configs:
            ax = axes[row, col]
            if indicator in data and not data[indicator].empty:
                df = data[indicator].last('730D')  # Last 2 years
                ax.plot(df.index, df.iloc[:, 0], linewidth=2, color='steelblue')
                ax.set_title(indicator, fontweight='bold')
                ax.set_ylabel(ylabel)
                ax.grid(True, alpha=0.3)
                ax.tick_params(axis='x', rotation=45)
                
                # Add current value annotation
                current = df.iloc[-1, 0]
                ax.annotate(f'Current: {current:.2f}', 
                          xy=(df.index[-1], current),
                          xytext=(10, 10), textcoords='offset points',
                          bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                          fontsize=9, fontweight='bold')
            else:
                ax.text(0.5, 0.5, 'Data Not Available', transform=ax.transAxes,
                       ha='center', va='center', fontsize=12)
                ax.set_title(indicator, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Dashboard saved as {save_path}")
        
        return fig
    
    def generate_portfolio_insights(self, analysis: Dict) -> str:
        """Generate portfolio strategy insights for client presentation"""
        
        insights = []
        insights.append("=== FEDERAL RESERVE POLICY IMPACT ANALYSIS ===\n")
        insights.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        
        # Interest Rate Environment
        if 'Federal Funds Rate' in analysis:
            ffr = analysis['Federal Funds Rate']
            insights.append("🏦 INTEREST RATE ENVIRONMENT:")
            insights.append(f"   Current Fed Funds Rate: {ffr['current_value']}%")
            insights.append(f"   3-Month Change: {ffr['recent_change_pct']:+.2f}%")
            insights.append(f"   1-Year Change: {ffr['year_change_pct']:+.2f}%")
            
            if ffr['recent_change_pct'] > 0.5:
                insights.append("   📈 RISING RATES: Consider duration risk in bonds, favor financials")
            elif ffr['recent_change_pct'] < -0.5:
                insights.append("   📉 FALLING RATES: Growth stocks may outperform, bond rally potential")
            else:
                insights.append("   ⚖️  STABLE RATES: Balanced approach, focus on fundamentals")
            insights.append("")
        
        # Inflation Indicators
        if 'Core CPI' in analysis:
            cpi = analysis['Core CPI']
            insights.append("📊 INFLATION ENVIRONMENT:")
            insights.append(f"   Current Core CPI: {cpi['current_value']}%")
            insights.append(f"   Recent Trend: {cpi['recent_change_pct']:+.2f}%")
            
            if cpi['current_value'] > 3.0:
                insights.append("   🚨 HIGH INFLATION: TIPS, commodities, real assets favored")
            elif cpi['current_value'] < 2.0:
                insights.append("   💰 LOW INFLATION: Growth stocks, long duration bonds attractive")
            else:
                insights.append("   🎯 TARGET INFLATION: Fed likely comfortable, balanced allocation")
            insights.append("")
        
        # Employment Situation
        if 'Unemployment Rate' in analysis:
            unemployment = analysis['Unemployment Rate']
            insights.append("👥 EMPLOYMENT SITUATION:")
            insights.append(f"   Current Unemployment: {unemployment['current_value']}%")
            insights.append(f"   Recent Change: {unemployment['recent_change_pct']:+.2f}%")
            
            if unemployment['current_value'] < 4.0:
                insights.append("   💪 STRONG LABOR MARKET: Consumer discretionary, wage inflation risk")
            elif unemployment['current_value'] > 6.0:
                insights.append("   ⚠️  WEAK LABOR MARKET: Defensive positioning, Fed may ease")
            else:
                insights.append("   ✅ BALANCED LABOR MARKET: Goldilocks scenario for equities")
            insights.append("")
        
        # Market Sentiment
        if 'VIX' in analysis:
            vix = analysis['VIX']
            insights.append("📈 MARKET SENTIMENT:")
            insights.append(f"   Current VIX: {vix['current_value']}")
            
            if vix['current_value'] > 25:
                insights.append("   😰 HIGH VOLATILITY: Risk-off sentiment, defensive assets")
            elif vix['current_value'] < 15:
                insights.append("   😌 LOW VOLATILITY: Complacency risk, consider hedges")
            else:
                insights.append("   😐 MODERATE VOLATILITY: Normal market conditions")
            insights.append("")
        
        # Portfolio Recommendations
        insights.append("🎯 PORTFOLIO STRATEGY RECOMMENDATIONS:")
        
        # Determine overall regime
        if 'Federal Funds Rate' in analysis and 'Core CPI' in analysis:
            ffr_rising = analysis['Federal Funds Rate']['recent_change_pct'] > 0
            inflation_high = analysis['Core CPI']['current_value'] > 2.5
            
            if ffr_rising and inflation_high:
                insights.append("   • HAWKISH FED REGIME: Reduce duration, favor value over growth")
                insights.append("   • Overweight: Financials, Energy, Short-term bonds")
                insights.append("   • Underweight: Long duration bonds, High P/E growth stocks")
            elif not ffr_rising and not inflation_high:
                insights.append("   • DOVISH FED REGIME: Risk-on positioning appropriate")
                insights.append("   • Overweight: Technology, Consumer Discretionary, Long bonds")
                insights.append("   • Underweight: Utilities, REITs (rate sensitive)")
            else:
                insights.append("   • TRANSITIONAL REGIME: Maintain balanced approach")
                insights.append("   • Focus on quality companies with pricing power")
        
        insights.append("\n📋 KEY MONITORING POINTS:")
        insights.append("   • Watch for Fed communication changes (dot plot, minutes)")
        insights.append("   • Monitor labor market data (NFP, JOLTS, wages)")
        insights.append("   • Track inflation expectations (5Y5Y, TIPS breakevens)")
        insights.append("   • Observe yield curve shape and credit spreads")
        
        return "\n".join(insights)

def create_demo_data():
    """Create demo data for urgent analysis when API key not available"""
    import numpy as np
    
    # Create sample data based on current economic conditions (as of 2024)
    dates = pd.date_range(start='2019-01-01', end='2024-06-01', freq='M')
    n_periods = len(dates)
    
    demo_data = {}
    
    # Create consistent time series for all indicators
    np.random.seed(42)  # For reproducible demo data
    
    # Federal Funds Rate - Current: ~5.25%
    ffr_base = np.concatenate([
        np.linspace(2.5, 0.25, 12),     # 2019 cuts
        np.repeat(0.25, 24),            # Zero rate period
        np.linspace(0.25, 5.25, n_periods - 36)  # Recent hikes
    ])
    demo_data['Federal Funds Rate'] = pd.DataFrame(
        {'value': ffr_base}, index=dates
    )
    
    # 10-Year Treasury - Current: ~4.5%
    treasury_base = np.concatenate([
        np.linspace(2.7, 0.7, 12),      # Initial decline
        np.linspace(0.7, 4.5, n_periods - 12)  # Recovery and surge
    ])
    demo_data['10-Year Treasury'] = pd.DataFrame(
        {'value': treasury_base}, index=dates
    )
    
    # Unemployment Rate - Current: ~3.7%
    unemp_base = np.concatenate([
        [3.7] * 3,                      # Pre-COVID
        [14.8, 11.1, 8.4],            # COVID spike and recovery
        np.linspace(8.4, 3.7, n_periods - 6)  # Continued recovery
    ])
    demo_data['Unemployment Rate'] = pd.DataFrame(
        {'value': unemp_base}, index=dates
    )
    
    # Core CPI - Current: ~3.8%
    cpi_base = np.concatenate([
        [2.1] * 12,                     # Pre-COVID stable
        np.linspace(2.1, 1.6, 12),      # COVID decline
        np.linspace(1.6, 6.6, 12),      # Inflation surge
        np.linspace(6.6, 3.8, n_periods - 36)  # Recent decline
    ])
    demo_data['Core CPI'] = pd.DataFrame(
        {'value': cpi_base}, index=dates
    )
    
    # VIX - Current: ~18
    vix_base = np.concatenate([
        np.random.normal(15, 2, 3),      # Pre-COVID calm
        [80, 50, 35],                   # COVID volatility spike
        np.random.normal(18, 4, n_periods - 6)  # Post-COVID normal
    ])
    demo_data['VIX'] = pd.DataFrame(
        {'value': np.abs(vix_base)}, index=dates
    )
    
    # Consumer Sentiment - Current: ~75
    sentiment_base = np.concatenate([
        [95] * 3,                       # Pre-COVID high
        np.linspace(95, 70, 12),        # COVID decline
        np.linspace(70, 75, n_periods - 15)  # Gradual recovery
    ])
    demo_data['Consumer Sentiment'] = pd.DataFrame(
        {'value': sentiment_base}, index=dates
    )
    
    return demo_data

def main():
    """Main execution function"""
    
    print("Federal Reserve Policy Analyzer")
    print("=" * 50)
    
    # Check for API key in environment or use demo mode
    import os
    api_key = os.environ.get('FRED_API_KEY', '')
    
    if not api_key:
        print("⚠️  No API key found. Using demo mode for urgent analysis.")
        print("Demo data reflects approximate current economic conditions.\n")
        
        # Use demo data
        policy_data = create_demo_data()
        print("✅ Demo data loaded successfully")
        
    else:
        # Initialize analyzer with real API
        analyzer = FREDAnalyzer(api_key)
        policy_data = analyzer.get_fed_policy_data()
        
        if not policy_data:
            print("❌ API failed. Falling back to demo mode...")
            policy_data = create_demo_data()
    
    if not policy_data:
        print("❌ No data available.")
        return
    
    # Create dummy analyzer for demo mode
    analyzer = FREDAnalyzer(api_key) if api_key else FREDAnalyzer("demo")
    
    # Analyze trends
    print("\nAnalyzing policy trends...")
    analysis = analyzer.analyze_policy_trends(policy_data)
    
    # Create dashboard
    print("Creating policy dashboard...")
    analyzer.create_policy_dashboard(policy_data)
    
    # Generate insights
    print("Generating portfolio insights...")
    insights = analyzer.generate_portfolio_insights(analysis)
    
    # Save insights to file
    with open('fed_policy_insights.txt', 'w') as f:
        f.write(insights)
    
    print(f"\n{insights}")
    print(f"\n✅ Analysis complete!")
    print(f"📊 Dashboard saved: fed_policy_dashboard.png")
    print(f"📝 Insights saved: fed_policy_insights.txt")

if __name__ == "__main__":
    main()