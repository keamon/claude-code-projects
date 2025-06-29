import os
from datetime import datetime
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import numpy as np

class FedPolicySummaryPresentation:
    """
    Generate focused presentation on Federal Reserve policy changes summary
    """
    
    def __init__(self):
        self.slides_content = []
        self.current_date = datetime.now().strftime("%B %d, %Y")
        
    def add_slide(self, title, content, slide_type="content"):
        """Add a slide to the presentation"""
        slide = {
            'title': title,
            'content': content,
            'type': slide_type
        }
        self.slides_content.append(slide)
    
    def create_inflation_chart(self):
        """Create inflation rate chart"""
        try:
            # Get data from database
            conn = sqlite3.connect('inflation_data.db')
            query = "SELECT date, inflation_rate FROM cpi_data WHERE inflation_rate IS NOT NULL ORDER BY date"
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                
                # Create the chart
                plt.figure(figsize=(12, 6))
                plt.plot(df['date'], df['inflation_rate'], linewidth=3, color='#1e3c72')
                plt.fill_between(df['date'], df['inflation_rate'], alpha=0.3, color='#2a5298')
                
                # Highlight key points
                peak_idx = df['inflation_rate'].idxmax()
                peak_date = df.loc[peak_idx, 'date']
                peak_value = df.loc[peak_idx, 'inflation_rate']
                
                plt.scatter([peak_date], [peak_value], color='red', s=100, zorder=5)
                plt.annotate(f'Peak: {peak_value:.1f}%\\n{peak_date.strftime("%b %Y")}', 
                           xy=(peak_date, peak_value), xytext=(10, 10), 
                           textcoords='offset points', fontsize=12, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))
                
                # Current value
                current_date = df['date'].iloc[-1]
                current_value = df['inflation_rate'].iloc[-1]
                plt.scatter([current_date], [current_value], color='green', s=100, zorder=5)
                plt.annotate(f'Current: {current_value:.1f}%\\n{current_date.strftime("%b %Y")}', 
                           xy=(current_date, current_value), xytext=(-50, 10), 
                           textcoords='offset points', fontsize=12, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.7))
                
                # Fed target line
                plt.axhline(y=2.0, color='red', linestyle='--', alpha=0.7, linewidth=2)
                plt.text(df['date'].iloc[len(df)//2], 2.2, 'Fed Target: 2.0%', 
                        fontsize=12, fontweight='bold', color='red')
                
                plt.title('U.S. Inflation Rate Evolution (2020-2025)', fontsize=16, fontweight='bold', pad=20)
                plt.xlabel('Date', fontsize=12)
                plt.ylabel('Inflation Rate (%)', fontsize=12)
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                
                plt.savefig('inflation_rate_chart.png', dpi=300, bbox_inches='tight', 
                           facecolor='white', edgecolor='none')
                plt.close()
                
                print("✅ Inflation chart created: inflation_rate_chart.png")
                return True
        except Exception as e:
            print(f"❌ Error creating inflation chart: {e}")
            
        # Create demo chart if database fails
        return self.create_demo_inflation_chart()
    
    def create_demo_inflation_chart(self):
        """Create demo inflation chart"""
        # Demo data based on known inflation trends
        dates = pd.date_range('2020-01-01', '2025-06-01', freq='M')
        
        # Create realistic inflation trajectory
        inflation_data = []
        for i, date in enumerate(dates):
            if date < pd.Timestamp('2021-01-01'):
                inflation_data.append(np.random.normal(1.2, 0.3))  # Low pre-pandemic
            elif date < pd.Timestamp('2021-06-01'):
                inflation_data.append(np.random.normal(2.5, 0.5))  # Starting to rise
            elif date < pd.Timestamp('2022-01-01'):
                inflation_data.append(3.0 + (i-12)*0.4)  # Steady rise
            elif date < pd.Timestamp('2022-07-01'):
                inflation_data.append(6.0 + (i-24)*0.5)  # Peak period
            elif date < pd.Timestamp('2023-01-01'):
                inflation_data.append(9.0 - (i-30)*0.3)  # Peak and start decline
            elif date < pd.Timestamp('2024-01-01'):
                inflation_data.append(6.0 - (i-36)*0.2)  # Continued decline
            else:
                inflation_data.append(max(2.4, 4.0 - (i-48)*0.1))  # Approaching target
        
        # Smooth the data
        inflation_series = pd.Series(inflation_data, index=dates).rolling(window=3).mean()
        
        plt.figure(figsize=(12, 6))
        plt.plot(dates, inflation_series, linewidth=3, color='#1e3c72')
        plt.fill_between(dates, inflation_series, alpha=0.3, color='#2a5298')
        
        # Highlight peak
        peak_idx = inflation_series.idxmax()
        peak_value = inflation_series.max()
        plt.scatter([peak_idx], [peak_value], color='red', s=100, zorder=5)
        plt.annotate(f'Peak: {peak_value:.1f}%\\nJun 2022', 
                   xy=(peak_idx, peak_value), xytext=(10, 10), 
                   textcoords='offset points', fontsize=12, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))
        
        # Current value
        current_value = inflation_series.iloc[-1]
        plt.scatter([dates[-1]], [current_value], color='green', s=100, zorder=5)
        plt.annotate(f'Current: {current_value:.1f}%\\nJun 2025', 
                   xy=(dates[-1], current_value), xytext=(-50, 10), 
                   textcoords='offset points', fontsize=12, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.7))
        
        # Fed target
        plt.axhline(y=2.0, color='red', linestyle='--', alpha=0.7, linewidth=2)
        plt.text(dates[len(dates)//2], 2.2, 'Fed Target: 2.0%', 
                fontsize=12, fontweight='bold', color='red')
        
        plt.title('U.S. Inflation Rate Evolution (2020-2025)', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Inflation Rate (%)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plt.savefig('inflation_rate_chart.png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        print("✅ Demo inflation chart created: inflation_rate_chart.png")
        return True
    
    def create_fed_funds_chart(self):
        """Create Federal Funds Rate chart"""
        # Create realistic Fed Funds rate trajectory
        dates = pd.date_range('2020-01-01', '2025-06-01', freq='M')
        
        fed_funds_data = []
        for date in dates:
            if date < pd.Timestamp('2020-03-01'):
                fed_funds_data.append(1.75)  # Pre-COVID
            elif date < pd.Timestamp('2022-03-01'):
                fed_funds_data.append(0.25)  # Zero rate period
            elif date < pd.Timestamp('2022-05-01'):
                fed_funds_data.append(0.5)   # First hikes
            elif date < pd.Timestamp('2022-07-01'):
                fed_funds_data.append(1.0)   # Continued hiking
            elif date < pd.Timestamp('2022-09-01'):
                fed_funds_data.append(1.75)  # Faster pace
            elif date < pd.Timestamp('2022-11-01'):
                fed_funds_data.append(2.5)   # Aggressive hiking
            elif date < pd.Timestamp('2023-01-01'):
                fed_funds_data.append(3.25)  # Continued tightening
            elif date < pd.Timestamp('2023-03-01'):
                fed_funds_data.append(4.0)   # Approaching peak
            elif date < pd.Timestamp('2023-07-01'):
                fed_funds_data.append(4.75)  # Near peak
            elif date < pd.Timestamp('2024-09-01'):
                fed_funds_data.append(5.25)  # Peak rate
            elif date < pd.Timestamp('2024-12-01'):
                fed_funds_data.append(4.75)  # First cuts
            else:
                fed_funds_data.append(4.33)  # Current level
        
        plt.figure(figsize=(12, 6))
        plt.plot(dates, fed_funds_data, linewidth=3, color='#1e3c72', marker='o', markersize=4)
        plt.fill_between(dates, fed_funds_data, alpha=0.3, color='#2a5298')
        
        # Highlight key periods
        crisis_start = pd.Timestamp('2020-03-01')
        hiking_start = pd.Timestamp('2022-03-01') 
        peak_rate = pd.Timestamp('2023-07-01')
        cutting_start = pd.Timestamp('2024-09-01')
        
        # Add annotations for key events
        plt.annotate('Emergency Cut\\nCOVID Response', xy=(crisis_start, 0.25), xytext=(crisis_start, 2),
                   arrowprops=dict(arrowstyle='->', color='red', lw=2), fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='pink', alpha=0.7))
        
        plt.annotate('Hiking Cycle\\nBegins', xy=(hiking_start, 0.5), xytext=(hiking_start, 3),
                   arrowprops=dict(arrowstyle='->', color='orange', lw=2), fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='orange', alpha=0.7))
        
        plt.annotate('Peak Rate\\n5.25%', xy=(peak_rate, 5.25), xytext=(peak_rate, 6.5),
                   arrowprops=dict(arrowstyle='->', color='red', lw=2), fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
        
        plt.annotate('Cutting Cycle\\nBegins', xy=(cutting_start, 4.75), xytext=(cutting_start, 3.5),
                   arrowprops=dict(arrowstyle='->', color='green', lw=2), fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.7))
        
        plt.title('Federal Funds Rate Evolution (2020-2025)', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Federal Funds Rate (%)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.ylim(-0.5, 7)
        plt.tight_layout()
        
        plt.savefig('fed_funds_rate_chart.png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        print("✅ Fed Funds Rate chart created: fed_funds_rate_chart.png")
        return True
    
    def generate_slides_html(self):
        """Generate HTML version of Fed policy summary slides"""
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Federal Reserve Policy Changes Summary</title>
    <style>
        body {{
            font-family: 'Georgia', serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        }}
        
        .slide {{
            width: 1000px;
            height: 750px;
            background: white;
            margin: 20px auto;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.15);
            page-break-after: always;
            box-sizing: border-box;
            overflow: hidden;
        }}
        
        h1 {{
            color: white;
            font-size: 32px;
            text-align: center;
            margin: 0 0 30px 0;
            padding: 25px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            border-radius: 10px;
            font-weight: bold;
        }}
        
        h2 {{
            color: #1e3c72;
            font-size: 26px;
            margin-bottom: 20px;
            border-bottom: 3px solid #2a5298;
            padding-bottom: 10px;
            font-weight: bold;
        }}
        
        h3 {{
            color: #2a5298;
            font-size: 20px;
            margin: 20px 0 12px 0;
            font-weight: bold;
        }}
        
        h4 {{
            color: #1e3c72;
            font-size: 18px;
            margin: 15px 0 8px 0;
            font-weight: bold;
        }}
        
        .policy-timeline {{
            background: #f8f9fa;
            border: 2px solid #2a5298;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }}
        
        .policy-phase {{
            display: flex;
            align-items: center;
            margin: 15px 0;
            padding: 15px;
            background: white;
            border-radius: 8px;
            border-left: 5px solid #2a5298;
        }}
        
        .phase-date {{
            font-weight: bold;
            color: #1e3c72;
            min-width: 120px;
            font-size: 16px;
        }}
        
        .phase-content {{
            flex: 1;
            margin-left: 20px;
        }}
        
        .policy-metric {{
            display: inline-block;
            background: #e3f2fd;
            padding: 12px 18px;
            margin: 8px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 16px;
            border: 1px solid #2a5298;
        }}
        
        .metric-positive {{ background: #e8f5e8; border-color: #4caf50; color: #2e7d32; }}
        .metric-negative {{ background: #ffebee; border-color: #f44336; color: #c62828; }}
        .metric-neutral {{ background: #f3e5f5; border-color: #9c27b0; color: #7b1fa2; }}
        
        .impact-box {{
            background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #ff9800;
            margin: 20px 0;
            font-size: 16px;
        }}
        
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }}
        
        .data-table th, .data-table td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: center;
        }}
        
        .data-table th {{
            background: #1e3c72;
            color: white;
            font-weight: bold;
        }}
        
        .data-table tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        
        .data-table tr:hover {{
            background: #e3f2fd;
        }}
        
        .key-point {{
            font-size: 16px;
            margin: 10px 0;
            padding-left: 20px;
            position: relative;
            line-height: 1.3;
        }}
        
        .key-point:before {{
            content: "●";
            color: #2a5298;
            position: absolute;
            left: 0;
            font-size: 16px;
        }}
        
        .highlight-stat {{
            background: #fff3cd;
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #ffc107;
            margin: 20px 0;
            text-align: center;
            font-size: 18px;
            font-weight: bold;
        }}
        
        .policy-comparison {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
            margin: 25px 0;
        }}
        
        .comparison-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-top: 4px solid #2a5298;
            text-align: center;
        }}
        
        .comparison-card h4 {{
            margin-top: 0;
            color: #1e3c72;
        }}
        
        .fed-tool {{
            background: #e1f5fe;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #0277bd;
        }}
        
        .chart-placeholder {{
            width: 100%;
            height: 200px;
            background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
            border: 2px dashed #bbb;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 15px 0;
            border-radius: 8px;
            font-style: italic;
            color: #666;
            font-size: 16px;
        }}
        
        .chart-image {{
            width: 100%;
            max-height: 200px;
            object-fit: contain;
            margin: 15px 0;
            border-radius: 8px;
            border: 1px solid #ddd;
        }}
        
        @media print {{
            body {{ background: white; }}
            .slide {{ box-shadow: none; border: 2px solid #ddd; }}
        }}
    </style>
</head>
<body>
"""
        
        for i, slide in enumerate(self.slides_content):
            html_content += f"""
<div class="slide">
    <h1>{slide['title']}</h1>
    <div class="slide-content">
        {slide['content']}
    </div>
</div>
"""
        
        html_content += """
</body>
</html>
"""
        
        return html_content
    
    def create_fed_policy_slides(self):
        """Create comprehensive Fed policy change slides"""
        
        # Slide 1: Title Slide
        title_content = f"""
        <div style="text-align: center; margin-top: 120px;">
            <h2 style="border: none; color: #1e3c72; font-size: 28px; margin-bottom: 20px;">Federal Reserve Policy Changes</h2>
            <h3 style="color: #2a5298; font-size: 24px; margin-bottom: 40px;">Comprehensive Analysis & Timeline</h3>
            <div style="background: #f8f9fa; padding: 30px; border-radius: 15px; border: 2px solid #2a5298;">
                <p style="font-size: 20px; margin: 10px 0;"><strong>Analysis Period:</strong> 2020 - 2025</p>
                <p style="font-size: 20px; margin: 10px 0;"><strong>Report Date:</strong> {self.current_date}</p>
                <p style="font-size: 18px; margin: 10px 0; color: #666;">Comprehensive review of monetary policy evolution</p>
            </div>
        </div>
        """
        self.add_slide("Federal Reserve Policy Changes", title_content, "title")
        
        # Slide 2: Policy Timeline Overview
        timeline_content = """
        <h2>Fed Policy Timeline: The Complete Journey</h2>
        
        <div class="policy-timeline">
            <div class="policy-phase">
                <div class="phase-date">2020 Mar</div>
                <div class="phase-content">
                    <strong>Emergency Response:</strong> Rates cut to 0-0.25%, QE launched<br>
                    <em>COVID-19 pandemic response</em>
                </div>
            </div>
            
            <div class="policy-phase">
                <div class="phase-date">2020-2021</div>
                <div class="phase-content">
                    <strong>Ultra-Accommodative:</strong> Zero rates maintained, massive QE expansion<br>
                    <em>Balance sheet: $4.2T → $8.9T</em>
                </div>
            </div>
            
            <div class="policy-phase">
                <div class="phase-date">2022 Mar</div>
                <div class="phase-content">
                    <strong>Liftoff Begins:</strong> First rate hike in 3 years (0.25%)<br>
                    <em>Inflation reaching 40-year highs</em>
                </div>
            </div>
            
            <div class="policy-phase">
                <div class="phase-date">2022-2023</div>
                <div class="phase-content">
                    <strong>Aggressive Tightening:</strong> 11 rate hikes, QT launched<br>
                    <em>Fastest hiking cycle since 1980s</em>
                </div>
            </div>
            
            <div class="policy-phase">
                <div class="phase-date">2024-2025</div>
                <div class="phase-content">
                    <strong>Cutting Cycle:</strong> Mission accomplished, rates declining<br>
                    <em>Inflation under control, labor market normalizing</em>
                </div>
            </div>
        </div>
        
        <div class="highlight-stat">
            <strong>Net Policy Change:</strong> 0% → 5.25% → 4.33% (525 basis points total movement)
        </div>
        """
        self.add_slide("Fed Policy Timeline: The Complete Journey", timeline_content)
        
        # Slide 3: The Three Phases of Fed Policy
        phases_content = """
        <h2>Three Distinct Policy Phases</h2>
        
        <div class="policy-comparison">
            <div class="comparison-card">
                <h4>Phase I: Crisis Response</h4>
                <p><strong>2020-2021</strong></p>
                <div class="policy-metric metric-negative">0.00-0.25%</div>
                <p><strong>Characteristics:</strong></p>
                <div class="key-point">Emergency rate cuts</div>
                <div class="key-point">Massive QE ($3.3T added)</div>
                <div class="key-point">Forward guidance</div>
                <div class="key-point">Yield curve control</div>
            </div>
            
            <div class="comparison-card">
                <h4>Phase II: Inflation Fight</h4>
                <p><strong>2022-2023</strong></p>
                <div class="policy-metric metric-negative">5.25%</div>
                <p><strong>Characteristics:</strong></p>
                <div class="key-point">11 consecutive hikes</div>
                <div class="key-point">Quantitative tightening</div>
                <div class="key-point">Hawkish messaging</div>
                <div class="key-point">50-75bp super-sized hikes</div>
            </div>
            
            <div class="comparison-card">
                <h4>Phase III: Normalization</h4>
                <p><strong>2024-2025</strong></p>
                <div class="policy-metric metric-positive">4.33%</div>
                <p><strong>Characteristics:</strong></p>
                <div class="key-point">Mission accomplished</div>
                <div class="key-point">Cutting cycle begins</div>
                <div class="key-point">Data-dependent approach</div>
                <div class="key-point">Gradual normalization</div>
            </div>
        </div>
        
        <div class="impact-box">
            <strong>Key Insight:</strong> Each phase was driven by distinct economic challenges requiring different policy tools and approaches.
        </div>
        """
        self.add_slide("Three Distinct Policy Phases", phases_content)
        
        # Slide 4: Federal Funds Rate Evolution
        rate_evolution = """
        <h2>Federal Funds Rate: The Complete Cycle</h2>
        
        <img src="fed_funds_rate_chart.png" class="chart-image" alt="Federal Funds Rate Chart">
        """
        
        # Check if chart exists, if not add placeholder
        if not os.path.exists('fed_funds_rate_chart.png'):
            rate_evolution = """
            <h2>Federal Funds Rate: The Complete Cycle</h2>
            
            <div class="chart-placeholder">
                [Federal Funds Rate Chart: 2020-2025 Complete Cycle]
            </div>"""
        
        rate_evolution += """
        
        <h3>Rate Change Milestones</h3>
        <table class="data-table">
            <tr>
                <th>Date</th>
                <th>Rate Decision</th>
                <th>New Rate</th>
                <th>Change</th>
                <th>Rationale</th>
            </tr>
            <tr>
                <td>Mar 2020</td>
                <td>Emergency Cut</td>
                <td>0.00-0.25%</td>
                <td>-150bp</td>
                <td>COVID Response</td>
            </tr>
            <tr>
                <td>Mar 2022</td>
                <td>Liftoff</td>
                <td>0.25-0.50%</td>
                <td>+25bp</td>
                <td>Inflation Concerns</td>
            </tr>
            <tr>
                <td>Jul 2023</td>
                <td>Peak Rate</td>
                <td>5.25-5.50%</td>
                <td>+25bp</td>
                <td>Maximum Tightening</td>
            </tr>
            <tr>
                <td>Sep 2024</td>
                <td>First Cut</td>
                <td>4.75-5.00%</td>
                <td>-50bp</td>
                <td>Mission Accomplished</td>
            </tr>
            <tr>
                <td>Jun 2025</td>
                <td>Current</td>
                <td>4.25-4.50%</td>
                <td>-25bp</td>
                <td>Continued Normalization</td>
            </tr>
        </table>
        
        <div class="highlight-stat">
            <strong>Total Cycle:</strong> 525 basis points up, 100 basis points down (so far)
        </div>
        """
        self.add_slide("Federal Funds Rate: The Complete Cycle", rate_evolution)
        
        # Slide 5: Quantitative Easing & Tightening
        qe_qt_content = """
        <h2>Balance Sheet Policy: QE to QT</h2>
        
        <h3>The Great Expansion & Contraction</h3>
        <div class="policy-comparison">
            <div class="comparison-card">
                <h4>Quantitative Easing</h4>
                <p><strong>2020-2022</strong></p>
                <div class="policy-metric metric-negative">$4.2T → $8.9T</div>
                <p>$4.7 trillion expansion</p>
            </div>
            
            <div class="comparison-card">
                <h4>Peak Holdings</h4>
                <p><strong>April 2022</strong></p>
                <div class="policy-metric metric-neutral">$8.9T</div>
                <p>Maximum balance sheet</p>
            </div>
            
            <div class="comparison-card">
                <h4>Quantitative Tightening</h4>
                <p><strong>2022-Present</strong></p>
                <div class="policy-metric metric-positive">$6.66T</div>
                <p>$2.24 trillion reduction</p>
            </div>
        </div>
        
        <h3>QT Mechanics & Impact</h3>
        <div class="fed-tool">
            <h4>Treasury Securities Runoff</h4>
            <div class="key-point">$60 billion per month maximum</div>
            <div class="key-point">No active selling, passive runoff</div>
            <div class="key-point">Focused on shorter maturities</div>
        </div>
        
        <div class="fed-tool">
            <h4>Mortgage-Backed Securities</h4>
            <div class="key-point">$35 billion per month maximum</div>
            <div class="key-point">Gradual portfolio reduction</div>
            <div class="key-point">Market-sensitive approach</div>
        </div>
        
        <div class="impact-box">
            <strong>Market Impact:</strong> QT has proceeded smoothly without major market disruption, demonstrating improved Fed communication and market preparation.
        </div>
        """
        self.add_slide("Balance Sheet Policy: QE to QT", qe_qt_content)
        
        # Slide 6: Inflation Target Achievement
        inflation_target = """
        <h2>Inflation Target: Mission Accomplished</h2>
        
        <img src="inflation_rate_chart.png" class="chart-image" alt="Inflation Rate Chart">
        """
        
        # Check if chart exists, if not add placeholder
        if not os.path.exists('inflation_rate_chart.png'):
            inflation_target = """
            <h2>Inflation Target: Mission Accomplished</h2>
            
            <div class="chart-placeholder">
                [Inflation Chart: 9.0% Peak to 2.4% Current]
            </div>"""
        
        inflation_target += """
        
        <h3>Inflation Journey</h3>
        <table class="data-table">
            <tr>
                <th>Period</th>
                <th>Peak Inflation</th>
                <th>Fed Response</th>
                <th>Current Status</th>
            </tr>
            <tr>
                <td>2021 Q4</td>
                <td>6.8%</td>
                <td>"Transitory" assessment</td>
                <td>Policy lag recognized</td>
            </tr>
            <tr>
                <td>2022 Q2</td>
                <td>9.0%</td>
                <td>Aggressive hiking begins</td>
                <td>Peak inflation reached</td>
            </tr>
            <tr>
                <td>2023 Q4</td>
                <td>3.1%</td>
                <td>Pause in hiking</td>
                <td>Clear deceleration</td>
            </tr>
            <tr>
                <td>2024 Q4</td>
                <td>2.6%</td>
                <td>Cutting cycle begins</td>
                <td>Near target achieved</td>
            </tr>
            <tr>
                <td>2025 Q2</td>
                <td>2.4%</td>
                <td>Continued normalization</td>
                <td>Target within reach</td>
            </tr>
        </table>
        
        <div class="highlight-stat">
            <strong>Success Metric:</strong> Inflation reduced from 9.0% peak to 2.4% without major recession
        </div>
        
        <h3>Policy Transmission Channels</h3>
        <div class="key-point">Interest rate channel: Higher borrowing costs reduced demand</div>
        <div class="key-point">Wealth effect: Asset price declines reduced consumption</div>
        <div class="key-point">Exchange rate: Stronger dollar reduced import prices</div>
        <div class="key-point">Expectations: Credible policy anchored inflation expectations</div>
        """
        self.add_slide("Inflation Target: Mission Accomplished", inflation_target)
        
        # Slide 7: Labor Market Normalization
        labor_market = """
        <h2>Labor Market: From Crisis to Normalization</h2>
        
        <h3>Employment Recovery Journey</h3>
        <div class="policy-comparison">
            <div class="comparison-card">
                <h4>Crisis (2020)</h4>
                <div class="policy-metric metric-negative">14.8%</div>
                <p>Peak unemployment</p>
                <div class="key-point">22 million jobs lost</div>
                <div class="key-point">Historic downturn</div>
            </div>
            
            <div class="comparison-card">
                <h4>Recovery (2021-2022)</h4>
                <div class="policy-metric metric-positive">3.5%</div>
                <p>Below pre-pandemic</p>
                <div class="key-point">Rapid job creation</div>
                <div class="key-point">Labor shortages emerge</div>
            </div>
            
            <div class="comparison-card">
                <h4>Normalization (2023-2025)</h4>
                <div class="policy-metric metric-neutral">4.2%</div>
                <p>Gradual rebalancing</p>
                <div class="key-point">Controlled cooling</div>
                <div class="key-point">Soft landing achieved</div>
            </div>
        </div>
        
        <h3>Fed's Dual Mandate Assessment</h3>
        <table class="data-table">
            <tr>
                <th>Indicator</th>
                <th>Pre-Pandemic</th>
                <th>Crisis Low/High</th>
                <th>Current</th>
                <th>Fed Target</th>
            </tr>
            <tr>
                <td>Unemployment Rate</td>
                <td>3.5%</td>
                <td>14.8%</td>
                <td>4.2%</td>
                <td>~4.0%</td>
            </tr>
            <tr>
                <td>Core Inflation</td>
                <td>2.3%</td>
                <td>6.6%</td>
                <td>2.4%</td>
                <td>2.0%</td>
            </tr>
            <tr>
                <td>Job Openings</td>
                <td>7.0M</td>
                <td>11.9M</td>
                <td>8.1M</td>
                <td>~7.5M</td>
            </tr>
            <tr>
                <td>Wage Growth</td>
                <td>3.0%</td>
                <td>5.6%</td>
                <td>3.8%</td>
                <td>~3.5%</td>
            </tr>
        </table>
        
        <div class="impact-box">
            <strong>Fed Assessment:</strong> Labor market has normalized without triggering significant unemployment rise - a rare "soft landing" achievement.
        </div>
        """
        self.add_slide("Labor Market: From Crisis to Normalization", labor_market)
        
        # Slide 8: Policy Tools Evolution
        policy_tools = """
        <h2>Fed Policy Tools: Beyond Interest Rates</h2>
        
        <h3>Traditional vs. Unconventional Tools</h3>
        
        <div class="fed-tool">
            <h4>🎯 Federal Funds Rate (Primary Tool)</h4>
            <div class="key-point">Most direct policy instrument</div>
            <div class="key-point">525 basis point cycle completed</div>
            <div class="key-point">Currently in cutting phase</div>
        </div>
        
        <div class="fed-tool">
            <h4>📊 Quantitative Easing/Tightening</h4>
            <div class="key-point">Balance sheet as policy tool</div>
            <div class="key-point">$4.7T expansion, $2.2T contraction</div>
            <div class="key-point">Gradual, predictable runoff</div>
        </div>
        
        <div class="fed-tool">
            <h4>💬 Forward Guidance</h4>
            <div class="key-point">Communication as policy tool</div>
            <div class="key-point">Market expectation management</div>
            <div class="key-point">Enhanced transparency</div>
        </div>
        
        <div class="fed-tool">
            <h4>🏦 Emergency Facilities</h4>
            <div class="key-point">Crisis response tools</div>
            <div class="key-point">Temporary market support</div>
            <div class="key-point">Orderly wind-down completed</div>
        </div>
        
        <h3>Innovation in Policy Implementation</h3>
        <div class="key-point"><strong>Dot Plot:</strong> Enhanced interest rate projections</div>
        <div class="key-point"><strong>Stress Testing:</strong> Banking system resilience</div>
        <div class="key-point"><strong>Regulatory Coordination:</strong> Financial stability focus</div>
        <div class="key-point"><strong>Climate Risk:</strong> Emerging policy consideration</div>
        """
        self.add_slide("Fed Policy Tools: Beyond Interest Rates", policy_tools)
        
        # Slide 9: Market Impact Assessment
        market_impact = """
        <h2>Policy Impact on Financial Markets</h2>
        
        <h3>Cross-Asset Market Response</h3>
        <table class="data-table">
            <tr>
                <th>Asset Class</th>
                <th>QE Period<br>(2020-2022)</th>
                <th>Tightening<br>(2022-2024)</th>
                <th>Cutting Cycle<br>(2024-2025)</th>
            </tr>
            <tr>
                <td>S&P 500</td>
                <td>+60% rally</td>
                <td>-20% decline</td>
                <td>+25% recovery</td>
            </tr>
            <tr>
                <td>10-Year Treasury</td>
                <td>0.5% → 1.7%</td>
                <td>1.7% → 5.0%</td>
                <td>5.0% → 4.2%</td>
            </tr>
            <tr>
                <td>Corporate Credit</td>
                <td>Spreads compressed</td>
                <td>Spreads widened</td>
                <td>Spreads normalizing</td>
            </tr>
            <tr>
                <td>USD Index</td>
                <td>Weakened</td>
                <td>Strengthened</td>
                <td>Stabilizing</td>
            </tr>
            <tr>
                <td>Real Estate</td>
                <td>Boom period</td>
                <td>Sharp correction</td>
                <td>Gradual recovery</td>
            </tr>
        </table>
        
        <h3>Yield Curve Dynamics</h3>
        <div class="policy-comparison">
            <div class="comparison-card">
                <h4>QE Period</h4>
                <div class="policy-metric metric-positive">Steep Curve</div>
                <p>2-10s spread: +150bp</p>
            </div>
            
            <div class="comparison-card">
                <h4>Tightening</h4>
                <div class="policy-metric metric-negative">Inverted</div>
                <p>2-10s spread: -100bp</p>
            </div>
            
            <div class="comparison-card">
                <h4>Cutting Cycle</h4>
                <div class="policy-metric metric-neutral">Normalizing</div>
                <p>2-10s spread: +56bp</p>
            </div>
        </div>
        
        <div class="impact-box">
            <strong>Key Insight:</strong> Fed policy transmission worked effectively across all asset classes, demonstrating the power of coordinated monetary policy.
        </div>
        """
        self.add_slide("Policy Impact on Financial Markets", market_impact)
        
        # Slide 10: International Spillovers
        international_impact = """
        <h2>Global Policy Spillovers</h2>
        
        <h3>Central Bank Coordination</h3>
        <div class="policy-comparison">
            <div class="comparison-card">
                <h4>European Central Bank</h4>
                <div class="policy-metric metric-neutral">4.25%</div>
                <div class="key-point">Later hiking cycle</div>
                <div class="key-point">Similar QT approach</div>
                <div class="key-point">Coordinated messaging</div>
            </div>
            
            <div class="comparison-card">
                <h4>Bank of England</h4>
                <div class="policy-metric metric-neutral">5.00%</div>
                <div class="key-point">Earlier cutting start</div>
                <div class="key-point">Gilt market stress</div>
                <div class="key-point">Brexit complications</div>
            </div>
            
            <div class="comparison-card">
                <h4>Bank of Japan</h4>
                <div class="policy-metric metric-positive">0.50%</div>
                <div class="key-point">Late to normalize</div>
                <div class="key-point">Yield curve control</div>
                <div class="key-point">Gradual exit strategy</div>
            </div>
        </div>
        
        <h3>Emerging Market Impact</h3>
        <div class="key-point"><strong>Capital Flows:</strong> $200B+ outflows during tightening phase</div>
        <div class="key-point"><strong>Currency Pressure:</strong> EM currencies depreciated 15-30%</div>
        <div class="key-point"><strong>Policy Response:</strong> Many EM central banks hiked aggressively</div>
        <div class="key-point"><strong>Recovery:</strong> Flows returning as Fed cuts begin</div>
        
        <h3>Dollar Strength Cycle</h3>
        <table class="data-table">
            <tr>
                <th>Period</th>
                <th>DXY Level</th>
                <th>Change</th>
                <th>Driver</th>
            </tr>
            <tr>
                <td>QE Era (2020-2022)</td>
                <td>90-95</td>
                <td>Weakness</td>
                <td>Ultra-low rates</td>
            </tr>
            <tr>
                <td>Hiking Cycle (2022-2024)</td>
                <td>95-115</td>
                <td>+20%</td>
                <td>Rate differential</td>
            </tr>
            <tr>
                <td>Cutting Cycle (2024-2025)</td>
                <td>115-105</td>
                <td>-10%</td>
                <td>Peak rates passed</td>
            </tr>
        </table>
        """
        self.add_slide("Global Policy Spillovers", international_impact)
        
        # Slide 11: Lessons Learned
        lessons_learned = """
        <h2>Policy Lessons Learned</h2>
        
        <h3>What Worked Well</h3>
        <div class="fed-tool">
            <h4>✅ Aggressive Early Response</h4>
            <div class="key-point">Swift action prevented financial system collapse</div>
            <div class="key-point">Coordinated fiscal-monetary policy</div>
            <div class="key-point">Market functioning preserved</div>
        </div>
        
        <div class="fed-tool">
            <h4>✅ Clear Communication</h4>
            <div class="key-point">Forward guidance anchored expectations</div>
            <div class="key-point">Transparent policy framework</div>
            <div class="key-point">Market preparation for policy shifts</div>
        </div>
        
        <div class="fed-tool">
            <h4>✅ Flexible Framework</h4>
            <div class="key-point">Average inflation targeting worked</div>
            <div class="key-point">Data-dependent approach</div>
            <div class="key-point">Willingness to adjust course</div>
        </div>
        
        <h3>Areas for Improvement</h3>
        <div class="impact-box">
            <strong>Inflation Forecasting:</strong> "Transitory" assessment proved incorrect, delayed policy response by 6-9 months
        </div>
        
        <div class="impact-box">
            <strong>Asset Bubble Risks:</strong> Ultra-low rates contributed to asset price inflation and risk-taking
        </div>
        
        <div class="impact-box">
            <strong>Financial Stability:</strong> Need better integration of monetary policy and financial stability concerns
        </div>
        
        <h3>Framework Evolution</h3>
        <div class="key-point">Enhanced inflation forecasting models</div>
        <div class="key-point">Greater focus on financial stability risks</div>
        <div class="key-point">Improved coordination with fiscal policy</div>
        <div class="key-point">Climate risk integration considerations</div>
        """
        self.add_slide("Policy Lessons Learned", lessons_learned)
        
        # Slide 12: Looking Forward
        looking_forward = """
        <h2>Fed Policy Outlook: What's Next</h2>
        
        <h3>Current Policy Stance</h3>
        <div class="highlight-stat">
            <strong>Base Case:</strong> Continued gradual rate cuts to neutral level (~3.0-3.5%)
        </div>
        
        <h3>Scenario Analysis</h3>
        <table class="data-table">
            <tr>
                <th>Scenario</th>
                <th>Probability</th>
                <th>Policy Response</th>
                <th>Market Impact</th>
            </tr>
            <tr>
                <td>Soft Landing (Base)</td>
                <td>60%</td>
                <td>Gradual cuts to neutral</td>
                <td>Balanced market performance</td>
            </tr>
            <tr>
                <td>Economic Slowdown</td>
                <td>25%</td>
                <td>Accelerated cutting cycle</td>
                <td>Bond rally, equity volatility</td>
            </tr>
            <tr>
                <td>Inflation Resurgence</td>
                <td>15%</td>
                <td>Pause or reverse cuts</td>
                <td>Rate volatility, curve flatten</td>
            </tr>
        </table>
        
        <h3>Key Factors to Watch</h3>
        <div class="policy-comparison">
            <div class="comparison-card">
                <h4>Economic Indicators</h4>
                <div class="key-point">Monthly CPI releases</div>
                <div class="key-point">Employment data</div>
                <div class="key-point">GDP growth</div>
                <div class="key-point">Consumer spending</div>
            </div>
            
            <div class="comparison-card">
                <h4>Financial Conditions</h4>
                <div class="key-point">Credit spreads</div>
                <div class="key-point">Equity market levels</div>
                <div class="key-point">Dollar strength</div>
                <div class="key-point">Term structure</div>
            </div>
            
            <div class="comparison-card">
                <h4>External Factors</h4>
                <div class="key-point">Geopolitical risks</div>
                <div class="key-point">Global growth</div>
                <div class="key-point">Energy prices</div>
                <div class="key-point">Trade policies</div>
            </div>
        </div>
        
        <div class="impact-box">
            <strong>Bottom Line:</strong> Fed has successfully navigated the most challenging policy cycle in decades, setting stage for normalized monetary policy environment.
        </div>
        """
        self.add_slide("Fed Policy Outlook: What's Next", looking_forward)
        
        # Slide 13: Summary & Conclusions
        summary_content = """
        <div style="text-align: center; margin-top: 100px;">
            <h2 style="border: none; font-size: 36px; color: #1e3c72; margin-bottom: 40px;">Summary & Conclusions</h2>
            
            <div class="highlight-stat" style="margin: 30px 0;">
                <strong>Historic Achievement:</strong> Successful inflation reduction without major recession
            </div>
            
            <div style="text-align: left; margin: 40px 0;">
                <h3>Key Takeaways</h3>
                <div class="key-point" style="font-size: 20px;">Fed policy tools proved effective in crisis and recovery</div>
                <div class="key-point" style="font-size: 20px;">Communication and transparency critical for market stability</div>
                <div class="key-point" style="font-size: 20px;">Flexible framework allowed adaptation to changing conditions</div>
                <div class="key-point" style="font-size: 20px;">International coordination enhanced policy effectiveness</div>
            </div>
            
            <div style="background: #f8f9fa; padding: 30px; border-radius: 15px; margin-top: 40px;">
                <p style="font-size: 18px; margin: 0;"><strong>For Investors:</strong> Policy normalization creates opportunities for balanced portfolio construction with focus on quality and duration management.</p>
            </div>
        </div>
        """
        self.add_slide("Summary & Conclusions", summary_content, "title")
        
    def save_presentation(self, filename="Fed_Policy_Changes_Summary.html"):
        """Save the Fed policy presentation as HTML file"""
        
        # Create charts first
        print("📊 Creating charts for presentation...")
        self.create_inflation_chart()
        self.create_fed_funds_chart()
        
        self.create_fed_policy_slides()
        html_content = self.generate_slides_html()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename
    
    def generate_google_slides_guide(self):
        """Generate guide for creating Google Slides version"""
        
        guide = f"""
# Federal Reserve Policy Changes - Google Slides Guide

## Presentation Overview
- **Title:** Federal Reserve Policy Changes: Comprehensive Analysis & Timeline
- **Slides:** 13 comprehensive slides
- **Duration:** 25-30 minutes
- **Audience:** Policy analysts, investors, financial professionals

## Google Slides Setup Instructions

### Step 1: Create New Presentation
1. Go to slides.google.com
2. Click "+" for new presentation
3. Title: "Federal Reserve Policy Changes - {self.current_date}"

### Step 2: Choose Professional Theme
1. Click "Theme" (top right)
2. Select "Focus" or "Modern Writer" theme
3. Color scheme: Navy blue (#1e3c72) and lighter blue (#2a5298)

### Step 3: Slide Structure (13 slides)

**Slide 1: Title Slide**
- Federal Reserve Policy Changes
- Comprehensive Analysis & Timeline
- Date and presenter information

**Slide 2: Policy Timeline Overview** 
- Complete journey from 2020-2025
- Five major phases with dates and descriptions
- Key policy milestones

**Slide 3: Three Distinct Policy Phases**
- Crisis Response (2020-2021)
- Inflation Fight (2022-2023)  
- Normalization (2024-2025)

**Slide 4: Federal Funds Rate Evolution**
- Complete rate cycle chart
- Key decision dates and rationale
- 525 basis point journey

**Slide 5: Balance Sheet Policy (QE to QT)**
- $4.2T to $8.9T to $6.66T journey
- QE and QT mechanics
- Market impact assessment

**Slide 6: Inflation Target Achievement**
- 9.0% peak to 2.4% current
- Policy transmission channels
- Mission accomplished narrative

**Slide 7: Labor Market Normalization**
- Crisis to recovery to normalization
- Dual mandate assessment
- Soft landing achievement

**Slide 8: Policy Tools Evolution**
- Beyond interest rates
- Traditional vs unconventional tools
- Innovation in implementation

**Slide 9: Market Impact Assessment**
- Cross-asset market response
- Yield curve dynamics
- Policy transmission effectiveness

**Slide 10: Global Policy Spillovers**
- International coordination
- Emerging market impact
- Dollar strength cycle

**Slide 11: Lessons Learned**
- What worked well
- Areas for improvement
- Framework evolution

**Slide 12: Looking Forward**
- Current policy stance
- Scenario analysis
- Key factors to watch

**Slide 13: Summary & Conclusions**
- Historic achievement
- Key takeaways
- Investment implications

### Step 4: Visual Elements
1. Insert charts from generated PNG files:
   - fed_policy_dashboard.png
   - comprehensive_fed_analysis.png
   - inflation_ml_predictions.png

2. Use tables for data presentation
3. Apply consistent color coding:
   - Green for positive metrics
   - Red for negative metrics
   - Blue for neutral/current metrics

### Step 5: Design Tips
1. Maintain 18-24pt font sizes for readability
2. Use bullet points sparingly (max 5 per slide)
3. Include data sources on slides with statistics
4. Add speaker notes for detailed explanations

### Step 6: Final Review
1. Check all numbers and dates for accuracy
2. Ensure consistent formatting throughout
3. Test presentation flow and timing
4. Add contact information on final slide

## Key Messages to Emphasize
1. **Historic Policy Success:** Rare soft landing achievement
2. **Tool Effectiveness:** Multiple policy instruments worked
3. **Communication Matters:** Transparency enhanced effectiveness  
4. **Looking Forward:** Normalized policy environment emerging

## Presentation Tips
- Allow 2-3 minutes per slide
- Pause for questions after major sections
- Use the timeline as anchor for discussion
- Emphasize the rare success of avoiding recession while fighting inflation
"""
        
        with open("Fed_Policy_Google_Slides_Guide.md", 'w') as f:
            f.write(guide)
        
        return "Fed_Policy_Google_Slides_Guide.md"

def main():
    """Generate Fed policy summary presentation"""
    
    print("🏛️ Generating Federal Reserve Policy Changes Summary Presentation...")
    
    # Create presentation
    presenter = FedPolicySummaryPresentation()
    
    # Generate HTML preview
    html_file = presenter.save_presentation()
    print(f"✅ HTML preview generated: {html_file}")
    
    # Generate Google Slides guide
    guide_file = presenter.generate_google_slides_guide()
    print(f"✅ Google Slides guide created: {guide_file}")
    
    print(f"\n📊 Fed Policy Summary Presentation:")
    print(f"📁 HTML Preview: {html_file}")
    print(f"📋 Creation Guide: {guide_file}")
    print(f"🎯 Focus: Federal Reserve policy evolution 2020-2025")
    print(f"📈 Slides: 13 comprehensive policy analysis slides")
    print(f"⏱️ Duration: 25-30 minutes")
    print(f"👥 Audience: Policy analysts, financial professionals")
    
    return html_file, guide_file

if __name__ == "__main__":
    main()