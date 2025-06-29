#!/usr/bin/env python3
"""
Federal Reserve Data Cleansing Pipeline
=====================================

Comprehensive data cleansing pipeline for Federal Reserve Economic Data (FRED)
used in policy analysis and investment strategy research.

Author: AI Assistant
Date: June 29, 2025
Purpose: Clean and prepare FRED datasets for analysis
"""

import pandas as pd
import numpy as np
import sqlite3
import requests
import os
import warnings
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple, Union
import logging
import argparse
import json

# Configure warnings and logging
warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FedDataCleansingConfig:
    """Configuration class for data cleansing parameters"""
    
    # FRED API Configuration
    FRED_API_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
    FRED_API_KEY = os.getenv('FRED_API_KEY', '852567bee469ec614405e5dce75b847d')
    
    # Database Configuration
    DATABASE_PATH = 'inflation_data.db'
    
    # Data Quality Thresholds
    MAX_MISSING_PERCENTAGE = 0.1  # 10% maximum missing data
    OUTLIER_Z_SCORE_THRESHOLD = 3.0
    MIN_DATA_POINTS = 12  # Minimum 12 data points for series
    
    # Date Range Configuration
    DEFAULT_START_DATE = '2000-01-01'
    DEFAULT_END_DATE = datetime.now().strftime('%Y-%m-%d')
    
    # FRED Series IDs for Federal Reserve Analysis
    FRED_SERIES = {
        'rates': {
            'FEDFUNDS': 'Federal Funds Rate',
            'GS10': '10-Year Treasury Rate',
            'GS2': '2-Year Treasury Rate',
            'GS5': '5-Year Treasury Rate',
            'TB3MS': '3-Month Treasury Rate'
        },
        'inflation': {
            'CPIAUCSL': 'Consumer Price Index',
            'CPILFESL': 'Core CPI',
            'PCEPI': 'PCE Price Index',
            'PCEPILFE': 'Core PCE Price Index'
        },
        'employment': {
            'UNRATE': 'Unemployment Rate',
            'PAYEMS': 'Nonfarm Payrolls',
            'CIVPART': 'Labor Force Participation Rate',
            'EMRATIO': 'Employment-Population Ratio'
        },
        'monetary_policy': {
            'WALCL': 'Fed Balance Sheet',
            'BOGMBASE': 'Monetary Base',
            'M2SL': 'M2 Money Supply'
        },
        'economic_activity': {
            'GDP': 'Gross Domestic Product',
            'INDPRO': 'Industrial Production Index',
            'HOUST': 'Housing Starts',
            'UMCSENT': 'Consumer Sentiment'
        }
    }

class DataQualityAssessment:
    """Class for assessing data quality issues"""
    
    @staticmethod
    def assess_missing_data(df: pd.DataFrame, series_name: str) -> Dict:
        """Assess missing data in a series"""
        total_records = len(df)
        missing_records = df.isnull().sum().sum() if hasattr(df.isnull().sum(), 'sum') else df.isnull().sum()
        missing_percentage = (missing_records / total_records) * 100 if total_records > 0 else 0
        
        return {
            'series_name': series_name,
            'total_records': total_records,
            'missing_records': missing_records,
            'missing_percentage': missing_percentage,
            'quality_flag': 'GOOD' if missing_percentage <= FedDataCleansingConfig.MAX_MISSING_PERCENTAGE * 100 else 'POOR'
        }
    
    @staticmethod
    def detect_outliers(series: pd.Series, method: str = 'zscore') -> pd.Series:
        """Detect outliers using specified method"""
        if method == 'zscore':
            z_scores = np.abs((series - series.mean()) / series.std())
            return z_scores > FedDataCleansingConfig.OUTLIER_Z_SCORE_THRESHOLD
        elif method == 'iqr':
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            return (series < lower_bound) | (series > upper_bound)
        else:
            raise ValueError("Method must be 'zscore' or 'iqr'")
    
    @staticmethod
    def assess_data_consistency(df: pd.DataFrame, date_column: str = 'date') -> Dict:
        """Assess data consistency and continuity"""
        if date_column not in df.columns:
            return {'error': f'Date column {date_column} not found'}
        
        df_sorted = df.sort_values(date_column)
        date_diff = df_sorted[date_column].diff()
        
        # Remove first NaT value from diff
        date_diff = date_diff.dropna()
        
        if len(date_diff) == 0:
            return {'error': 'Insufficient data for consistency assessment'}
        
        # Calculate frequency statistics
        most_common_freq = date_diff.mode().iloc[0] if len(date_diff.mode()) > 0 else None
        
        return {
            'date_range': f"{df_sorted[date_column].min()} to {df_sorted[date_column].max()}",
            'total_periods': len(df_sorted),
            'most_common_frequency': most_common_freq,
            'irregular_intervals': len(date_diff[date_diff != most_common_freq]) if most_common_freq else 0,
            'data_continuity': 'GOOD' if most_common_freq else 'POOR'
        }

