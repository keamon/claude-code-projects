import os
from datetime import datetime
import pandas as pd
import sqlite3

class GoogleSlidesGenerator:
    """
    Generate Google Slides presentation content for Federal Reserve analysis
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
    
    def generate_slides_html(self):
        """Generate HTML version of slides for preview"""
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Federal Reserve Policy Analysis - Client Presentation</title>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        
        .slide {{
            width: 800px;
            height: 600px;
            background: white;
            margin: 20px auto;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            page-break-after: always;
            display: flex;
            flex-direction: column;
        }}
        
        .slide-title {{
            background: #667eea;
            margin: 0 0 30px 0;
            padding: 0;
            border-radius: 10px;
        }}
        
        .slide-content {{
            background: white;
            padding: 40px;
        }}
        
        h1 {{
            color: white;
            font-size: 32px;
            text-align: center;
            margin: 0;
            padding: 30px;
            background: #667eea;
            border-radius: 10px;
        }}
        
        h2 {{
            color: #333;
            font-size: 28px;
            margin-bottom: 20px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        h3 {{
            color: #667eea;
            font-size: 22px;
            margin: 20px 0 10px 0;
        }}
        
        .bullet-point {{
            font-size: 18px;
            margin: 10px 0;
            padding-left: 20px;
            position: relative;
        }}
        
        .bullet-point:before {{
            content: "▶";
            color: #667eea;
            position: absolute;
            left: 0;
        }}
        
        .highlight {{
            background: #fff3cd;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #ffc107;
            margin: 20px 0;
        }}
        
        .metric {{
            display: inline-block;
            background: #e9ecef;
            padding: 10px 15px;
            margin: 5px;
            border-radius: 5px;
            font-weight: bold;
        }}
        
        .positive {{ color: #28a745; }}
        .negative {{ color: #dc3545; }}
        .neutral {{ color: #6c757d; }}
        
        .chart-placeholder {{
            width: 100%;
            height: 200px;
            background: #f8f9fa;
            border: 2px dashed #dee2e6;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 20px 0;
            border-radius: 8px;
            font-style: italic;
            color: #6c757d;
        }}
        
        .strategy-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }}
        
        .strategy-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        .table th, .table td {{
            border: 1px solid #dee2e6;
            padding: 10px;
            text-align: center;
        }}
        
        .table th {{
            background: #667eea;
            color: white;
        }}
        
        .table tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        
        @media print {{
            body {{ background: white; }}
            .slide {{ box-shadow: none; border: 1px solid #ccc; }}
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
    
    def create_presentation_slides(self):
        """Create all slides for the presentation"""
        
        # Slide 1: Title Slide
        title_content = f"""
        <div style="text-align: center; margin-top: 100px;">
            <h2 style="border: none; color: #667eea; font-size: 24px;">Federal Reserve Policy Analysis</h2>
            <h3 style="color: #333; font-size: 20px;">Investment Strategy & Market Outlook</h3>
            <p style="font-size: 18px; margin-top: 50px;">Prepared for: [Client Name]</p>
            <p style="font-size: 16px;">Date: {self.current_date}</p>
            <p style="font-size: 16px;">Presented by: [Your Firm Name]</p>
        </div>
        """
        self.add_slide("Federal Reserve Policy Analysis", title_content, "title")
        
        # Slide 2: Executive Summary
        exec_summary = """
        <h2>Executive Summary</h2>
        <div class="highlight">
            <strong>Key Finding:</strong> Federal Reserve transitioning from aggressive tightening to cutting cycle
        </div>
        
        <h3>Current Economic Environment</h3>
        <div class="bullet-point">Fed Funds Rate: 4.33% (down 18.8% from peak)</div>
        <div class="bullet-point">Inflation: 2.38% (down from 9.0% peak in June 2022)</div>
        <div class="bullet-point">Unemployment: 4.2% (tight but normalizing)</div>
        <div class="bullet-point">Yield Curve: +0.56% spread (no longer inverted)</div>
        
        <h3>Investment Implication</h3>
        <div class="strategy-grid">
            <div class="strategy-card">
                <strong>Opportunity:</strong> Position for rate decline with duration extension
            </div>
            <div class="strategy-card">
                <strong>Strategy:</strong> Balanced growth approach as policy normalizes
            </div>
        </div>
        """
        self.add_slide("Executive Summary", exec_summary)
        
        # Slide 3: Federal Reserve Policy Evolution
        fed_policy = """
        <h2>Federal Reserve Policy Evolution</h2>
        
        <h3>Policy Timeline (2020-2025)</h3>
        <table class="table">
            <tr>
                <th>Period</th>
                <th>Fed Funds Rate</th>
                <th>Policy Stance</th>
                <th>Key Events</th>
            </tr>
            <tr>
                <td>2020-2022</td>
                <td>0.00-0.25%</td>
                <td>Ultra-Accommodative</td>
                <td>COVID Response, QE</td>
            </tr>
            <tr>
                <td>2022-2023</td>
                <td>0.25-5.25%</td>
                <td>Aggressive Tightening</td>
                <td>Inflation Fight</td>
            </tr>
            <tr>
                <td>2024-2025</td>
                <td>5.25-4.33%</td>
                <td>Cutting Cycle</td>
                <td>Mission Accomplished</td>
            </tr>
        </table>
        
        <div class="highlight">
            <strong>Current Status:</strong> Fed has successfully brought inflation down from 9.0% peak to near target levels
        </div>
        """
        self.add_slide("Federal Reserve Policy Evolution", fed_policy)
        
        # Slide 4: Inflation Analysis
        inflation_analysis = """
        <h2>Inflation Analysis: Mission Accomplished</h2>
        
        <h3>Historical Peak Analysis</h3>
        <div class="bullet-point">Peak Inflation: <span class="negative">9.0% (June 2022)</span></div>
        <div class="bullet-point">Current Level: <span class="positive">2.38% (May 2025)</span></div>
        <div class="bullet-point">Fed Target: <span class="neutral">2.0%</span></div>
        
        <div class="chart-placeholder">
            [Inflation Chart: 2020-2025 CPI Trends]
        </div>
        
        <h3>ML Forecast (Next 3 Months)</h3>
        <table class="table">
            <tr>
                <th>Month</th>
                <th>Predicted Inflation</th>
                <th>Confidence</th>
            </tr>
            <tr>
                <td>June 2025</td>
                <td>2.77%</td>
                <td>High</td>
            </tr>
            <tr>
                <td>July 2025</td>
                <td>2.77%</td>
                <td>High</td>
            </tr>
            <tr>
                <td>August 2025</td>
                <td>2.77%</td>
                <td>Medium</td>
            </tr>
        </table>
        """
        self.add_slide("Inflation Analysis: Mission Accomplished", inflation_analysis)
        
        # Slide 5: Phillips Curve Breakdown
        phillips_curve = """
        <h2>Phillips Curve Flattening: New Economic Reality</h2>
        
        <h3>Traditional Relationship Breakdown</h3>
        <div class="strategy-grid">
            <div class="strategy-card">
                <strong>2020-2021:</strong><br>
                Strong correlation (-0.857)<br>
                <em>Traditional relationship</em>
            </div>
            <div class="strategy-card">
                <strong>2022:</strong><br>
                No correlation (-0.007)<br>
                <em>Complete breakdown</em>
            </div>
        </div>
        
        <div class="chart-placeholder">
            [Phillips Curve Evolution Chart]
        </div>
        
        <h3>Investment Implications</h3>
        <div class="bullet-point">Traditional inflation hedging less reliable</div>
        <div class="bullet-point">Greater importance of real-time Fed communication</div>
        <div class="bullet-point">Need for more sophisticated portfolio strategies</div>
        """
        self.add_slide("Phillips Curve Flattening: New Economic Reality", phillips_curve)
        
        # Slide 6: Current Market Environment
        market_environment = """
        <h2>Current Market Environment Assessment</h2>
        
        <h3>Policy Regime Indicators</h3>
        <table class="table">
            <tr>
                <th>Indicator</th>
                <th>Current Status</th>
                <th>Trend</th>
                <th>Implication</th>
            </tr>
            <tr>
                <td>Rate Trend</td>
                <td>Cutting Cycle</td>
                <td>↓</td>
                <td>Supportive for risk assets</td>
            </tr>
            <tr>
                <td>Balance Sheet</td>
                <td>QT Contraction</td>
                <td>↓</td>
                <td>Gradual liquidity drain</td>
            </tr>
            <tr>
                <td>Inflation</td>
                <td>Above Target</td>
                <td>↓</td>
                <td>Approaching Fed goal</td>
            </tr>
            <tr>
                <td>Employment</td>
                <td>Tight</td>
                <td>→</td>
                <td>Normalizing gradually</td>
            </tr>
        </table>
        
        <div class="highlight">
            <strong>Overall Assessment:</strong> Transitional environment favoring balanced allocation with tactical adjustments
        </div>
        """
        self.add_slide("Current Market Environment Assessment", market_environment)
        
        # Slide 7: Strategic Asset Allocation
        asset_allocation = """
        <h2>Strategic Asset Allocation Recommendations</h2>
        
        <h3>Target Portfolio Allocation</h3>
        <table class="table">
            <tr>
                <th>Asset Class</th>
                <th>Target Weight</th>
                <th>Strategy Focus</th>
                <th>Rationale</th>
            </tr>
            <tr>
                <td>Equities</td>
                <td><strong>65%</strong></td>
                <td>Balanced Growth/Value</td>
                <td>Fed transition supportive</td>
            </tr>
            <tr>
                <td>Fixed Income</td>
                <td><strong>30%</strong></td>
                <td>Extend Duration</td>
                <td>Capture rate decline</td>
            </tr>
            <tr>
                <td>Alternatives</td>
                <td><strong>5%</strong></td>
                <td>Real Assets</td>
                <td>Diversification benefit</td>
            </tr>
        </table>
        
        <div class="chart-placeholder">
            [Asset Allocation Pie Chart]
        </div>
        
        <h3>Key Positioning Changes</h3>
        <div class="bullet-point">Increase duration in fixed income</div>
        <div class="bullet-point">Maintain balanced equity approach</div>
        <div class="bullet-point">Modest alternative allocation for diversification</div>
        """
        self.add_slide("Strategic Asset Allocation Recommendations", asset_allocation)
        
        # Slide 8: Sector Strategy
        sector_strategy = """
        <h2>Sector Rotation Strategy</h2>
        
        <h3>Recommended Sector Positioning</h3>
        <div class="strategy-grid">
            <div class="strategy-card">
                <h4 style="color: #28a745;">OVERWEIGHT</h4>
                <div class="bullet-point">Healthcare</div>
                <div class="bullet-point">Technology</div>
                <div class="bullet-point">Industrials</div>
                <p><em>Focus on secular growth trends</em></p>
            </div>
            <div class="strategy-card">
                <h4 style="color: #dc3545;">UNDERWEIGHT</h4>
                <div class="bullet-point">Utilities</div>
                <div class="bullet-point">Materials</div>
                <p><em>Avoid rate-sensitive and cyclical risks</em></p>
            </div>
        </div>
        
        <h3>Sector Performance in Fed Cycles</h3>
        <table class="table">
            <tr>
                <th>Sector</th>
                <th>Cutting Cycle</th>
                <th>Current Positioning</th>
            </tr>
            <tr>
                <td>Technology</td>
                <td class="positive">Outperform</td>
                <td>Overweight</td>
            </tr>
            <tr>
                <td>Healthcare</td>
                <td class="positive">Defensive Growth</td>
                <td>Overweight</td>
            </tr>
            <tr>
                <td>Financials</td>
                <td class="negative">Underperform</td>
                <td>Neutral</td>
            </tr>
        </table>
        """
        self.add_slide("Sector Rotation Strategy", sector_strategy)
        
        # Slide 9: Fixed Income Strategy
        fixed_income = """
        <h2>Fixed Income Strategy: Duration Extension</h2>
        
        <h3>Rate Environment Analysis</h3>
        <div class="highlight">
            <strong>Key Insight:</strong> Fed cutting cycle creates opportunity for duration extension
        </div>
        
        <h3>Fixed Income Positioning</h3>
        <table class="table">
            <tr>
                <th>Strategy Component</th>
                <th>Current Approach</th>
                <th>Rationale</th>
            </tr>
            <tr>
                <td>Duration</td>
                <td>7-30 Years</td>
                <td>Capture rate decline</td>
            </tr>
            <tr>
                <td>Credit Quality</td>
                <td>Investment Grade</td>
                <td>Quality focus amid transition</td>
            </tr>
            <tr>
                <td>TIPS Allocation</td>
                <td>Underweight</td>
                <td>Inflation expectations normalizing</td>
            </tr>
            <tr>
                <td>International</td>
                <td>Selective</td>
                <td>Currency and rate differentials</td>
            </tr>
        </table>
        
        <div class="chart-placeholder">
            [Yield Curve and Duration Strategy Chart]
        </div>
        """
        self.add_slide("Fixed Income Strategy: Duration Extension", fixed_income)
        
        # Slide 10: Risk Management
        risk_management = """
        <h2>Risk Management Framework</h2>
        
        <h3>Current Risk Assessment</h3>
        <div class="strategy-grid">
            <div class="strategy-card">
                <h4>Volatility Outlook</h4>
                <p><strong>Medium</strong></p>
                <p>Fed transition creates moderate uncertainty</p>
            </div>
            <div class="strategy-card">
                <h4>Cash Allocation</h4>
                <p><strong>5-10%</strong></p>
                <p>Opportunistic positioning</p>
            </div>
        </div>
        
        <h3>Key Risk Factors to Monitor</h3>
        <div class="bullet-point">Federal Reserve communication changes</div>
        <div class="bullet-point">Labor market deterioration signals</div>
        <div class="bullet-point">Inflation re-acceleration</div>
        <div class="bullet-point">Geopolitical developments</div>
        <div class="bullet-point">Credit spread widening</div>
        
        <h3>Rebalancing Protocol</h3>
        <div class="bullet-point"><strong>Normal:</strong> Quarterly rebalancing</div>
        <div class="bullet-point"><strong>Stress:</strong> Monthly adjustments</div>
        <div class="bullet-point"><strong>Events:</strong> Fed meeting-driven changes</div>
        """
        self.add_slide("Risk Management Framework", risk_management)
        
        # Slide 11: Implementation Timeline
        implementation = """
        <h2>Implementation Timeline & Next Steps</h2>
        
        <h3>Immediate Actions (Next 30 Days)</h3>
        <div class="bullet-point">Extend fixed income duration</div>
        <div class="bullet-point">Rebalance sector allocations</div>
        <div class="bullet-point">Implement cash management strategy</div>
        
        <h3>Monitoring Schedule</h3>
        <table class="table">
            <tr>
                <th>Frequency</th>
                <th>Focus Areas</th>
                <th>Key Indicators</th>
            </tr>
            <tr>
                <td>Weekly</td>
                <td>Market Conditions</td>
                <td>VIX, Credit Spreads, Yields</td>
            </tr>
            <tr>
                <td>Monthly</td>
                <td>Economic Data</td>
                <td>CPI, Employment, Fed Minutes</td>
            </tr>
            <tr>
                <td>Quarterly</td>
                <td>Strategy Review</td>
                <td>Portfolio Performance, Rebalancing</td>
            </tr>
        </table>
        
        <h3>Key Upcoming Events</h3>
        <div class="bullet-point">Next Fed Meeting: [Date]</div>
        <div class="bullet-point">CPI Release: [Date]</div>
        <div class="bullet-point">Employment Report: [Date]</div>
        """
        self.add_slide("Implementation Timeline & Next Steps", implementation)
        
        # Slide 12: Q&A
        qa_slide = """
        <div style="text-align: center; margin-top: 150px;">
            <h2 style="border: none; font-size: 48px; color: #667eea;">Questions & Discussion</h2>
            <p style="font-size: 24px; margin-top: 50px;">Thank you for your attention</p>
            <p style="font-size: 18px; margin-top: 30px;">Contact Information:</p>
            <p style="font-size: 16px;">[Your Name] | [Your Email] | [Your Phone]</p>
        </div>
        """
        self.add_slide("Questions & Discussion", qa_slide, "title")
        
    def save_presentation(self, filename="Fed_Policy_Client_Presentation.html"):
        """Save the presentation as HTML file"""
        
        self.create_presentation_slides()
        html_content = self.generate_slides_html()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename
    
    def generate_google_slides_instructions(self):
        """Generate instructions for creating Google Slides"""
        
        instructions = f"""
