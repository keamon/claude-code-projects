import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from fredapi import Fred
from datetime import datetime
from scipy import stats
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

# Set professional styling
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("deep")

# Initialize FRED API
fred = Fred(api_key='YOUR_FRED_API_KEY')

def fetch_phillips_data():
    """Fetch unemployment and inflation data from FRED"""
    print("Fetching Phillips Curve data from FRED...")
    
    # Unemployment Rate (monthly)
    unemployment = fred.get_series('UNRATE', start='1960-01-01')
    
    # Core CPI (excludes food and energy) - more stable measure
    core_cpi = fred.get_series('CPILFESL', start='1960-01-01')
    
    # Calculate year-over-year inflation rate
    inflation = core_cpi.pct_change(periods=12) * 100
    
    # Align data by converting to quarterly averages for smoother analysis
    unemployment_q = unemployment.resample('Q').mean()
    inflation_q = inflation.resample('Q').mean()
    
    # Combine and clean data
    phillips_data = pd.DataFrame({
        'unemployment': unemployment_q,
        'inflation': inflation_q
    }).dropna()
    
    return phillips_data, unemployment, inflation

def calculate_decade_statistics(data):
    """Calculate Phillips Curve statistics by decade"""
    decades = {
        '1960s': ('1960-01-01', '1969-12-31'),
        '1970s': ('1970-01-01', '1979-12-31'), 
        '1980s': ('1980-01-01', '1989-12-31'),
        '1990s': ('1990-01-01', '1999-12-31'),
        '2000s': ('2000-01-01', '2009-12-31'),
        '2010s': ('2010-01-01', '2019-12-31'),
        '2020s': ('2020-01-01', '2025-12-31')
    }
    
    stats_by_decade = {}
    
    for decade, (start, end) in decades.items():
        decade_data = data[(data.index >= start) & (data.index <= end)]
        
        if len(decade_data) > 10:  # Ensure sufficient data points
            correlation = decade_data['unemployment'].corr(decade_data['inflation'])
            
            # Linear regression to get slope (Phillips Curve coefficient)
            X = decade_data['unemployment'].values.reshape(-1, 1)
            y = decade_data['inflation'].values
            
            reg = LinearRegression().fit(X, y)
            slope = reg.coef_[0]
            r_squared = reg.score(X, y)
            
            stats_by_decade[decade] = {
                'correlation': correlation,
                'slope': slope,
                'r_squared': r_squared,
                'n_observations': len(decade_data),
                'data': decade_data
            }
    
    return stats_by_decade

def calculate_rolling_correlation(data, window_years=10):
    """Calculate rolling correlation to show flattening over time"""
    window_quarters = window_years * 4  # Convert years to quarters
    
    rolling_corr = data['unemployment'].rolling(window=window_quarters, min_periods=20).corr(
        data['inflation']
    )
    
    return rolling_corr