class FedDataLoader:
    """Class for loading Federal Reserve data from various sources"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or FedDataCleansingConfig.FRED_API_KEY
        self.base_url = FedDataCleansingConfig.FRED_API_BASE_URL
    
    def fetch_fred_series(self, series_id: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Fetch data from FRED API"""
        try:
            params = {
                'series_id': series_id,
                'api_key': self.api_key,
                'file_type': 'json',
                'observation_start': start_date or FedDataCleansingConfig.DEFAULT_START_DATE,
                'observation_end': end_date or FedDataCleansingConfig.DEFAULT_END_DATE
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'observations' not in data:
                logger.warning(f"No observations found for series {series_id}")
                return pd.DataFrame()
            
            df = pd.DataFrame(data['observations'])
            
            if df.empty:
                logger.warning(f"Empty dataset returned for series {series_id}")
                return df
            
            # Basic preprocessing
            df['date'] = pd.to_datetime(df['date'])
            df[series_id] = pd.to_numeric(df['value'], errors='coerce')
            df = df[['date', series_id]].dropna()
            
            logger.info(f"Successfully fetched {len(df)} records for {series_id}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching {series_id}: {str(e)}")
            return pd.DataFrame()
    
    def load_from_database(self, table_name: str = 'fed_policy_data') -> pd.DataFrame:
        """Load data from SQLite database"""
        try:
            conn = sqlite3.connect(FedDataCleansingConfig.DATABASE_PATH)
            
            # Check if table exists
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            
            if not cursor.fetchone():
                logger.warning(f"Table {table_name} not found in database")
                return pd.DataFrame()
            
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            conn.close()
            
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            
            logger.info(f"Loaded {len(df)} records from database table {table_name}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading from database: {str(e)}")
            return pd.DataFrame()
    
    def load_from_csv(self, file_path: str) -> pd.DataFrame:
        """Load data from CSV file"""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"CSV file not found: {file_path}")
                return pd.DataFrame()
            
            df = pd.read_csv(file_path)
            
            # Try to identify date column
            date_columns = ['date', 'Date', 'DATE', 'observation_date']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    if col != 'date':
                        df = df.rename(columns={col: 'date'})
                    break
            
            logger.info(f"Loaded {len(df)} records from CSV: {file_path}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading CSV {file_path}: {str(e)}")
            return pd.DataFrame()

