import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

# Set professional styling
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("deep")

def generate_demo_phillips_data():
    """Generate realistic Phillips Curve data demonstrating flattening"""
    np.random.seed(42)
    
    # Create quarterly date range from 1960 to 2025
    dates = pd.date_range('1960-01-01', '2025-01-01', freq='Q')
    
    # Generate realistic economic data with changing relationships over time
    n_periods = len(dates)
    
    # Base unemployment rate with economic cycles
    unemployment_base = 6.0 + 2.5 * np.sin(np.arange(n_periods) * 0.05) + np.random.normal(0, 0.5, n_periods)
    
    # Create inflation with diminishing Phillips Curve relationship over time
    inflation = []
    
    for i, date in enumerate(dates):
        year = date.year
        
        # Phillips Curve coefficient that weakens over time
        if year < 1980:
            # Strong negative relationship (classic Phillips Curve)
            phillips_coef = -1.2
            base_inflation = 4.0
        elif year < 1990:
            # Weakening relationship (Volcker era)
            phillips_coef = -0.8
            base_inflation = 6.0
        elif year < 2000:
            # Further weakening (Great Moderation begins)
            phillips_coef = -0.4
            base_inflation = 3.0
        elif year < 2010:
            # Weak relationship (Great Moderation)
            phillips_coef = -0.2
            base_inflation = 2.5
        else:
            # Very weak/flat relationship (Post-crisis era)
            phillips_coef = -0.05
            base_inflation = 2.0
        
        # Calculate inflation based on unemployment gap
        unemployment_gap = unemployment_base[i] - 5.5  # Natural rate assumption
        inflation_point = base_inflation + phillips_coef * unemployment_gap + np.random.normal(0, 0.8)
        
        # Add some persistence and external shocks
        if i > 0:
            inflation_point = 0.7 * inflation[-1] + 0.3 * inflation_point
        
        # Add specific historical shocks
        if 1973 <= year <= 1975:  # Oil crisis
            inflation_point += 4.0
        elif 1979 <= year <= 1981:  # Second oil crisis
            inflation_point += 3.0
        elif 2008 <= year <= 2009:  # Financial crisis
            inflation_point -= 2.0
        elif 2020 <= year <= 2021:  # COVID-19
            inflation_point += np.random.normal(2.0, 1.5)
        
        inflation.append(max(inflation_point, -2.0))  # Floor at -2% deflation
    
    # Create DataFrame
    phillips_data = pd.DataFrame({
        'unemployment': unemployment_base,
        'inflation': inflation
    }, index=dates)
    
    return phillips_data

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
        
        if len(decade_data) > 10:
            correlation = decade_data['unemployment'].corr(decade_data['inflation'])
            
            # Linear regression to get slope
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
    """Calculate rolling correlation"""
    window_quarters = window_years * 4
    
    rolling_corr = data['unemployment'].rolling(window=window_quarters, min_periods=20).corr(
        data['inflation']
    )
    
    return rolling_corr