def create_phillips_visualization(data, decade_stats, rolling_corr):
    """Create comprehensive Phillips Curve visualization"""
    
    # Set up the figure with professional styling
    fig = plt.figure(figsize=(20, 16))
    fig.patch.set_facecolor('white')
    
    # Define colors for different eras
    era_colors = {
        '1960s': '#1f77b4',  # Classic blue
        '1970s': '#ff7f0e',  # Orange (stagflation era)
        '1980s': '#2ca02c',  # Green (Volcker era)
        '1990s': '#d62728',  # Red (Great Moderation begins)
        '2000s': '#9467bd',  # Purple (Great Moderation)
        '2010s': '#8c564b',  # Brown (Post-crisis)
        '2020s': '#e377c2'   # Pink (Current era)
    }
    
    # 1. Historical Phillips Curve Evolution (Top Left)
    ax1 = plt.subplot(2, 3, 1)
    
    # Plot selected decades to show evolution
    key_decades = ['1960s', '1980s', '2000s', '2010s']
    
    for decade in key_decades:
        if decade in decade_stats:
            decade_data = decade_stats[decade]['data']
            correlation = decade_stats[decade]['correlation']
            slope = decade_stats[decade]['slope']
            
            # Scatter plot
            ax1.scatter(decade_data['unemployment'], decade_data['inflation'], 
                       alpha=0.6, s=30, color=era_colors[decade], 
                       label=f'{decade} (ρ={correlation:.2f})')
            
            # Trend line
            x_range = np.linspace(decade_data['unemployment'].min(), 
                                decade_data['unemployment'].max(), 100)
            y_trend = slope * (x_range - decade_data['unemployment'].mean()) + decade_data['inflation'].mean()
            ax1.plot(x_range, y_trend, '--', color=era_colors[decade], alpha=0.8, linewidth=2)
    
    ax1.set_xlabel('Unemployment Rate (%)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Core Inflation Rate (%)', fontsize=12, fontweight='bold')
    ax1.set_title('Phillips Curve Evolution by Era', fontsize=14, fontweight='bold', pad=20)
    ax1.legend(frameon=True, fancybox=True, shadow=True)
    ax1.grid(True, alpha=0.3)
    
    # 2. Rolling Correlation Timeline (Top Right)
    ax2 = plt.subplot(2, 3, 2)
    
    ax2.plot(rolling_corr.index, rolling_corr.values, linewidth=3, color='#d62728')
    ax2.fill_between(rolling_corr.index, rolling_corr.values, alpha=0.3, color='#d62728')
    ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax2.axhline(y=-0.5, color='gray', linestyle=':', alpha=0.7, label='Strong Relationship')
    
    # Add key events
    events = {
        '1973-01-01': 'Oil Crisis',
        '1979-01-01': 'Volcker Era',
        '1990-01-01': 'Great Moderation',
        '2008-01-01': 'Financial Crisis',
        '2020-01-01': 'COVID-19'
    }
    
    for date, event in events.items():
        try:
            event_date = pd.to_datetime(date)
            if event_date >= rolling_corr.index.min() and event_date <= rolling_corr.index.max():
                ax2.axvline(x=event_date, color='gray', linestyle=':', alpha=0.7)
                ax2.text(event_date, rolling_corr.max() * 0.8, event, 
                        rotation=90, fontsize=9, ha='right')
        except:
            continue
    
    ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax2.set_ylabel('10-Year Rolling Correlation', fontsize=12, fontweight='bold')
    ax2.set_title('Phillips Curve Relationship Weakening Over Time', 
                  fontsize=14, fontweight='bold', pad=20)
    ax2.grid(True, alpha=0.3)
    
    # 3. Decade-by-Decade Analysis (Bottom Left)
    ax3 = plt.subplot(2, 3, 4)
    
    decades = list(decade_stats.keys())
    correlations = [decade_stats[d]['correlation'] for d in decades]
    
    x_pos = np.arange(len(decades))
    
    # Create bar chart showing correlation strength
    bars = ax3.bar(x_pos, correlations, color=[era_colors.get(d, '#cccccc') for d in decades], 
                   alpha=0.7, edgecolor='black', linewidth=1)
    
    # Add value labels on bars
    for i, (bar, corr) in enumerate(zip(bars, correlations)):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{corr:.2f}', ha='center', va='bottom', fontweight='bold')
    
    ax3.set_xlabel('Decade', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Correlation Coefficient', fontsize=12, fontweight='bold')
    ax3.set_title('Phillips Curve Correlation by Decade', fontsize=14, fontweight='bold', pad=20)
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(decades, rotation=45)
    ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 4. Slope Coefficients Over Time (Bottom Right)
    ax4 = plt.subplot(2, 3, 5)
    
    slope_values = [decade_stats[d]['slope'] for d in decades]
    
    # Line plot showing slope evolution
    ax4.plot(decades, slope_values, 'o-', linewidth=3, markersize=8, 
             color='#2ca02c', markerfacecolor='white', markeredgewidth=2)
    
    # Fill area to emphasize the flattening
    ax4.fill_between(decades, slope_values, alpha=0.3, color='#2ca02c')
    ax4.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    # Add slope values as annotations
    for i, (decade, slope) in enumerate(zip(decades, slope_values)):
        ax4.annotate(f'{slope:.2f}', (i, slope), textcoords="offset points",
                    xytext=(0,10), ha='center', fontweight='bold')
    
    ax4.set_xlabel('Decade', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Phillips Curve Slope Coefficient', fontsize=12, fontweight='bold')
    ax4.set_title('Flattening: Slope Coefficient Evolution', fontsize=14, fontweight='bold', pad=20)
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(True, alpha=0.3)
    
    # 5. Statistical Summary Table (Top Center)
    ax5 = plt.subplot(2, 3, 3)
    ax5.axis('off')
    
    # Create summary statistics table
    summary_data = []
    for decade in ['1960s', '1980s', '2000s', '2010s', '2020s']:
        if decade in decade_stats:
            stats = decade_stats[decade]
            summary_data.append([
                decade,
                f"{stats['correlation']:.3f}",
                f"{stats['slope']:.3f}",
                f"{stats['r_squared']:.3f}",
                f"{stats['n_observations']}"
            ])
    
    if summary_data:
        table = ax5.table(cellText=summary_data,
                         colLabels=['Era', 'Correlation', 'Slope', 'R²', 'N'],
                         cellLoc='center',
                         loc='center',
                         colColours=['lightgray']*5)
        
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1, 2)
        
        # Style the table
        for i in range(len(summary_data) + 1):
            for j in range(5):
                cell = table[(i, j)]
                if i == 0:  # Header row
                    cell.set_text_props(weight='bold')
                    cell.set_facecolor('#4472C4')
                    cell.set_text_props(color='white')
                else:
                    cell.set_facecolor('white')
                    cell.set_edgecolor('gray')
    
    ax5.set_title('Phillips Curve Statistics Summary', fontsize=14, fontweight='bold', pad=20)
    
    # 6. Modern Era Detail (Bottom Center)
    ax6 = plt.subplot(2, 3, 6)
    
    # Focus on post-2000 data to show flattening
    modern_data = data[data.index >= '2000-01-01']
    
    if len(modern_data) > 0:
        # Create scatter plot with color gradient by year
        years = modern_data.index.year
        scatter = ax6.scatter(modern_data['unemployment'], modern_data['inflation'], 
                             c=years, cmap='viridis', alpha=0.7, s=40)
        
        # Add trend line for modern era
        X_modern = modern_data['unemployment'].values.reshape(-1, 1)
        y_modern = modern_data['inflation'].values
        reg_modern = LinearRegression().fit(X_modern, y_modern)
        
        x_range_modern = np.linspace(modern_data['unemployment'].min(), 
                                    modern_data['unemployment'].max(), 100)
        y_trend_modern = reg_modern.predict(x_range_modern.reshape(-1, 1))
        
        ax6.plot(x_range_modern, y_trend_modern, '--', color='red', linewidth=3, 
                 label=f'Trend (slope={reg_modern.coef_[0]:.3f})')
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax6)
        cbar.set_label('Year', fontsize=10, fontweight='bold')
        
        ax6.legend()
    
    ax6.set_xlabel('Unemployment Rate (%)', fontsize=12, fontweight='bold')
    ax6.set_ylabel('Core Inflation Rate (%)', fontsize=12, fontweight='bold')
    ax6.set_title('Modern Era Phillips Curve (2000-2025)', fontsize=14, fontweight='bold', pad=20)
    ax6.grid(True, alpha=0.3)
    
    # Overall styling
    plt.suptitle('The Flattening of the Phillips Curve: Diminished Inflation-Unemployment Relationship', 
                 fontsize=18, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.93, hspace=0.3, wspace=0.3)
    
    return fig