class FedDataCleaner:
    """Comprehensive data cleansing class for Federal Reserve data"""
    
    def __init__(self):
        self.cleaning_log = []
    
    def log_cleaning_action(self, action: str, series_name: str, details: str = ""):
        """Log cleaning actions for audit trail"""
        self.cleaning_log.append({
            'timestamp': datetime.now(),
            'action': action,
            'series': series_name,
            'details': details
        })
    
    def standardize_date_format(self, df: pd.DataFrame, date_column: str = 'date') -> pd.DataFrame:
        """Standardize date formats across datasets"""
        if date_column not in df.columns:
            logger.warning(f"Date column '{date_column}' not found")
            return df
        
        try:
            original_format = df[date_column].dtype
            df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
            
            # Remove rows with invalid dates
            before_count = len(df)
            df = df.dropna(subset=[date_column])
            after_count = len(df)
            
            if before_count != after_count:
                self.log_cleaning_action(
                    'DATE_STANDARDIZATION', 
                    'UNKNOWN',
                    f"Removed {before_count - after_count} rows with invalid dates"
                )
            
            logger.info(f"Standardized date format from {original_format} to datetime64")
            return df
            
        except Exception as e:
            logger.error(f"Error standardizing dates: {str(e)}")
            return df
    
    def handle_missing_values(self, df: pd.DataFrame, series_name: str, method: str = 'interpolate') -> pd.DataFrame:
        """Handle missing values using specified method"""
        if df.empty:
            return df
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            missing_count = df[col].isnull().sum()
            
            if missing_count == 0:
                continue
            
            original_count = len(df)
            
            if method == 'interpolate':
                df[col] = df[col].interpolate(method='linear')
            elif method == 'forward_fill':
                df[col] = df[col].fillna(method='ffill')
            elif method == 'backward_fill':
                df[col] = df[col].fillna(method='bfill')
            elif method == 'drop':
                df = df.dropna(subset=[col])
            elif method == 'mean':
                df[col] = df[col].fillna(df[col].mean())
            elif method == 'median':
                df[col] = df[col].fillna(df[col].median())
            
            self.log_cleaning_action(
                'MISSING_VALUES', 
                series_name,
                f"Column {col}: {missing_count} missing values handled using {method}"
            )
        
        return df
    
    def remove_outliers(self, df: pd.DataFrame, series_name: str, method: str = 'zscore', 
                       threshold: float = None) -> pd.DataFrame:
        """Remove or cap outliers"""
        if df.empty:
            return df
        
        threshold = threshold or FedDataCleansingConfig.OUTLIER_Z_SCORE_THRESHOLD
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if col == 'date':  # Skip date columns
                continue
                
            outliers = DataQualityAssessment.detect_outliers(df[col], method=method)
            outlier_count = outliers.sum()
            
            if outlier_count > 0:
                # Cap outliers instead of removing them to preserve time series continuity
                if method == 'zscore':
                    mean_val = df[col].mean()
                    std_val = df[col].std()
                    upper_bound = mean_val + threshold * std_val
                    lower_bound = mean_val - threshold * std_val
                    
                    df.loc[df[col] > upper_bound, col] = upper_bound
                    df.loc[df[col] < lower_bound, col] = lower_bound
                
                elif method == 'iqr':
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    upper_bound = Q3 + 1.5 * IQR
                    lower_bound = Q1 - 1.5 * IQR
                    
                    df.loc[df[col] > upper_bound, col] = upper_bound
                    df.loc[df[col] < lower_bound, col] = lower_bound
                
                self.log_cleaning_action(
                    'OUTLIER_TREATMENT', 
                    series_name,
                    f"Column {col}: {outlier_count} outliers capped using {method} method"
                )
        
        return df
    
    def standardize_frequency(self, df: pd.DataFrame, series_name: str, 
                            target_freq: str = 'M', date_column: str = 'date') -> pd.DataFrame:
        """Standardize data frequency (e.g., monthly, quarterly)"""
        if df.empty or date_column not in df.columns:
            return df
        
        try:
            df = df.sort_values(date_column)
            df = df.set_index(date_column)
            
            # Resample to target frequency
            if target_freq == 'M':  # Monthly
                df_resampled = df.resample('M').last()  # Use last value of month
            elif target_freq == 'Q':  # Quarterly
                df_resampled = df.resample('Q').last()
            elif target_freq == 'A':  # Annual
                df_resampled = df.resample('A').last()
            else:
                logger.warning(f"Unsupported frequency: {target_freq}")
                return df.reset_index()
            
            df_resampled = df_resampled.reset_index()
            
            self.log_cleaning_action(
                'FREQUENCY_STANDARDIZATION', 
                series_name,
                f"Resampled to {target_freq} frequency: {len(df)} -> {len(df_resampled)} records"
            )
            
            return df_resampled
            
        except Exception as e:
            logger.error(f"Error standardizing frequency for {series_name}: {str(e)}")
            return df.reset_index() if date_column in df.index.names else df
    
    def validate_data_range(self, df: pd.DataFrame, series_name: str, 
                          expected_min: float = None, expected_max: float = None) -> pd.DataFrame:
        """Validate data is within expected ranges"""
        if df.empty:
            return df
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if col == 'date':  # Skip date columns
                continue
            
            # Define reasonable ranges for common Fed series
            if expected_min is None or expected_max is None:
                if 'FEDFUNDS' in col or 'GS' in col or 'TB' in col:
                    # Interest rates: -1% to 25%
                    min_val, max_val = -1, 25
                elif 'UNRATE' in col:
                    # Unemployment rate: 0% to 25%
                    min_val, max_val = 0, 25
                elif 'CPI' in col and 'rate' in series_name.lower():
                    # Inflation rate: -10% to 20%
                    min_val, max_val = -10, 20
                else:
                    # Default: no range validation
                    continue
            else:
                min_val, max_val = expected_min, expected_max
            
            # Count and flag out-of-range values
            out_of_range = (df[col] < min_val) | (df[col] > max_val)
            out_of_range_count = out_of_range.sum()
            
            if out_of_range_count > 0:
                self.log_cleaning_action(
                    'RANGE_VALIDATION', 
                    series_name,
                    f"Column {col}: {out_of_range_count} values outside expected range [{min_val}, {max_val}]"
                )
                
                # Optionally cap extreme values
                df.loc[df[col] < min_val, col] = min_val
                df.loc[df[col] > max_val, col] = max_val
        
        return df
    
    def get_cleaning_summary(self) -> pd.DataFrame:
        """Get summary of all cleaning actions performed"""
        if not self.cleaning_log:
            return pd.DataFrame()
        
        return pd.DataFrame(self.cleaning_log)