# Google Slides Creation Instructions

## Step 1: Create New Google Slides Presentation
1. Go to slides.google.com
2. Click "+" to create new presentation
3. Choose "Blank" template
4. Title: "Federal Reserve Policy Analysis - {self.current_date}"

## Step 2: Apply Professional Theme
1. Click "Theme" button (top right)
2. Choose "Modern Writer" or "Swiss" theme
3. Primary color: #667eea (blue)
4. Accent color: #764ba2 (purple)

## Step 3: Import Content Structure
Use the HTML preview file as reference for:
- Slide titles and structure
- Key bullet points and data
- Tables and metrics
- Visual placeholders

## Step 4: Add Charts and Images
1. Insert → Chart → Import from Sheets
2. Add generated PNG files:
   - inflation_ml_predictions.png
   - phillips_curve_evolution.png
   - comprehensive_fed_analysis.png
   - fed_policy_dashboard.png

## Step 5: Customize Design
1. Ensure consistent fonts (Arial or Roboto)
2. Use color scheme throughout
3. Add your company logo
4. Include client branding elements

## Step 6: Review and Share
1. Review all slides for accuracy
2. Check spelling and formatting  
3. Share with client via email or link
4. Set appropriate permissions

## Slide Count: 12 slides
## Presentation Time: 15-20 minutes
## Target Audience: Investment clients
"""
        
        with open("Google_Slides_Instructions.md", 'w') as f:
            f.write(instructions)
        
        return "Google_Slides_Instructions.md"

def main():
    """Generate the Google Slides presentation materials"""
    
    print("🎯 Generating Google Slides Client Presentation...")
    
    # Create presentation generator
    slides = GoogleSlidesGenerator()
    
    # Generate HTML preview
    html_file = slides.save_presentation()
    print(f"✅ HTML preview generated: {html_file}")
    
    # Generate Google Slides instructions
    instructions_file = slides.generate_google_slides_instructions()
    print(f"✅ Instructions created: {instructions_file}")
    
    print(f"\n📊 Presentation Summary:")
    print(f"📁 HTML Preview: {html_file}")
    print(f"📋 Instructions: {instructions_file}")
    print(f"🎯 Slides: 12 professional slides")
    print(f"⏱️ Duration: 15-20 minutes")
    print(f"👥 Audience: Investment clients")
    
    return html_file, instructions_file

if __name__ == "__main__":
    main()