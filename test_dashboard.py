#!/usr/bin/env python3
"""Test the dashboard functionality"""

import pandas as pd
import numpy as np
import sys
import os

# Add current directory to path
sys.path.insert(0, '/Users/chen/claude-code-projects')

try:
    from fred_dashboard import FREDDashboard
    
    # Create dashboard instance
    dashboard = FREDDashboard()
    
    # Test demo data creation
    demo_data = dashboard.create_demo_series('FEDFUNDS', '2020-01-01', '2024-01-01')
    print(f"Demo data shape: {demo_data.shape}")
    print(f"Demo data sample:\n{demo_data.head()}")
    
    # Test correlation chart creation
    dates = pd.date_range('2020-01-01', '2024-01-01', freq='ME')  # Use 'ME' instead of 'M'
    data1 = pd.DataFrame({'value': np.random.randn(len(dates))}, index=dates)
    data2 = pd.DataFrame({'value': np.random.randn(len(dates))}, index=dates)
    
    fig = dashboard.create_correlation_chart(data1, data2, 'Test1', 'Test2', '#1f77b4', '#ff7f0e')
    print(f"Correlation chart created successfully")
    print(f"Figure has {len(fig.data)} traces")
    
    print("✅ All dashboard functions working correctly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()