class FedDataCleansingPipeline:
    """Main pipeline class that orchestrates the entire cleansing process"""
    
    def __init__(self, config: FedDataCleansingConfig = None):
        self.config = config or FedDataCleansingConfig()
        self.loader = FedDataLoader()
        self.cleaner = FedDataCleaner()
        self.quality_assessor = DataQualityAssessment()
        self.cleaned_datasets = {}
        self.quality_reports = {}
    
    def process_single_series(self, series_id: str, series_name: str, 
                            cleansing_options: Dict = None) -> Dict:
        """Process a single FRED series through the complete pipeline"""
        
        default_options = {
            'missing_value_method': 'interpolate',
            'outlier_method': 'zscore',
            'outlier_threshold': 3.0,
            'target_frequency': 'M',
            'validate_range': True
        }
        
        options = {**default_options, **(cleansing_options or {})}
        
        logger.info(f"Processing series: {series_id} ({series_name})")
        
        # Step 1: Load data
        df = self.loader.fetch_fred_series(series_id)
        
        if df.empty:
            logger.warning(f"No data loaded for {series_id}")
            return {'status': 'failed', 'reason': 'no_data'}
        
        # Step 2: Initial quality assessment
        initial_quality = self.quality_assessor.assess_missing_data(df, series_name)
        consistency_check = self.quality_assessor.assess_data_consistency(df)
        
        # Step 3: Data cleansing steps
        df = self.cleaner.standardize_date_format(df)
        df = self.cleaner.handle_missing_values(df, series_name, options['missing_value_method'])
        df = self.cleaner.remove_outliers(df, series_name, options['outlier_method'], options['outlier_threshold'])
        
        if options['validate_range']:
            df = self.cleaner.validate_data_range(df, series_name)
        
        df = self.cleaner.standardize_frequency(df, series_name, options['target_frequency'])
        
        # Step 4: Final quality assessment
        final_quality = self.quality_assessor.assess_missing_data(df, series_name)
        
        # Step 5: Store results
        self.cleaned_datasets[series_id] = df
        self.quality_reports[series_id] = {
            'series_name': series_name,
            'initial_quality': initial_quality,
            'final_quality': final_quality,
            'consistency_check': consistency_check,
            'cleansing_options': options,
            'final_record_count': len(df),
            'date_range': f"{df['date'].min()} to {df['date'].max()}" if not df.empty else "N/A"
        }
        
        logger.info(f"Successfully processed {series_id}: {len(df)} records")
        return {'status': 'success', 'records': len(df)}
    
    def process_all_series(self, categories: List[str] = None) -> Dict:
        """Process all series in specified categories"""
        
        categories = categories or list(self.config.FRED_SERIES.keys())
        results = {'success': [], 'failed': []}
        
        print(f"\\n🚀 Starting comprehensive cleansing pipeline for {len(categories)} categories")
        print("=" * 70)
        
        for category in categories:
            if category not in self.config.FRED_SERIES:
                logger.warning(f"Category {category} not found in configuration")
                continue
            
            print(f"\\n📊 Processing category: {category.upper()}")
            print("-" * 50)
            
            for series_id, series_name in self.config.FRED_SERIES[category].items():
                result = self.process_single_series(series_id, series_name)
                
                if result['status'] == 'success':
                    print(f"✅ {series_id}: {result['records']} records")
                    results['success'].append(series_id)
                else:
                    print(f"❌ {series_id}: {result.get('reason', 'unknown error')}")
                    results['failed'].append(series_id)
        
        print(f"\\n📈 Pipeline Summary:")
        print(f"✅ Successful: {len(results['success'])} series")
        print(f"❌ Failed: {len(results['failed'])} series")
        
        return results
    
    def generate_quality_report(self) -> pd.DataFrame:
        """Generate comprehensive data quality report"""
        
        report_data = []
        
        for series_id, report in self.quality_reports.items():
            report_data.append({
                'Series_ID': series_id,
                'Series_Name': report['series_name'],
                'Initial_Records': report['initial_quality']['total_records'],
                'Final_Records': report['final_record_count'],
                'Initial_Missing_%': report['initial_quality']['missing_percentage'],
                'Final_Missing_%': report['final_quality']['missing_percentage'],
                'Quality_Flag': report['final_quality']['quality_flag'],
                'Date_Range': report['date_range'],
                'Data_Continuity': report['consistency_check'].get('data_continuity', 'UNKNOWN')
            })
        
        return pd.DataFrame(report_data)
    
    def export_cleaned_data(self, output_format: str = 'csv', output_dir: str = 'cleaned_data') -> None:
        """Export cleaned datasets"""
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        for series_id, df in self.cleaned_datasets.items():
            if output_format == 'csv':
                output_path = os.path.join(output_dir, f"{series_id}_cleaned.csv")
                df.to_csv(output_path, index=False)
            elif output_format == 'sqlite':
                output_path = os.path.join(output_dir, 'cleaned_fed_data.db')
                conn = sqlite3.connect(output_path)
                df.to_sql(f"{series_id}_cleaned", conn, if_exists='replace', index=False)
                conn.close()
        
        logger.info(f"Exported {len(self.cleaned_datasets)} datasets to {output_dir}")
    
    def create_summary_visualization(self, output_path: str = 'data_quality_dashboard.png') -> None:
        """Create data quality visualization dashboard"""
        
        if not self.quality_reports:
            logger.warning("No quality reports available for visualization")
            return
        
        quality_df = self.generate_quality_report()
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Federal Reserve Data Quality Dashboard', fontsize=16, fontweight='bold')
        
        # 1. Quality Flag Distribution
        ax1 = axes[0, 0]
        quality_counts = quality_df['Quality_Flag'].value_counts()
        colors = ['green' if flag == 'GOOD' else 'red' for flag in quality_counts.index]
        ax1.pie(quality_counts.values, labels=quality_counts.index, autopct='%1.1f%%', colors=colors)
        ax1.set_title('Data Quality Distribution')
        
        # 2. Record Count by Series
        ax2 = axes[0, 1]
        ax2.bar(range(len(quality_df)), quality_df['Final_Records'])
        ax2.set_title('Record Count by Series')
        ax2.set_xlabel('Series Index')
        ax2.set_ylabel('Record Count')
        
        # 3. Missing Data Percentage
        ax3 = axes[1, 0]
        ax3.hist(quality_df['Final_Missing_%'], bins=10, alpha=0.7, color='blue')
        ax3.set_title('Distribution of Missing Data %')
        ax3.set_xlabel('Missing Data %')
        ax3.set_ylabel('Frequency')
        
        # 4. Data Continuity
        ax4 = axes[1, 1]
        continuity_counts = quality_df['Data_Continuity'].value_counts()
        ax4.bar(continuity_counts.index, continuity_counts.values)
        ax4.set_title('Data Continuity Assessment')
        ax4.set_ylabel('Count')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Quality dashboard saved to {output_path}")