def create_phillips_visualization(data, decade_stats, rolling_corr):
    """Create comprehensive Phillips Curve visualization"""
    
    fig = plt.figure(figsize=(20, 16))
    fig.patch.set_facecolor('white')
    
    # Professional color scheme
    era_colors = {
        '1960s': '#1f77b4',  # Classic blue
        '1970s': '#ff7f0e',  # Orange (stagflation)
        '1980s': '#2ca02c',  # Green (Volcker era)
        '1990s': '#d62728',  # Red (Great Moderation)
        '2000s': '#9467bd',  # Purple
        '2010s': '#8c564b',  # Brown (Post-crisis)
        '2020s': '#e377c2'   # Pink (Current)
    }
    
    # 1. Historical Evolution (Top Left)
    ax1 = plt.subplot(2, 3, 1)
    
    key_decades = ['1960s', '1980s', '2000s', '2010s']
    
    for decade in key_decades:
        if decade in decade_stats:
            decade_data = decade_stats[decade]['data']
            correlation = decade_stats[decade]['correlation']
            slope = decade_stats[decade]['slope']
            
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
    
    # 2. Rolling Correlation (Top Right)
    ax2 = plt.subplot(2, 3, 2)
    
    ax2.plot(rolling_corr.index, rolling_corr.values, linewidth=3, color='#d62728')
    ax2.fill_between(rolling_corr.index, rolling_corr.values, alpha=0.3, color='#d62728')
    ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax2.axhline(y=-0.5, color='gray', linestyle=':', alpha=0.7, label='Strong Relationship')
    
    # Key events
    events = [
        ('1973-01-01', 'Oil Crisis'),
        ('1979-01-01', 'Volcker Era'),
        ('1990-01-01', 'Great Moderation'),
        ('2008-01-01', 'Financial Crisis'),
        ('2020-01-01', 'COVID-19')
    ]
    
    for date_str, event in events:
        try:
            event_date = pd.to_datetime(date_str)
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
    
    # 3. Decade Correlations (Bottom Left)
    ax3 = plt.subplot(2, 3, 4)
    
    decades = list(decade_stats.keys())
    correlations = [decade_stats[d]['correlation'] for d in decades]
    
    x_pos = np.arange(len(decades))
    bars = ax3.bar(x_pos, correlations, color=[era_colors.get(d, '#cccccc') for d in decades], 
                   alpha=0.7, edgecolor='black', linewidth=1)
    
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
    
    # 4. Slope Evolution (Bottom Right)
    ax4 = plt.subplot(2, 3, 5)
    
    slope_values = [decade_stats[d]['slope'] for d in decades]
    
    ax4.plot(decades, slope_values, 'o-', linewidth=3, markersize=8, 
             color='#2ca02c', markerfacecolor='white', markeredgewidth=2)
    ax4.fill_between(decades, slope_values, alpha=0.3, color='#2ca02c')
    ax4.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    for i, (decade, slope) in enumerate(zip(decades, slope_values)):
        ax4.annotate(f'{slope:.2f}', (i, slope), textcoords="offset points",
                    xytext=(0,10), ha='center', fontweight='bold')
    
    ax4.set_xlabel('Decade', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Phillips Curve Slope Coefficient', fontsize=12, fontweight='bold')
    ax4.set_title('Flattening: Slope Coefficient Evolution', fontsize=14, fontweight='bold', pad=20)
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(True, alpha=0.3)
    
    # 5. Summary Table (Top Center)
    ax5 = plt.subplot(2, 3, 3)
    ax5.axis('off')
    
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
        
        for i in range(len(summary_data) + 1):
            for j in range(5):
                cell = table[(i, j)]
                if i == 0:
                    cell.set_text_props(weight='bold')
                    cell.set_facecolor('#4472C4')
                    cell.set_text_props(color='white')
                else:
                    cell.set_facecolor('white')
                    cell.set_edgecolor('gray')
    
    ax5.set_title('Phillips Curve Statistics Summary', fontsize=14, fontweight='bold', pad=20)
    
    # 6. Modern Era Detail (Bottom Center)
    ax6 = plt.subplot(2, 3, 6)
    
    modern_data = data[data.index >= '2000-01-01']
    
    if len(modern_data) > 0:
        years = modern_data.index.year
        scatter = ax6.scatter(modern_data['unemployment'], modern_data['inflation'], 
                             c=years, cmap='viridis', alpha=0.7, s=40)
        
        X_modern = modern_data['unemployment'].values.reshape(-1, 1)
        y_modern = modern_data['inflation'].values
        reg_modern = LinearRegression().fit(X_modern, y_modern)
        
        x_range_modern = np.linspace(modern_data['unemployment'].min(), 
                                    modern_data['unemployment'].max(), 100)
        y_trend_modern = reg_modern.predict(x_range_modern.reshape(-1, 1))
        
        ax6.plot(x_range_modern, y_trend_modern, '--', color='red', linewidth=3, 
                 label=f'Trend (slope={reg_modern.coef_[0]:.3f})')
        
        cbar = plt.colorbar(scatter, ax=ax6)
        cbar.set_label('Year', fontsize=10, fontweight='bold')
        ax6.legend()
    
    ax6.set_xlabel('Unemployment Rate (%)', fontsize=12, fontweight='bold')
    ax6.set_ylabel('Core Inflation Rate (%)', fontsize=12, fontweight='bold')
    ax6.set_title('Modern Era Phillips Curve (2000-2025)', fontsize=14, fontweight='bold', pad=20)
    ax6.grid(True, alpha=0.3)
    
    plt.suptitle('The Flattening of the Phillips Curve: Diminished Inflation-Unemployment Relationship', 
                 fontsize=18, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.93, hspace=0.3, wspace=0.3)
    
    return fig

def main():
    """Generate demo Phillips Curve visualization"""
    print("Generating Phillips Curve Flattening Demonstration...")
    
    # Generate demo data
    phillips_data = generate_demo_phillips_data()
    
    print(f"Data period: {phillips_data.index[0]} to {phillips_data.index[-1]}")
    print(f"Total observations: {len(phillips_data)}")
    
    # Calculate statistics
    decade_stats = calculate_decade_statistics(phillips_data)
    rolling_corr = calculate_rolling_correlation(phillips_data, window_years=10)
    
    # Create visualization
    fig = create_phillips_visualization(phillips_data, decade_stats, rolling_corr)
    
    # Save high-quality output
    fig.savefig('/Users/chen/claude-code-projects/phillips_curve_flattening_demo.png', 
               dpi=300, bbox_inches='tight', facecolor='white')
    
    print("\n" + "="*60)
    print("PHILLIPS CURVE FLATTENING DEMONSTRATION - KEY INSIGHTS")
    print("="*60)
    
    # Show key findings
    early_corr = decade_stats.get('1960s', {}).get('correlation', 0)
    recent_corr = decade_stats.get('2010s', {}).get('correlation', 0)
    
    print(f"\n📊 QUANTIFIED FLATTENING:")
    print(f"   1960s Correlation: {early_corr:.3f}")
    print(f"   2010s Correlation: {recent_corr:.3f}")
    if early_corr != 0:
        print(f"   Relationship Weakening: {((abs(recent_corr) - abs(early_corr)) / abs(early_corr) * 100):.1f}%")
    
    print(f"\n💡 ECONOMIC IMPLICATIONS:")
    print(f"   • Traditional Phillips Curve trade-off has weakened significantly")
    print(f"   • Central bank credibility has anchored inflation expectations")
    print(f"   • Labor market slack is less predictive of inflation")
    print(f"   • Monetary policy transmission has fundamentally changed")
    
    print(f"\n✅ Demonstration complete! Visualization saved to:")
    print(f"   📊 phillips_curve_flattening_demo.png")
    
    plt.show()

if __name__ == "__main__":
    main()