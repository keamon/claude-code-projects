#!/usr/bin/env python3
"""
Interactive Federal Reserve Economic Data Dashboard
Streamlit app for visualizing FRED API data with multiple panels and correlation analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import os
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Federal Reserve Economic Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(90deg, #f0f8ff, #e6f3ff);
        border-radius: 10px;
        border: 2px solid #1f77b4;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .correlation-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
    }
    
    .stSelectbox > div > div {
        background-color: #f8f9fa;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f0f8ff, #ffffff);
    }
</style>
""", unsafe_allow_html=True)

class FREDDashboard:
    """Interactive FRED data dashboard"""
    
    def __init__(self):
        self.base_url = "https://api.stlouisfed.org/fred"
        self.session = requests.Session()
        
        # Key economic indicators with descriptions
        self.indicators = {
            'Federal Funds Rate': {
                'series_id': 'FEDFUNDS',
                'description': 'Target federal funds rate set by FOMC',
                'unit': 'Percent',
                'color': '#1f77b4'
            },
            '10-Year Treasury': {
                'series_id': 'GS10',
                'description': '10-Year Treasury Constant Maturity Rate',
                'unit': 'Percent',
                'color': '#ff7f0e'
            },
            '2-Year Treasury': {
                'series_id': 'GS2',
                'description': '2-Year Treasury Constant Maturity Rate',
                'unit': 'Percent',
                'color': '#2ca02c'
            },
            'Unemployment Rate': {
                'series_id': 'UNRATE',
                'description': 'Unemployment Rate (Seasonally Adjusted)',
                'unit': 'Percent',
                'color': '#d62728'
            },
            'Core CPI': {
                'series_id': 'CPILFESL',
                'description': 'Consumer Price Index: All Items Less Food & Energy',
                'unit': 'Index',
                'color': '#9467bd'
            },
            'Core PCE': {
                'series_id': 'PCEPILFE',
                'description': 'Personal Consumption Expenditures: Core',
                'unit': 'Index',
                'color': '#8c564b'
            },
            'Inflation Rate (CPI)': {
                'series_id': 'CPIAUCSL',
                'description': 'Consumer Price Index for All Urban Consumers: All Items',
                'unit': 'Index',
                'color': '#ff1744'
            },
            'YoY Inflation Rate': {
                'series_id': 'CPIAUCSL_YOY',
                'description': 'Year-over-Year Inflation Rate (CPI)',
                'unit': 'Percent',
                'color': '#e91e63'
            },
            'GDP Growth': {
                'series_id': 'GDPC1',
                'description': 'Real Gross Domestic Product',
                'unit': 'Billions of Chained 2017 Dollars',
                'color': '#e377c2'
            },
            'Consumer Sentiment': {
                'series_id': 'UMCSENT',
                'description': 'University of Michigan Consumer Sentiment',
                'unit': 'Index',
                'color': '#7f7f7f'
            },
            'VIX': {
                'series_id': 'VIXCLS',
                'description': 'CBOE Volatility Index',
                'unit': 'Index',
                'color': '#bcbd22'
            },
            'Dollar Index': {
                'series_id': 'DEXUSEU',
                'description': 'U.S. Dollar to Euro Exchange Rate',
                'unit': 'USD per EUR',
                'color': '#17becf'
            }
        }
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def fetch_series(_self, series_id: str, start_date: str, end_date: str, api_key: str) -> pd.DataFrame:
        """Fetch time series data from FRED API with caching"""
        
        # Check if this is a calculated YoY inflation rate
        if series_id == 'CPIAUCSL_YOY':
            return _self.calculate_yoy_inflation(start_date, end_date, api_key)
        
        if not api_key or api_key == "demo":
            return _self.create_demo_series(series_id, start_date, end_date)
        
        url = f"{_self.base_url}/series/observations"
        params = {
            'series_id': series_id,
            'api_key': api_key,
            'file_type': 'json',
            'observation_start': start_date,
            'observation_end': end_date
        }
        
        try:
            response = _self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'observations' not in data:
                return pd.DataFrame()
                
            df = pd.DataFrame(data['observations'])
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df = df.dropna(subset=['value'])
            df = df.set_index('date').sort_index()
            
            return df[['value']]
            
        except Exception as e:
            st.warning(f"API error for {series_id}: {str(e)}. Using demo data.")
            return _self.create_demo_series(series_id, start_date, end_date)
    
    def calculate_yoy_inflation(self, start_date: str, end_date: str, api_key: str) -> pd.DataFrame:
        """Calculate year-over-year inflation rate from CPI data"""
        
        if not api_key or api_key == "demo":
            return self.create_demo_series('CPIAUCSL_YOY', start_date, end_date)
        
        # Extend start date by 1 year to ensure we have enough data for YoY calculation
        extended_start = pd.to_datetime(start_date) - pd.DateOffset(years=1)
        extended_start_str = extended_start.strftime('%Y-%m-%d')
        
        # Fetch CPI data directly (avoid recursion)
        url = f"{self.base_url}/series/observations"
        params = {
            'series_id': 'CPIAUCSL',
            'api_key': api_key,
            'file_type': 'json',
            'observation_start': extended_start_str,
            'observation_end': end_date
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'observations' not in data:
                return self.create_demo_series('CPIAUCSL_YOY', start_date, end_date)
                
            df = pd.DataFrame(data['observations'])
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df = df.dropna(subset=['value'])
            df = df.set_index('date').sort_index()
            
            # Calculate year-over-year percentage change
            yoy_inflation = df.pct_change(periods=12) * 100  # 12 months = 1 year
            
            # Filter to original date range
            yoy_inflation = yoy_inflation[yoy_inflation.index >= start_date]
            
            return yoy_inflation.dropna()
            
        except Exception as e:
            st.warning(f"API error calculating YoY inflation: {str(e)}. Using demo data.")
            return self.create_demo_series('CPIAUCSL_YOY', start_date, end_date)
    
    def create_demo_series(self, series_id: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Create demo data for specific series"""
        dates = pd.date_range(start=start_date, end=end_date, freq='M')
        np.random.seed(hash(series_id) % 1000)  # Consistent seed per series
        
        # Base patterns for different series
        base_values = {
            'FEDFUNDS': np.concatenate([
                np.linspace(2.5, 0.25, len(dates)//4),
                np.repeat(0.25, len(dates)//2),
                np.linspace(0.25, 5.25, len(dates) - 3*len(dates)//4)
            ]),
            'GS10': np.concatenate([
                np.linspace(2.7, 0.7, len(dates)//3),
                np.linspace(0.7, 4.5, len(dates) - len(dates)//3)
            ]),
            'GS2': np.concatenate([
                np.linspace(2.5, 0.1, len(dates)//3),
                np.linspace(0.1, 4.8, len(dates) - len(dates)//3)
            ]),
            'UNRATE': np.concatenate([
                [3.7] * 3,
                [14.8, 11.1, 8.4],
                np.linspace(8.4, 3.7, len(dates) - 6)
            ]) if len(dates) > 6 else np.repeat(3.7, len(dates)),
            'CPILFESL': np.cumsum(np.random.normal(0.2, 0.5, len(dates))) + 250,
            'PCEPILFE': np.cumsum(np.random.normal(0.15, 0.3, len(dates))) + 100,
            'CPIAUCSL': np.cumsum(np.random.normal(0.2, 0.4, len(dates))) + 280,
            'CPIAUCSL_YOY': np.concatenate([
                [2.1] * 12,                     # Pre-COVID stable 2%
                np.linspace(2.1, 0.5, 12),      # COVID deflation
                np.linspace(0.5, 9.1, 12),      # Inflation surge 2021
                np.linspace(9.1, 3.2, len(dates) - 36)  # Recent decline
            ])[:len(dates)],
            'GDPC1': np.cumsum(np.random.normal(50, 100, len(dates))) + 20000,
            'UMCSENT': np.random.normal(80, 10, len(dates)),
            'VIXCLS': np.abs(np.random.normal(18, 8, len(dates))),
            'DEXUSEU': np.random.normal(0.85, 0.05, len(dates))
        }
        
        values = base_values.get(series_id, np.random.normal(100, 10, len(dates)))
        
        return pd.DataFrame({'value': values[:len(dates)]}, index=dates)
    
    def create_metric_chart(self, data: pd.DataFrame, title: str, color: str, unit: str) -> go.Figure:
        """Create an individual metric chart"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['value'],
            mode='lines',
            name=title,
            line=dict(color=color, width=3),
            hovertemplate=f'<b>{title}</b><br>Date: %{{x}}<br>Value: %{{y:.2f}} {unit}<extra></extra>'
        ))
        
        # Add trend line
        if len(data) > 1:
            z = np.polyfit(range(len(data)), data['value'], 1)
            trend_line = np.poly1d(z)
            fig.add_trace(go.Scatter(
                x=data.index,
                y=trend_line(range(len(data))),
                mode='lines',
                name='Trend',
                line=dict(color=color, width=1, dash='dash'),
                opacity=0.6,
                hovertemplate='<b>Trend Line</b><extra></extra>'
            ))
        
        fig.update_layout(
            title=dict(
                text=f'<b>{title}</b>',
                x=0.5,
                font=dict(size=16)
            ),
            xaxis_title='Date',
            yaxis_title=f'{title} ({unit})',
            hovermode='x unified',
            template='plotly_white',
            height=350,
            margin=dict(t=50, b=50, l=50, r=50),
            showlegend=False
        )
        
        return fig
    
    def create_correlation_chart(self, data1: pd.DataFrame, data2: pd.DataFrame, 
                               name1: str, name2: str, color1: str, color2: str) -> go.Figure:
        """Create correlation scatter plot"""
        
        # Align data by date
        combined = pd.merge(data1, data2, left_index=True, right_index=True, suffixes=('_1', '_2'))
        combined = combined.dropna()
        
        if len(combined) < 2:
            fig = go.Figure()
            fig.add_annotation(text="Insufficient data for correlation analysis", 
                             x=0.5, y=0.5, showarrow=False)
            return fig
        
        # Calculate correlation
        correlation = combined['value_1'].corr(combined['value_2'])
        
        fig = go.Figure()
        
        # Create time-based color values with proper scaling
        min_date = combined.index.min()
        max_date = combined.index.max()
        
        # Convert dates to years as float for colorbar
        color_values = combined.index.year + (combined.index.month - 1) / 12
        
        # Create custom tick values and labels for colorbar
        year_range = max_date.year - min_date.year + 1
        if year_range <= 5:
            # Show every year if range is small
            tick_years = list(range(min_date.year, max_date.year + 1))
        else:
            # Show every 2-3 years if range is large
            step = max(1, year_range // 5)
            tick_years = list(range(min_date.year, max_date.year + 1, step))
        
        tick_vals = tick_years
        tick_text = [str(year) for year in tick_years]
        
        fig.add_trace(go.Scatter(
            x=combined['value_1'],
            y=combined['value_2'],
            mode='markers',
            name=f'{name1} vs {name2}',
            marker=dict(
                color=color_values,
                colorscale='Viridis',
                size=8,
                opacity=0.7,
                colorbar=dict(
                    title=dict(text="Time Period", side="right"),
                    tickmode="array",
                    tickvals=tick_vals,
                    ticktext=tick_text,
                    len=0.8,
                    thickness=15
                )
            ),
            hovertemplate=f'<b>Date: %{{text}}</b><br>{name1}: %{{x:.2f}}<br>{name2}: %{{y:.2f}}<extra></extra>',
            text=combined.index.strftime('%Y-%m-%d')
        ))
        
        # Add trend line
        z = np.polyfit(combined['value_1'], combined['value_2'], 1)
        trend_line = np.poly1d(z)
        x_trend = np.linspace(combined['value_1'].min(), combined['value_1'].max(), 100)
        
        fig.add_trace(go.Scatter(
            x=x_trend,
            y=trend_line(x_trend),
            mode='lines',
            name='Trend',
            line=dict(color='red', width=2, dash='dash'),
            hovertemplate='<b>Trend Line</b><extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text=f'<b>{name1} vs {name2}</b><br><sub>Correlation: {correlation:.3f}</sub>',
                x=0.5,
                font=dict(size=16)
            ),
            xaxis_title=name1,
            yaxis_title=name2,
            template='plotly_white',
            height=500,
            showlegend=False
        )
        
        return fig

def main():
    """Main dashboard application"""
    
    # Initialize dashboard
    dashboard = FREDDashboard()
    
    # Header
    st.markdown('<div class="main-header">🏦 Federal Reserve Economic Dashboard</div>', 
                unsafe_allow_html=True)
    
    # Sidebar configuration
    st.sidebar.header("📊 Dashboard Configuration")
    
    # API Key input
    api_key = st.sidebar.text_input(
        "FRED API Key (optional)",
        type="password",
        help="Get free API key at https://fred.stlouisfed.org/docs/api/api_key.html"
    )
    
    if not api_key:
        st.sidebar.info("💡 Using demo data. Enter API key for real-time data.")
    
    # Time range selector
    st.sidebar.subheader("📅 Time Range")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=365*5),
            max_value=datetime.now()
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            max_value=datetime.now()
        )
    
    # Convert dates to strings
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    # Main dashboard content
    st.header("📈 Economic Indicators")
    
    # Create 4 panels with dropdowns
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    columns = [col1, col2, col3, col4]
    panel_data = {}
    
    # Panel selection and display
    for i, col in enumerate(columns):
        with col:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            
            selected_metric = st.selectbox(
                f"Panel {i+1} Metric",
                options=list(dashboard.indicators.keys()),
                index=i % len(dashboard.indicators),
                key=f"panel_{i}"
            )
            
            # Fetch and display data
            indicator_info = dashboard.indicators[selected_metric]
            data = dashboard.fetch_series(
                indicator_info['series_id'],
                start_str,
                end_str,
                api_key or "demo"
            )
            
            if not data.empty:
                # Store data for correlation analysis
                panel_data[selected_metric] = data
                
                # Create and display chart
                fig = dashboard.create_metric_chart(
                    data,
                    selected_metric,
                    indicator_info['color'],
                    indicator_info['unit']
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Display current value and stats
                current_value = data['value'].iloc[-1]
                change_30d = ((current_value - data['value'].iloc[-min(30, len(data)-1)]) 
                             / data['value'].iloc[-min(30, len(data)-1)] * 100) if len(data) > 1 else 0
                
                st.metric(
                    label=f"Current {selected_metric}",
                    value=f"{current_value:.2f} {indicator_info['unit']}",
                    delta=f"{change_30d:+.2f}% (30d)"
                )
            else:
                st.error(f"No data available for {selected_metric}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Correlation Analysis Section
    st.markdown('<div class="correlation-section">', unsafe_allow_html=True)
    st.header("🔗 Correlation Analysis")
    
    if len(panel_data) >= 2:
        col1, col2 = st.columns(2)
        
        with col1:
            metric1 = st.selectbox(
                "First Metric",
                options=list(panel_data.keys()),
                key="corr_metric1"
            )
        
        with col2:
            metric2 = st.selectbox(
                "Second Metric",
                options=[m for m in panel_data.keys() if m != metric1],
                key="corr_metric2"
            )
        
        if metric1 and metric2 and metric1 != metric2:
            # Create correlation chart
            fig = dashboard.create_correlation_chart(
                panel_data[metric1],
                panel_data[metric2],
                metric1,
                metric2,
                dashboard.indicators[metric1]['color'],
                dashboard.indicators[metric2]['color']
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Correlation statistics
            combined = pd.merge(
                panel_data[metric1], 
                panel_data[metric2], 
                left_index=True, 
                right_index=True, 
                suffixes=('_1', '_2')
            ).dropna()
            
            if len(combined) > 1:
                correlation = combined['value_1'].corr(combined['value_2'])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Correlation Coefficient", f"{correlation:.3f}")
                with col2:
                    relationship = "Strong" if abs(correlation) > 0.7 else "Moderate" if abs(correlation) > 0.3 else "Weak"
                    st.metric("Relationship Strength", relationship)
                with col3:
                    direction = "Positive" if correlation > 0 else "Negative"
                    st.metric("Direction", direction)
    else:
        st.info("Select metrics in the panels above to enable correlation analysis.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<div style="text-align: center; color: #666; font-size: 0.9em;">'
        '📊 Federal Reserve Economic Data Dashboard | '
        'Data Source: <a href="https://fred.stlouisfed.org/">FRED API</a> | '
        f'Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        '</div>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()