def main():
    """Main execution function"""
    
    parser = argparse.ArgumentParser(description='Federal Reserve Data Cleansing Pipeline')
    parser.add_argument('--categories', nargs='+', default=None,
                       help='Categories to process (rates, inflation, employment, monetary_policy, economic_activity)')
    parser.add_argument('--output-dir', default='cleaned_fed_data',
                       help='Output directory for cleaned data')
    parser.add_argument('--output-format', choices=['csv', 'sqlite'], default='csv',
                       help='Output format for cleaned data')
    parser.add_argument('--config-file', default=None,
                       help='Path to custom configuration file')
    parser.add_argument('--create-dashboard', action='store_true',
                       help='Create data quality dashboard')
    
    args = parser.parse_args()
    
    print("🏛️ Federal Reserve Data Cleansing Pipeline")
    print("=" * 60)
    print(f"📅 Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize pipeline
    config = FedDataCleansingConfig()
    pipeline = FedDataCleansingPipeline(config)
    
    # Load custom configuration if provided
    if args.config_file and os.path.exists(args.config_file):
        with open(args.config_file, 'r') as f:
            custom_config = json.load(f)
            # Update configuration with custom values
            for key, value in custom_config.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        logger.info(f"Loaded custom configuration from {args.config_file}")
    
    # Process data
    results = pipeline.process_all_series(args.categories)
    
    # Generate and save quality report
    if pipeline.quality_reports:
        quality_report = pipeline.generate_quality_report()
        
        print("\\n📋 Data Quality Summary:")
        print(f"Total series processed: {len(quality_report)}")
        print(f"Good quality series: {len(quality_report[quality_report['Quality_Flag'] == 'GOOD'])}")
        print(f"Average record count: {quality_report['Final_Records'].mean():.0f}")
        print(f"Average missing data %: {quality_report['Final_Missing_%'].mean():.2f}%")
        
        # Save quality report
        quality_report_path = os.path.join(args.output_dir, 'data_quality_report.csv')
        if not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir)
        quality_report.to_csv(quality_report_path, index=False)
        print(f"✅ Quality report saved to {quality_report_path}")
    
    # Export cleaned data
    if pipeline.cleaned_datasets:
        pipeline.export_cleaned_data(args.output_format, args.output_dir)
        print(f"✅ Cleaned datasets exported to {args.output_dir}")
        
        # Save cleaning log
        cleaning_log = pipeline.cleaner.get_cleaning_summary()
        if not cleaning_log.empty:
            cleaning_log_path = os.path.join(args.output_dir, 'cleaning_actions_log.csv')
            cleaning_log.to_csv(cleaning_log_path, index=False)
            print(f"✅ Cleaning log saved to {cleaning_log_path}")
    
    # Create dashboard if requested
    if args.create_dashboard:
        dashboard_path = os.path.join(args.output_dir, 'data_quality_dashboard.png')
        pipeline.create_summary_visualization(dashboard_path)
        print(f"✅ Data quality dashboard created: {dashboard_path}")
    
    print(f"\\n✅ Pipeline execution completed successfully!")
    print(f"📊 Processed {len(results['success'])} series successfully")
    print(f"📁 Output directory: {args.output_dir}")
    
    return pipeline

if __name__ == "__main__":
    pipeline = main()