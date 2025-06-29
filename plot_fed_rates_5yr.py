import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import sqlite3

def plot_fed_rates_5_years():
    """Plot Federal Reserve interest rates for the last 5 years with detailed analysis"""
    
    # Create comprehensive 5-year Fed funds rate data
    start_date = datetime.now() - timedelta(days=5*365)
    end_date = datetime.now()
    
    # Generate monthly dates
    dates = pd.date_range(start=start_date, end=end_date, freq='MS')  # Month start
    
    # Create realistic Fed funds rate trajectory based on known policy timeline
    fed_rates = []
    
    for date in dates:
        if date < pd.Timestamp('2020-03-15'):
            # Pre-COVID: Rates around 1.75%
            fed_rates.append(1.75)
        elif date < pd.Timestamp('2020-04-01'):
            # Emergency cuts in March 2020
            fed_rates.append(0.25)
        elif date < pd.Timestamp('2022-03-01'):
            # Zero rate period: March 2020 - March 2022
            fed_rates.append(0.25)
        elif date < pd.Timestamp('2022-05-01'):
            # First rate hike: 0.25% to 0.75%
            fed_rates.append(0.75)
        elif date < pd.Timestamp('2022-07-01'):
            # Second hike: 0.75% to 1.75%
            fed_rates.append(1.75)
        elif date < pd.Timestamp('2022-09-01'):
            # Third hike: 1.75% to 2.50%
            fed_rates.append(2.50)
        elif date < pd.Timestamp('2022-11-01'):
            # Fourth hike: 2.50% to 3.25%
            fed_rates.append(3.25)
        elif date < pd.Timestamp('2023-01-01'):
            # Fifth hike: 3.25% to 4.00%
            fed_rates.append(4.00)
        elif date < pd.Timestamp('2023-03-01'):
            # Sixth hike: 4.00% to 4.75%
            fed_rates.append(4.75)
        elif date < pd.Timestamp('2023-07-01'):
            # Peak rate: 4.75% to 5.25%
            fed_rates.append(5.25)
        elif date < pd.Timestamp('2024-09-01'):
            # Peak sustained: 5.25%
            fed_rates.append(5.25)
        elif date < pd.Timestamp('2024-12-01'):
            # First cut: 5.25% to 4.75%
            fed_rates.append(4.75)
        elif date < pd.Timestamp('2025-03-01'):
            # Second cut: 4.75% to 4.50%
            fed_rates.append(4.50)
        else:
            # Current level: 4.33%
            fed_rates.append(4.33)
    
    # Try to get actual data from database first
    try:
        conn = sqlite3.connect('inflation_data.db')
        
        # Check if we have fed funds data
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name='fed_policy_data'"
        table_exists = pd.read_sql_query(query, conn)
        
        if not table_exists.empty:
            # Try to get FEDFUNDS data
            fed_query = "SELECT date, FEDFUNDS FROM fed_policy_data WHERE FEDFUNDS IS NOT NULL ORDER BY date"
            fed_data = pd.read_sql_query(fed_query, conn)
            
            if not fed_data.empty:
                fed_data['date'] = pd.to_datetime(fed_data['date'])
                # Filter for last 5 years
                five_years_ago = datetime.now() - timedelta(days=5*365)
                fed_data = fed_data[fed_data['date'] >= five_years_ago]
                
                if len(fed_data) > 10:  # Use actual data if we have enough points
                    dates = fed_data['date']
                    fed_rates = fed_data['FEDFUNDS']
                    print("✅ Using actual Fed funds rate data from database")
                else:
                    print("⚠️ Limited data in database, using constructed timeline")
            else:
                print("⚠️ No FEDFUNDS data in database, using constructed timeline")
        else:
            print("⚠️ No fed_policy_data table found, using constructed timeline")
        
        conn.close()
        
    except Exception as e:
        print(f"⚠️ Database access failed: {e}, using constructed timeline")
    
    # Create the plot
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Plot the main line
    ax.plot(dates, fed_rates, linewidth=3, color='#1f77b4', marker='o', markersize=4, 
            markerfacecolor='white', markeredgecolor='#1f77b4', markeredgewidth=2)
    
    # Fill area under the curve
    ax.fill_between(dates, fed_rates, alpha=0.3, color='#1f77b4')
    
    # Add policy regime background colors
    policy_periods = [
        (pd.Timestamp('2020-01-01'), pd.Timestamp('2020-03-15'), '#90EE90', 'Pre-COVID'),
        (pd.Timestamp('2020-03-15'), pd.Timestamp('2022-03-16'), '#FFE4E1', 'Emergency Response\n(Zero Rates)'),
        (pd.Timestamp('2022-03-16'), pd.Timestamp('2024-09-01'), '#FFB6C1', 'Aggressive Tightening'),
        (pd.Timestamp('2024-09-01'), pd.Timestamp('2025-12-31'), '#E0E0E0', 'Cutting Cycle')
    ]
    
    for start, end, color, label in policy_periods:
        if start >= dates.min() and start <= dates.max():
            ax.axvspan(start, min(end, dates.max()), alpha=0.2, color=color, label=label)
    
    # Add key policy events with annotations
    policy_events = [
        (pd.Timestamp('2020-03-15'), 0.25, 'Emergency Cut\nCOVID-19 Response', 'top'),
        (pd.Timestamp('2022-03-16'), 0.75, 'First Rate Hike\nInflation Fight Begins', 'bottom'),
        (pd.Timestamp('2023-07-01'), 5.25, 'Peak Rate\n5.25%', 'top'),
        (pd.Timestamp('2024-09-18'), 4.75, 'First Rate Cut\nMission Accomplished', 'bottom'),
        (pd.Timestamp('2025-06-01'), 4.33, 'Current Level\n4.33%', 'top')
    ]
    
    for event_date, rate, label, position in policy_events:
        if event_date >= dates.min() and event_date <= dates.max():
            # Find closest actual data point
            closest_idx = np.argmin(np.abs(pd.to_datetime(dates) - event_date))
            actual_date = dates.iloc[closest_idx] if hasattr(dates, 'iloc') else dates[closest_idx]
            actual_rate = fed_rates[closest_idx] if hasattr(fed_rates, 'iloc') else fed_rates[closest_idx]
            
            # Add annotation
            if position == 'top':
                xytext = (0, 20)
                va = 'bottom'
            else:
                xytext = (0, -20)
                va = 'top'
            
            ax.annotate(label, xy=(actual_date, actual_rate), xytext=xytext,
                       textcoords='offset points', fontsize=10, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.8),
                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='red', lw=2),
                       ha='center', va=va)
    
    # Add horizontal reference lines
    ax.axhline(y=2.0, color='green', linestyle='--', alpha=0.7, linewidth=2, label='Fed Long-term Target (~2%)')
    ax.axhline(y=5.25, color='red', linestyle='--', alpha=0.7, linewidth=2, label='Peak Rate (5.25%)')
    ax.axhline(y=0.25, color='orange', linestyle='--', alpha=0.7, linewidth=2, label='Emergency Low (0.25%)')
    
    # Formatting
    ax.set_title('Federal Reserve Interest Rate Evolution (Last 5 Years)\nFrom COVID Crisis to Inflation Fight to Normalization', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('Federal Funds Rate (%)', fontsize=12, fontweight='bold')
    
    # Format x-axis
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_minor_locator(mdates.MonthLocator([1, 7]))  # Jan and July
    
    # Format y-axis
    ax.set_ylim(-0.5, 6.0)
    ax.set_ylabel('Federal Funds Rate (%)', fontsize=12, fontweight='bold')
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    
    # Add legend
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc='upper left', fontsize=10, framealpha=0.9)
    
    # Add summary statistics box
    if len(fed_rates) > 0:
        current_rate = fed_rates[-1] if hasattr(fed_rates, 'iloc') else fed_rates[-1]
        max_rate = max(fed_rates)
        min_rate = min(fed_rates)
        
        stats_text = f"""Rate Statistics (5 Years):
Current: {current_rate:.2f}%
Peak: {max_rate:.2f}%
Trough: {min_rate:.2f}%
Total Range: {max_rate - min_rate:.2f}%"""
        
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    # Add Fed policy cycle summary
    cycle_text = """Policy Cycle Summary:
• 2020: Emergency response (1.75% → 0.25%)
• 2020-2022: Zero rate period (24 months)
• 2022-2024: Aggressive tightening (525bp)
• 2024-2025: Cutting cycle begins
• Current: Gradual normalization phase"""
    
    ax.text(0.98, 0.02, cycle_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='bottom', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    
    # Tight layout to prevent label cutoff
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('fed_rates_5_years.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    # Show the plot
    plt.show()
    
    print("✅ Fed rates 5-year chart created and saved as 'fed_rates_5_years.png'")
    
    # Print summary statistics
    if len(fed_rates) > 0:
        print(f"\n📊 FEDERAL FUNDS RATE STATISTICS (Last 5 Years)")
        print(f"{'='*50}")
        print(f"Current Rate: {fed_rates[-1]:.2f}%")
        print(f"Peak Rate: {max(fed_rates):.2f}%")
        print(f"Trough Rate: {min(fed_rates):.2f}%")
        print(f"Total Range: {max(fed_rates) - min(fed_rates):.2f} percentage points")
        print(f"Average Rate: {np.mean(fed_rates):.2f}%")
        print(f"Current vs. Peak: {fed_rates[-1] - max(fed_rates):+.2f}%")
        print(f"Current vs. Trough: {fed_rates[-1] - min(fed_rates):+.2f}%")

def main():
    """Main execution function"""
    print("📈 Plotting Federal Reserve Interest Rates (Last 5 Years)")
    print("=" * 60)
    
    plot_fed_rates_5_years()
    
    return True

if __name__ == "__main__":
    main()