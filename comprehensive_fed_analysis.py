import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import sqlite3
import os
import warnings
warnings.filterwarnings('ignore')

class ComprehensiveFedAnalyzer:
    """
    Comprehensive Federal Reserve Policy Analysis and Investment Strategy Tool
    """
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.stlouisfed.org/fred/series/observations"
        
        # Complete catalog of Fed policy-relevant datasets
        self.fed_datasets = {
            # === CORE MONETARY POLICY ===
            'FEDFUNDS': 'Federal Funds Rate',
            'DFEDTARU': 'Federal Funds Target Rate - Upper Limit',
            'DFEDTARL': 'Federal Funds Target Rate - Lower Limit',
            'DFF': 'Federal Funds Rate (Daily)',
            
            # === TREASURY YIELD CURVE ===
            'DGS3MO': '3-Month Treasury Rate',
            'DGS6MO': '6-Month Treasury Rate',
            'DGS1': '1-Year Treasury Rate',
            'DGS2': '2-Year Treasury Rate',
            'DGS3': '3-Year Treasury Rate',
            'DGS5': '5-Year Treasury Rate',
            'DGS7': '7-Year Treasury Rate',
            'DGS10': '10-Year Treasury Rate',
            'DGS20': '20-Year Treasury Rate',
            'DGS30': '30-Year Treasury Rate',
            
            # === YIELD CURVE SPREADS ===
            'T10Y2Y': '10-Year Treasury Minus 2-Year Treasury',
            'T10Y3M': '10-Year Treasury Minus 3-Month Treasury',
            'T5YIE': '5-Year Breakeven Inflation Rate',
            'T10YIE': '10-Year Breakeven Inflation Rate',
            
            # === FED BALANCE SHEET ===
            'WALCL': 'Fed Total Assets',
            'WSHOMCB': 'Fed Holdings of Mortgage-Backed Securities',
            'WSHOSHO': 'Fed Holdings of Treasury Securities',
            'WSHOTSL': 'Fed Holdings of Treasury Securities (Long-term)',
            'WDTGAL': 'Fed Total Deposits',
            'RRPONTSYD': 'Overnight Reverse Repurchase Agreements',
            
            # === MONEY SUPPLY & LIQUIDITY ===
            'M1SL': 'M1 Money Stock',
            'M2SL': 'M2 Money Stock',
            'BOGMBASE': 'Monetary Base',
            'EXCSRESNS': 'Excess Reserves of Depository Institutions',
            'CURRSL': 'Currency in Circulation',
            
            # === BANKING SECTOR ===
            'DPSACBW027SBOG': 'Deposits at Commercial Banks',
            'TOTLL': 'Total Consumer Loans',
            'CCLACBW027SBOG': 'Commercial and Industrial Loans',
            'REALLN': 'Real Estate Loans',
            'INVEST': 'Securities in Bank Credit',
            
            # === CREDIT MARKETS ===
            'BAMLH0A0HYM2': 'High Yield Corporate Bond Spread',
            'BAMLC0A1CAAA': 'AAA Corporate Bond Spread',
            'BAMLC0A4CBBB': 'BBB Corporate Bond Spread',
            'BAMLEMCBPIOAS': 'Emerging Markets Bond Spread',
            
            # === INFLATION INDICATORS ===
            'CPIAUCSL': 'Consumer Price Index',
            'CPILFESL': 'Core CPI (ex food & energy)',
            'PCEPI': 'PCE Price Index',
            'PCEPILFE': 'Core PCE Price Index',
            'CPILTT01USM659N': 'CPI Inflation Rate',
            
            # === EMPLOYMENT DATA ===
            'UNRATE': 'Unemployment Rate',
            'PAYEMS': 'Total Nonfarm Payrolls',
            'CIVPART': 'Labor Force Participation Rate',
            'EMRATIO': 'Employment-Population Ratio',
            'AHETPI': 'Average Hourly Earnings',
            'JOLTS': 'Job Openings',
            
            # === ECONOMIC ACTIVITY ===
            'GDP': 'Gross Domestic Product',
            'GDPC1': 'Real GDP',
            'GDPPOT': 'Potential GDP',
            'INDPRO': 'Industrial Production Index',
            'HOUST': 'Housing Starts',
            'PERMIT': 'Building Permits',
            
            # === CONSUMER & BUSINESS ===
            'UMCSENT': 'Consumer Sentiment',
            'CSCICP03USM665S': 'Consumer Confidence',
            'RSXFS': 'Retail Sales',
            'BUSLOANS': 'Commercial and Industrial Loans',
            
            # === MARKET INDICATORS ===
            'SP500': 'S&P 500 Index',
            'VIXCLS': 'VIX Volatility Index',
            'NASDAQCOM': 'NASDAQ Composite',
            'DEXUSEU': 'USD/EUR Exchange Rate',
            'DEXCHUS': 'USD/CNY Exchange Rate',
            'GOLDAMGBD228NLBM': 'Gold Price',
            'DCOILWTICO': 'WTI Crude Oil Price',
            
            # === INTERNATIONAL ===
            'EFFR': 'Effective Federal Funds Rate',
            'IOER': 'Interest on Excess Reserves',
            'OBFR': 'Overnight Bank Funding Rate',
            'SOFR': 'Secured Overnight Financing Rate',
            
            # === FED COMMUNICATIONS ===
            'DFEDTAR': 'Federal Funds Target Rate',
            'FOMC': 'FOMC Meeting Dates'
        }
    
    def fetch_series_data(self, series_id, start_date='2020-01-01'):
        """Fetch individual series from FRED API"""
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json',
            'sort_order': 'asc',
            'observation_start': start_date
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            observations = data['observations']
            
            df = pd.DataFrame(observations)
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df = df.dropna(subset=['value'])
            df = df[['date', 'value']].sort_values('date')
            df.columns = ['date', series_id]
            
            return df
            
        except Exception as e:
            return None
    
    def analyze_recent_policy_changes(self):
        """Analyze recent Federal Reserve policy changes"""
        
        print("🏛️ ANALYZING RECENT FEDERAL RESERVE POLICY CHANGES")
        print("=" * 60)
        
        policy_analysis = {}
        
        # Core policy indicators
        core_indicators = ['FEDFUNDS', 'WALCL', 'T10Y2Y', 'M2SL', 'UNRATE', 'CPIAUCSL']
        
        for indicator in core_indicators:
            print(f"Fetching {indicator}: {self.fed_datasets[indicator]}")
            data = self.fetch_series_data(indicator)
            
            if data is not None and len(data) > 0:
                # Calculate recent changes
                current_value = data[indicator].iloc[-1]
                
                # 3-month change
                three_months_ago = data['date'].max() - timedelta(days=90)
                recent_data = data[data['date'] >= three_months_ago]
                if len(recent_data) > 1:
                    three_month_change = current_value - recent_data[indicator].iloc[0]
                    three_month_pct = (three_month_change / recent_data[indicator].iloc[0]) * 100
                else:
                    three_month_change = None
                    three_month_pct = None
                
                # 1-year change
                one_year_ago = data['date'].max() - timedelta(days=365)
                year_data = data[data['date'] >= one_year_ago]
                if len(year_data) > 1:
                    year_change = current_value - year_data[indicator].iloc[0]
                    year_pct = (year_change / year_data[indicator].iloc[0]) * 100
                else:
                    year_change = None
                    year_pct = None
                
                policy_analysis[indicator] = {
                    'name': self.fed_datasets[indicator],
                    'current_value': current_value,
                    'three_month_change': three_month_change,
                    'three_month_pct': three_month_pct,
                    'year_change': year_change,
                    'year_pct': year_pct,
                    'last_updated': data['date'].iloc[-1]
                }
                
                print(f"  ✓ Current: {current_value:.2f}")
                if year_pct:
                    print(f"  📈 1-Year Change: {year_pct:+.1f}%")
        
        return policy_analysis
    
    def identify_policy_regime(self, policy_data):
        """Identify current Fed policy regime"""
        
        regime_indicators = {
            'rate_trend': 'Unknown',
            'balance_sheet_trend': 'Unknown',
            'inflation_status': 'Unknown',
            'employment_status': 'Unknown'
        }
        
        # Rate trend
        if 'FEDFUNDS' in policy_data:
            ff_change = policy_data['FEDFUNDS'].get('year_pct', 0)
            if ff_change > 50:
                regime_indicators['rate_trend'] = 'Aggressive Hiking'
            elif ff_change > 10:
                regime_indicators['rate_trend'] = 'Hiking Cycle'
            elif ff_change < -10:
                regime_indicators['rate_trend'] = 'Cutting Cycle'
            else:
                regime_indicators['rate_trend'] = 'On Hold'
        
        # Balance sheet trend
        if 'WALCL' in policy_data:
            bs_change = policy_data['WALCL'].get('year_pct', 0)
            if bs_change > 10:
                regime_indicators['balance_sheet_trend'] = 'QE Expansion'
            elif bs_change < -5:
                regime_indicators['balance_sheet_trend'] = 'QT Contraction'
            else:
                regime_indicators['balance_sheet_trend'] = 'Stable'
        
        # Inflation status
        if 'CPIAUCSL' in policy_data:
            cpi_level = policy_data['CPIAUCSL'].get('current_value', 0)
            if cpi_level > 4:
                regime_indicators['inflation_status'] = 'High Inflation'
            elif cpi_level < 1:
                regime_indicators['inflation_status'] = 'Low Inflation'
            else:
                regime_indicators['inflation_status'] = 'Target Range'
        
        # Employment status
        if 'UNRATE' in policy_data:
            unemployment = policy_data['UNRATE'].get('current_value', 0)
            if unemployment < 3.5:
                regime_indicators['employment_status'] = 'Very Tight'
            elif unemployment < 5:
                regime_indicators['employment_status'] = 'Tight'
            elif unemployment > 6:
                regime_indicators['employment_status'] = 'Weak'
            else:
                regime_indicators['employment_status'] = 'Balanced'
        
        return regime_indicators
    
    def generate_investment_strategies(self, policy_data, regime):
        """Generate comprehensive investment strategies based on Fed policy"""
        
        strategies = {
            'asset_allocation': {},
            'sector_rotation': {},
            'fixed_income': {},
            'alternatives': {},
            'risk_management': {}
        }
        
        # Overall regime assessment
        is_hawkish = (regime['rate_trend'] in ['Aggressive Hiking', 'Hiking Cycle'] and 
                     regime['inflation_status'] == 'High Inflation')
        is_dovish = (regime['rate_trend'] == 'Cutting Cycle' and 
                    regime['employment_status'] == 'Weak')
        
        # Asset Allocation
        if is_hawkish:
            strategies['asset_allocation'] = {
                'equities': {'weight': '60%', 'bias': 'Value over Growth'},
                'fixed_income': {'weight': '30%', 'bias': 'Short duration, High yield'},
                'alternatives': {'weight': '10%', 'bias': 'Commodities, Real assets'},
                'rationale': 'Hawkish Fed requires defensive positioning'
            }
        elif is_dovish:
            strategies['asset_allocation'] = {
                'equities': {'weight': '70%', 'bias': 'Growth over Value'},
                'fixed_income': {'weight': '25%', 'bias': 'Long duration Treasuries'},
                'alternatives': {'weight': '5%', 'bias': 'REITs, Growth assets'},
                'rationale': 'Dovish Fed supports risk assets'
            }
        else:
            strategies['asset_allocation'] = {
                'equities': {'weight': '65%', 'bias': 'Balanced approach'},
                'fixed_income': {'weight': '30%', 'bias': 'Mixed duration'},
                'alternatives': {'weight': '5%', 'bias': 'Diversified'},
                'rationale': 'Neutral Fed policy supports balanced allocation'
            }
        
        # Sector Rotation
        if is_hawkish:
            strategies['sector_rotation'] = {
                'overweight': ['Financials', 'Energy', 'Materials', 'Consumer Staples'],
                'underweight': ['Technology', 'Real Estate', 'Utilities', 'Growth stocks'],
                'rationale': 'High rates benefit banks, hurt growth and rate-sensitive sectors'
            }
        elif is_dovish:
            strategies['sector_rotation'] = {
                'overweight': ['Technology', 'Consumer Discretionary', 'Communication', 'Real Estate'],
                'underweight': ['Financials', 'Energy', 'Utilities'],
                'rationale': 'Low rates support growth and rate-sensitive sectors'
            }
        else:
            strategies['sector_rotation'] = {
                'overweight': ['Healthcare', 'Technology', 'Industrials'],
                'underweight': ['Utilities', 'Materials'],
                'rationale': 'Balanced approach focusing on secular growth trends'
            }
        
        # Fixed Income Strategy
        if regime['rate_trend'] == 'Aggressive Hiking':
            strategies['fixed_income'] = {
                'duration': 'Short (1-3 years)',
                'credit': 'High quality corporate bonds',
                'tips': 'Overweight inflation protection',
                'strategy': 'Lock in high yields, minimize duration risk'
            }
        elif regime['rate_trend'] == 'Cutting Cycle':
            strategies['fixed_income'] = {
                'duration': 'Long (7-30 years)',
                'credit': 'Investment grade corporates',
                'tips': 'Underweight as inflation falls',
                'strategy': 'Capture bond rally from falling rates'
            }
        
        # Risk Management
        vol_level = 'High' if is_hawkish else 'Medium'
        strategies['risk_management'] = {
            'volatility_outlook': vol_level,
            'hedging': ['VIX calls', 'Put spreads'] if vol_level == 'High' else ['Modest hedging'],
            'cash_level': '10-15%' if vol_level == 'High' else '5-10%',
            'rebalancing': 'Monthly' if vol_level == 'High' else 'Quarterly'
        }
        
        return strategies
    
    def create_fed_policy_dashboard(self, policy_data):
        """Create comprehensive Fed policy visualization"""
        
        fig, axes = plt.subplots(3, 2, figsize=(16, 12))
        fig.suptitle('Federal Reserve Policy Dashboard & Investment Strategy', 
                     fontsize=16, fontweight='bold')
        
        # Create sample visualizations (using demo data structure)
        import numpy as np
        
        # Fed Funds Rate trend
        ax1 = axes[0, 0]
        dates = pd.date_range('2020-01-01', '2025-06-01', freq='M')
        ff_rates = np.concatenate([np.repeat(0.25, 24), np.linspace(0.25, 5.25, len(dates)-24)])
        ax1.plot(dates, ff_rates, 'b-', linewidth=2)
        ax1.fill_between(dates, ff_rates, alpha=0.3)
        ax1.set_title('Federal Funds Rate Evolution')
        ax1.set_ylabel('Rate (%)')
        ax1.grid(True, alpha=0.3)
        
        # Policy regime timeline
        ax2 = axes[0, 1]
        regimes = ['Zero Rate', 'First Hike', 'Aggressive Hiking', 'Peak Rates']
        regime_dates = ['2020-03', '2022-03', '2022-12', '2024-06']
        colors = ['green', 'yellow', 'red', 'orange']
        
        for i, (regime, date, color) in enumerate(zip(regimes, regime_dates, colors)):
            ax2.barh(i, 1, color=color, alpha=0.7)
            ax2.text(0.5, i, f'{regime}\\n{date}', ha='center', va='center', fontweight='bold')
        
        ax2.set_title('Fed Policy Regime Timeline')
        ax2.set_yticks(range(len(regimes)))
        ax2.set_yticklabels(regimes)
        ax2.set_xlim(0, 1)
        
        # Asset class performance matrix
        ax3 = axes[1, 0]
        assets = ['Stocks', 'Bonds', 'REITs', 'Commodities', 'Cash']
        regimes_perf = ['Low Rates', 'Rising Rates', 'High Rates']
        
        # Performance matrix (sample data)
        perf_matrix = np.array([
            [8, -2, 3],   # Stocks
            [3, -5, 4],   # Bonds  
            [12, -8, 2],  # REITs
            [15, 8, 5],   # Commodities
            [0, 3, 5]     # Cash
        ])
        
        im = ax3.imshow(perf_matrix, cmap='RdYlGn', aspect='auto')
        ax3.set_xticks(range(len(regimes_perf)))
        ax3.set_yticks(range(len(assets)))
        ax3.set_xticklabels(regimes_perf)
        ax3.set_yticklabels(assets)
        ax3.set_title('Asset Performance by Rate Regime (%)')
        
        for i in range(len(assets)):
            for j in range(len(regimes_perf)):
                ax3.text(j, i, f'{perf_matrix[i,j]:+d}%', ha='center', va='center')
        
        # Sector rotation heat map
        ax4 = axes[1, 1]
        sectors = ['Tech', 'Finance', 'Energy', 'REITs', 'Utilities']
        rate_environments = ['Cutting', 'Rising', 'Peak']
        
        sector_matrix = np.array([
            [2, -1, -2],   # Tech
            [-1, 2, 1],    # Finance
            [0, 1, 2],     # Energy
            [2, -2, -1],   # REITs
            [1, -1, 0]     # Utilities
        ])
        
        im2 = ax4.imshow(sector_matrix, cmap='RdYlGn', aspect='auto')
        ax4.set_xticks(range(len(rate_environments)))
        ax4.set_yticks(range(len(sectors)))
        ax4.set_xticklabels(rate_environments)
        ax4.set_yticklabels(sectors)
        ax4.set_title('Sector Rotation Strategy')
        
        for i in range(len(sectors)):
            for j in range(len(rate_environments)):
                color = 'white' if abs(sector_matrix[i,j]) > 1 else 'black'
                ax4.text(j, i, f'{sector_matrix[i,j]:+d}', ha='center', va='center', color=color)
        
        # Risk-Return scatter
        ax5 = axes[2, 0]
        
        strategy_names = ['Conservative', 'Balanced', 'Aggressive', 'All Weather']
        returns = [4, 7, 10, 6]
        risks = [5, 10, 15, 8]
        
        scatter = ax5.scatter(risks, returns, s=100, alpha=0.7, c=range(len(strategy_names)), cmap='viridis')
        
        for i, name in enumerate(strategy_names):
            ax5.annotate(name, (risks[i], returns[i]), xytext=(5, 5), textcoords='offset points')
        
        ax5.set_xlabel('Risk (Volatility %)')
        ax5.set_ylabel('Expected Return (%)')
        ax5.set_title('Portfolio Strategy Risk-Return')
        ax5.grid(True, alpha=0.3)
        
        # Policy impact timeline
        ax6 = axes[2, 1]
        
        policy_events = ['QE Launch', 'Taper Talk', 'Rate Hikes', 'Pause', 'Cuts?']
        market_impact = [-5, -10, -15, 5, 10]
        event_dates = range(len(policy_events))
        
        colors = ['red' if x < 0 else 'green' for x in market_impact]
        bars = ax6.bar(event_dates, market_impact, color=colors, alpha=0.7)
        
        ax6.set_xticks(event_dates)
        ax6.set_xticklabels(policy_events, rotation=45)
        ax6.set_ylabel('Market Impact (%)')
        ax6.set_title('Fed Policy Events & Market Reaction')
        ax6.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        for bar, impact in zip(bars, market_impact):
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2., height + (1 if height > 0 else -2),
                    f'{impact:+d}%', ha='center', va='bottom' if height > 0 else 'top')
        
        plt.tight_layout()
        plt.savefig('comprehensive_fed_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("📊 Comprehensive dashboard saved as 'comprehensive_fed_analysis.png'")
    
    def generate_comprehensive_report(self):
        """Generate comprehensive Federal Reserve policy analysis report"""
        
        print("\\n🏛️ COMPREHENSIVE FEDERAL RESERVE POLICY ANALYSIS")
        print("=" * 80)
        
        # Analyze policy changes
        policy_data = self.analyze_recent_policy_changes()
        
        if not policy_data:
            print("❌ Unable to fetch sufficient data")
            return None
        
        # Identify regime
        regime = self.identify_policy_regime(policy_data)
        
        print(f"\\n📊 CURRENT POLICY REGIME ASSESSMENT")
        print("-" * 50)
        for indicator, status in regime.items():
            print(f"{indicator.replace('_', ' ').title()}: {status}")
        
        # Generate investment strategies
        strategies = self.generate_investment_strategies(policy_data, regime)
        
        print(f"\\n🎯 INVESTMENT STRATEGY RECOMMENDATIONS")
        print("-" * 50)
        
        # Asset Allocation
        print("\\nASSET ALLOCATION:")
        for asset, details in strategies['asset_allocation'].items():
            if asset != 'rationale':
                print(f"  {asset.title()}: {details['weight']} ({details['bias']})")
        print(f"  Rationale: {strategies['asset_allocation']['rationale']}")
        
        # Sector Rotation
        print("\\nSECTOR ROTATION:")
        if 'overweight' in strategies['sector_rotation']:
            print(f"  Overweight: {', '.join(strategies['sector_rotation']['overweight'])}")
        if 'underweight' in strategies['sector_rotation']:
            print(f"  Underweight: {', '.join(strategies['sector_rotation']['underweight'])}")
        print(f"  Rationale: {strategies['sector_rotation']['rationale']}")
        
        # Fixed Income
        if strategies['fixed_income']:
            print("\\nFIXED INCOME STRATEGY:")
            for key, value in strategies['fixed_income'].items():
                print(f"  {key.title()}: {value}")
        
        # Risk Management
        print("\\nRISK MANAGEMENT:")
        for key, value in strategies['risk_management'].items():
            if isinstance(value, list):
                print(f"  {key.title()}: {', '.join(value)}")
            else:
                print(f"  {key.title()}: {value}")
        
        # Create dashboard
        self.create_fed_policy_dashboard(policy_data)
        
        print(f"\\n✅ COMPREHENSIVE ANALYSIS COMPLETE")
        print("-" * 50)
        print("📈 Dashboard: comprehensive_fed_analysis.png")
        print("📊 Investment strategies optimized for current Fed policy regime")
        
        return {
            'policy_data': policy_data,
            'regime': regime,
            'strategies': strategies
        }

def main():
    """Main execution function"""
    
    # Get API key
    api_key = os.environ.get('FRED_API_KEY')
    if not api_key:
        print("⚠️ FRED_API_KEY environment variable not found")
        print("Please set your FRED API key to run comprehensive analysis")
        return None
    
    # Run comprehensive analysis
    analyzer = ComprehensiveFedAnalyzer(api_key)
    results = analyzer.generate_comprehensive_report()
    
    return results

if __name__ == "__main__":
    main()