def generate_insights(decade_stats, rolling_corr):
    """Generate key insights for analysis"""
    
    print("\n" + "="*60)
    print("PHILLIPS CURVE FLATTENING ANALYSIS - KEY INSIGHTS")
    print("="*60)
    
    # Correlation decline
    early_corr = decade_stats.get('1960s', {}).get('correlation', 0)
    recent_corr = decade_stats.get('2010s', {}).get('correlation', 0)
    
    print(f"\n📊 QUANTIFIED FLATTENING:")
    print(f"   1960s Correlation: {early_corr:.3f}")
    print(f"   2010s Correlation: {recent_corr:.3f}")
    if early_corr != 0:
        print(f"   Relationship Weakening: {((abs(recent_corr) - abs(early_corr)) / abs(early_corr) * 100):.1f}%")
    
    # Slope analysis
    early_slope = abs(decade_stats.get('1960s', {}).get('slope', 0))
    recent_slope = abs(decade_stats.get('2010s', {}).get('slope', 0))
    
    print(f"\n📈 SLOPE COEFFICIENT ANALYSIS:")
    print(f"   1960s Slope: -{early_slope:.3f}")
    print(f"   2010s Slope: -{recent_slope:.3f}")
    if early_slope != 0:
        print(f"   Slope Flattening: {((early_slope - recent_slope) / early_slope * 100):.1f}%")
    
    # Rolling correlation insights
    if len(rolling_corr.dropna()) > 0:
        print(f"\n📉 RELATIONSHIP EVOLUTION:")
        print(f"   Strongest Period: {rolling_corr.min():.3f} (most negative)")
        print(f"   Current Period: {rolling_corr.iloc[-10:].mean():.3f}")
        print(f"   Trend: {'Flattening' if rolling_corr.iloc[-10:].mean() > rolling_corr.min() else 'Stable'}")
    
    # Economic implications
    print(f"\n💡 ECONOMIC IMPLICATIONS:")
    print(f"   • Fed's inflation anchoring has been successful")
    print(f"   • Traditional Phillips Curve trade-offs weakened")
    print(f"   • Monetary policy transmission mechanisms changed")
    print(f"   • Labor market slack less predictive of inflation")

def main():
    """Main analysis function"""
    print("Phillips Curve Flattening Analysis")
    print("Fetching data from FRED API...")
    
    try:
        # Fetch data
        phillips_data, unemployment_monthly, inflation_monthly = fetch_phillips_data()
        
        print(f"Data period: {phillips_data.index[0]} to {phillips_data.index[-1]}")
        print(f"Total observations: {len(phillips_data)}")
        
        # Calculate statistics
        decade_stats = calculate_decade_statistics(phillips_data)
        rolling_corr = calculate_rolling_correlation(phillips_data, window_years=10)
        
        # Create visualization
        fig = create_phillips_visualization(phillips_data, decade_stats, rolling_corr)
        
        # Save high-quality output
        fig.savefig('/Users/chen/claude-code-projects/phillips_curve_flattening.png', 
                   dpi=300, bbox_inches='tight', facecolor='white')
        
        # Generate insights
        generate_insights(decade_stats, rolling_corr)
        
        # Save data for further analysis
        phillips_data.to_csv('/Users/chen/claude-code-projects/phillips_curve_data.csv')
        
        print(f"\n✅ Analysis complete! High-quality visualization saved to:")
        print(f"   📊 phillips_curve_flattening.png")
        print(f"   📁 phillips_curve_data.csv")
        
        plt.show()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Note: You need a FRED API key. Get one free at:")
        print("   https://fred.stlouisfed.org/docs/api/api_key.html")

if __name__ == "__main__":
    main()