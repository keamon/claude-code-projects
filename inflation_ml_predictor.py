import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import sqlite3
import warnings
from datetime import datetime, timedelta
import joblib

# Time series specific imports
try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.stattools import adfuller
    from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False
    print("Warning: statsmodels not available. ARIMA model will be skipped.")

try:
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping
    import tensorflow as tf
    tf.random.set_seed(42)
    HAS_TENSORFLOW = False  # Set to False to avoid TensorFlow issues
except ImportError:
    HAS_TENSORFLOW = False

warnings.filterwarnings('ignore')
np.random.seed(42)

class InflationPredictor:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.data = None
        self.features = None
        self.target = None
        
    def load_data(self):
        """Load inflation data from SQLite database"""
        try:
            conn = sqlite3.connect('inflation_data.db')
            query = """
            SELECT date, value as cpi, inflation_rate 
            FROM cpi_data 
            WHERE inflation_rate IS NOT NULL
            ORDER BY date
            """
            df = pd.read_sql_query(query, conn)
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            conn.close()
            
            # Remove any remaining NaN values
            df = df.dropna()
            
            print(f"Loaded {len(df)} data points")
            print(f"Date range: {df.index.min()} to {df.index.max()}")
            
            self.data = df
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def create_features(self, lookback_periods=6):
        """Create features for ML models"""
        df = self.data.copy()
        
        # Create lagged features
        for i in range(1, lookback_periods + 1):
            df[f'inflation_lag_{i}'] = df['inflation_rate'].shift(i)
            df[f'cpi_lag_{i}'] = df['cpi'].shift(i)
        
        # Create rolling statistics
        for window in [3, 6, 12]:
            df[f'inflation_rolling_mean_{window}'] = df['inflation_rate'].rolling(window).mean()
            df[f'inflation_rolling_std_{window}'] = df['inflation_rate'].rolling(window).std()
            df[f'cpi_rolling_mean_{window}'] = df['cpi'].rolling(window).mean()
        
        # Create trend features
        df['inflation_diff'] = df['inflation_rate'].diff()
        df['inflation_diff_2'] = df['inflation_rate'].diff(2)
        df['cpi_pct_change'] = df['cpi'].pct_change()
        
        # Create seasonal features
        df['month'] = df.index.month
        df['quarter'] = df.index.quarter
        df['year'] = df.index.year
        
        # Create cyclical features
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        # Drop rows with NaN values created by lagging
        df = df.dropna()
        
        # Separate features and target
        target_col = 'inflation_rate'
        feature_cols = [col for col in df.columns if col not in ['inflation_rate', 'cpi']]
        
        self.features = df[feature_cols]
        self.target = df[target_col]
        
        print(f"Created {len(feature_cols)} features")
        print(f"Features: {feature_cols}")
        print(f"Training data shape: {self.features.shape}")
        
        return df
    
    def prepare_lstm_data(self, sequence_length=12):
        """Prepare data for LSTM model"""
        if not HAS_TENSORFLOW:
            return None, None, None, None
            
        data = self.data['inflation_rate'].values
        
        # Create sequences
        X, y = [], []
        for i in range(sequence_length, len(data)):
            X.append(data[i-sequence_length:i])
            y.append(data[i])
        
        X, y = np.array(X), np.array(y)
        
        # Split data
        split_idx = int(0.8 * len(X))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Reshape for LSTM
        X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
        X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))
        
        return X_train, X_test, y_train, y_test
    
    def train_random_forest(self, test_size=0.2):
        """Train Random Forest model"""
        try:
            # Split data
            split_idx = int((1 - test_size) * len(self.features))
            
            X_train = self.features.iloc[:split_idx]
            X_test = self.features.iloc[split_idx:]
            y_train = self.target.iloc[:split_idx]
            y_test = self.target.iloc[split_idx:]
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            rf_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
            
            rf_model.fit(X_train_scaled, y_train)
            
            # Make predictions
            y_pred = rf_model.predict(X_test_scaled)
            
            # Calculate metrics
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            
            self.models['random_forest'] = rf_model
            self.scalers['random_forest'] = scaler
            
            return {
                'model': rf_model,
                'mae': mae,
                'rmse': rmse,
                'r2': r2,
                'predictions': y_pred,
                'actual': y_test,
                'feature_importance': dict(zip(self.features.columns, rf_model.feature_importances_))
            }
            
        except Exception as e:
            print(f"Error training Random Forest: {e}")
            return None
    
    def train_arima(self):
        """Train ARIMA model"""
        if not HAS_STATSMODELS:
            return None
            
        try:
            # Use inflation rate data
            ts_data = self.data['inflation_rate']
            
            # Check stationarity
            adf_result = adfuller(ts_data.dropna())
            print(f"ADF Statistic: {adf_result[0]:.4f}")
            print(f"p-value: {adf_result[1]:.4f}")
            
            # Split data
            split_idx = int(0.8 * len(ts_data))
            train_data = ts_data[:split_idx]
            test_data = ts_data[split_idx:]
            
            # Fit ARIMA model - try different orders
            best_aic = float('inf')
            best_model = None
            best_order = None
            
            for p in range(0, 3):
                for d in range(0, 2):
                    for q in range(0, 3):
                        try:
                            model = ARIMA(train_data, order=(p, d, q))
                            fitted_model = model.fit()
                            if fitted_model.aic < best_aic:
                                best_aic = fitted_model.aic
                                best_model = fitted_model
                                best_order = (p, d, q)
                        except:
                            continue
            
            if best_model is None:
                print("Could not fit ARIMA model")
                return None
            
            print(f"Best ARIMA order: {best_order}, AIC: {best_aic:.2f}")
            
            # Make predictions
            forecast = best_model.forecast(steps=len(test_data))
            
            # Calculate metrics
            mae = mean_absolute_error(test_data, forecast)
            rmse = np.sqrt(mean_squared_error(test_data, forecast))
            r2 = r2_score(test_data, forecast)
            
            self.models['arima'] = best_model
            
            return {
                'model': best_model,
                'order': best_order,
                'mae': mae,
                'rmse': rmse,
                'r2': r2,
                'predictions': forecast,
                'actual': test_data,
                'aic': best_aic
            }
            
        except Exception as e:
            print(f"Error training ARIMA: {e}")
            return None
    
    def train_lstm(self):
        """Train LSTM model"""
        if not HAS_TENSORFLOW:
            return None
            
        try:
            X_train, X_test, y_train, y_test = self.prepare_lstm_data()
            
            if X_train is None:
                return None
            
            # Build LSTM model
            model = Sequential([
                LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], 1)),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(25),
                Dense(1)
            ])
            
            model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])
            
            # Train model
            early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
            
            history = model.fit(
                X_train, y_train,
                batch_size=16,
                epochs=100,
                validation_data=(X_test, y_test),
                callbacks=[early_stopping],
                verbose=0
            )
            
            # Make predictions
            y_pred = model.predict(X_test).flatten()
            
            # Calculate metrics
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            
            self.models['lstm'] = model
            
            return {
                'model': model,
                'mae': mae,
                'rmse': rmse,
                'r2': r2,
                'predictions': y_pred,
                'actual': y_test,
                'history': history
            }
            
        except Exception as e:
            print(f"Error training LSTM: {e}")
            return None
    
    def train_all_models(self):
        """Train all available models"""
        print("Training ML models for inflation prediction...")
        
        # Load and prepare data
        if not self.load_data():
            return None
        
        # Create features for tree-based models
        feature_data = self.create_features()
        
        results = {}
        
        # Train Random Forest
        print("\nTraining Random Forest...")
        rf_results = self.train_random_forest()
        if rf_results:
            results['random_forest'] = rf_results
            print(f"Random Forest - MAE: {rf_results['mae']:.3f}, RMSE: {rf_results['rmse']:.3f}, R²: {rf_results['r2']:.3f}")
        
        # Train ARIMA
        if HAS_STATSMODELS:
            print("\nTraining ARIMA...")
            arima_results = self.train_arima()
            if arima_results:
                results['arima'] = arima_results
                print(f"ARIMA{arima_results['order']} - MAE: {arima_results['mae']:.3f}, RMSE: {arima_results['rmse']:.3f}, R²: {arima_results['r2']:.3f}")
        
        # Train LSTM
        if HAS_TENSORFLOW:
            print("\nTraining LSTM...")
            lstm_results = self.train_lstm()
            if lstm_results:
                results['lstm'] = lstm_results
                print(f"LSTM - MAE: {lstm_results['mae']:.3f}, RMSE: {lstm_results['rmse']:.3f}, R²: {lstm_results['r2']:.3f}")
        
        return results
    
    def select_best_model(self, results):
        """Select best model based on performance metrics"""
        if not results:
            return None, None
        
        # Compare models by MAE (lower is better)
        best_model_name = min(results.keys(), key=lambda x: results[x]['mae'])
        best_model_results = results[best_model_name]
        
        print(f"\nBest model: {best_model_name}")
        print(f"Performance: MAE={best_model_results['mae']:.3f}, RMSE={best_model_results['rmse']:.3f}, R²={best_model_results['r2']:.3f}")
        
        return best_model_name, best_model_results
    
    def predict_future(self, best_model_name, months=3):
        """Predict inflation for next N months"""
        try:
            if best_model_name == 'random_forest':
                return self._predict_rf_future(months)
            elif best_model_name == 'arima':
                return self._predict_arima_future(months)
            elif best_model_name == 'lstm':
                return self._predict_lstm_future(months)
            else:
                return None
        except Exception as e:
            print(f"Error making future predictions: {e}")
            return None
    
    def _predict_rf_future(self, months):
        """Predict future using Random Forest"""
        model = self.models['random_forest']
        scaler = self.scalers['random_forest']
        
        # Use last available data point as starting point
        last_features = self.features.iloc[-1:].copy()
        predictions = []
        prediction_dates = []
        
        # Generate future dates
        last_date = self.data.index[-1]
        
        for i in range(months):
            # Predict next month
            scaled_features = scaler.transform(last_features)
            pred = model.predict(scaled_features)[0]
            predictions.append(pred)
            
            # Generate next date
            next_date = last_date + timedelta(days=30 * (i + 1))
            prediction_dates.append(next_date)
            
            # Update features for next prediction (simplified approach)
            # In practice, you'd need to update all lagged features properly
            if i < months - 1:
                # Create new feature row (this is a simplified version)
                new_features = last_features.copy()
                # Update some key features
                new_features.iloc[0, 0] = pred  # Update first lag
                last_features = new_features
        
        return prediction_dates, predictions
    
    def _predict_arima_future(self, months):
        """Predict future using ARIMA"""
        model = self.models['arima']
        forecast = model.forecast(steps=months)
        
        # Generate future dates
        last_date = self.data.index[-1]
        prediction_dates = [last_date + timedelta(days=30 * (i + 1)) for i in range(months)]
        
        return prediction_dates, forecast.tolist()
    
    def _predict_lstm_future(self, months):
        """Predict future using LSTM (simplified)"""
        # This is a simplified implementation
        # In practice, you'd need more sophisticated recursive prediction
        return None, []
    
    def create_prediction_visualization(self, results, best_model_name, future_dates, future_predictions):
        """Create comprehensive visualization of results and predictions"""
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Inflation Rate ML Prediction Analysis', fontsize=16, fontweight='bold')
        
        # Plot 1: Historical data and predictions
        ax1 = axes[0, 0]
        ax1.plot(self.data.index, self.data['inflation_rate'], 'b-', label='Historical', linewidth=2)
        
        if future_dates and future_predictions:
            ax1.plot(future_dates, future_predictions, 'r--', marker='o', 
                    label=f'Predicted ({best_model_name})', linewidth=2, markersize=8)
        
        ax1.set_title('Historical vs Predicted Inflation Rate')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Inflation Rate (%)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Model performance comparison
        ax2 = axes[0, 1]
        model_names = list(results.keys())
        mae_scores = [results[name]['mae'] for name in model_names]
        
        bars = ax2.bar(model_names, mae_scores, color=['blue', 'green', 'red'][:len(model_names)])
        ax2.set_title('Model Performance Comparison (MAE)')
        ax2.set_ylabel('Mean Absolute Error')
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, score in zip(bars, mae_scores):
            ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.01,
                    f'{score:.3f}', ha='center', va='bottom')
        
        # Plot 3: Feature importance (if Random Forest)
        ax3 = axes[1, 0]
        if best_model_name == 'random_forest' and 'feature_importance' in results[best_model_name]:
            importance = results[best_model_name]['feature_importance']
            # Get top 10 features
            top_features = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True)[:10])
            
            ax3.barh(list(top_features.keys()), list(top_features.values()))
            ax3.set_title('Top 10 Feature Importance (Random Forest)')
            ax3.set_xlabel('Importance')
        else:
            ax3.text(0.5, 0.5, 'Feature importance\nnot available', 
                    ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title('Feature Importance')
        
        # Plot 4: Prediction details
        ax4 = axes[1, 1]
        if future_dates and future_predictions:
            # Create a table of predictions
            pred_df = pd.DataFrame({
                'Date': [d.strftime('%Y-%m-%d') for d in future_dates],
                'Predicted Inflation (%)': [f'{p:.2f}' for p in future_predictions]
            })
            
            ax4.axis('tight')
            ax4.axis('off')
            table = ax4.table(cellText=pred_df.values, colLabels=pred_df.columns,
                             cellLoc='center', loc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1.2, 1.5)
            ax4.set_title('3-Month Inflation Predictions')
        
        plt.tight_layout()
        plt.savefig('inflation_ml_predictions.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Visualization saved as 'inflation_ml_predictions.png'")

def main():
    """Main execution function"""
    predictor = InflationPredictor()
    
    # Train all models
    results = predictor.train_all_models()
    
    if not results:
        print("No models were successfully trained.")
        return
    
    # Select best model
    best_model_name, best_results = predictor.select_best_model(results)
    
    if not best_model_name:
        print("Could not select best model.")
        return
    
    # Make future predictions
    print(f"\nGenerating 3-month predictions using {best_model_name}...")
    future_dates, future_predictions = predictor.predict_future(best_model_name, months=3)
    
    if future_dates and future_predictions:
        print("\n" + "="*60)
        print("3-MONTH INFLATION RATE PREDICTIONS")
        print("="*60)
        
        for date, pred in zip(future_dates, future_predictions):
            print(f"{date.strftime('%B %Y'):>15}: {pred:>6.2f}%")
        
        print(f"\nModel used: {best_model_name}")
        print(f"Model accuracy (MAE): {best_results['mae']:.3f}%")
        
        # Create visualization
        predictor.create_prediction_visualization(
            results, best_model_name, future_dates, future_predictions
        )
        
        # Save model for future use
        if best_model_name == 'random_forest':
            joblib.dump(predictor.models['random_forest'], 'inflation_rf_model.joblib')
            joblib.dump(predictor.scalers['random_forest'], 'inflation_rf_scaler.joblib')
            print("\nModel saved as 'inflation_rf_model.joblib'")
    
    else:
        print("Could not generate future predictions.")
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()