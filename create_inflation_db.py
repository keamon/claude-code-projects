import sqlite3
import pandas as pd
import os

def create_inflation_database():
    """Create SQLite database from CPI inflation CSV data"""
    
    # Check if CSV file exists
    csv_file = 'cpi_inflation_data.csv'
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found. Please run fetch_inflation_data.py first.")
        return False
    
    # Database file name
    db_file = 'inflation_data.db'
    
    try:
        # Read CSV data
        print(f"Reading data from {csv_file}...")
        df = pd.read_csv(csv_file)
        
        # Display data info
        print(f"Loaded {len(df)} records")
        print(f"Columns: {list(df.columns)}")
        print(f"Date range: {df['date'].min()} to {df['date'].max()}")
        
        # Connect to SQLite database (creates if doesn't exist)
        print(f"\nCreating SQLite database: {db_file}")
        conn = sqlite3.connect(db_file)
        
        # Create table and insert data
        df.to_sql('cpi_data', conn, if_exists='replace', index=False)
        
        # Create indexes for better query performance
        cursor = conn.cursor()
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON cpi_data(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_value ON cpi_data(value)')
        
        # Verify the data was inserted
        cursor.execute('SELECT COUNT(*) FROM cpi_data')
        count = cursor.fetchone()[0]
        print(f"Successfully inserted {count} records into cpi_data table")
        
        # Show table schema
        cursor.execute('PRAGMA table_info(cpi_data)')
        schema = cursor.fetchall()
        print("\nTable schema:")
        for col in schema:
            print(f"  {col[1]} ({col[2]})")
        
        # Show sample data
        print("\nSample data (first 5 rows):")
        cursor.execute('SELECT * FROM cpi_data ORDER BY date LIMIT 5')
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute('PRAGMA table_info(cpi_data)')
        columns = [col[1] for col in cursor.fetchall()]
        
        # Print header
        print(" | ".join(f"{col:>12}" for col in columns))
        print("-" * (len(columns) * 15))
        
        # Print data rows
        for row in rows:
            formatted_row = []
            for i, val in enumerate(row):
                if columns[i] == 'date':
                    formatted_row.append(f"{str(val)[:10]:>12}")
                elif isinstance(val, float):
                    formatted_row.append(f"{val:>12.2f}")
                else:
                    formatted_row.append(f"{str(val):>12}")
            print(" | ".join(formatted_row))
        
        # Show latest inflation data
        print("\nLatest inflation data:")
        cursor.execute('''
            SELECT date, value, inflation_rate 
            FROM cpi_data 
            WHERE inflation_rate IS NOT NULL 
            ORDER BY date DESC 
            LIMIT 5
        ''')
        recent_data = cursor.fetchall()
        
        print(f"{'Date':>12} | {'CPI':>8} | {'Inflation %':>12}")
        print("-" * 40)
        for row in recent_data:
            date_str = str(row[0])[:10]
            print(f"{date_str:>12} | {row[1]:>8.2f} | {row[2]:>12.2f}")
        
        conn.close()
        print(f"\nDatabase created successfully: {db_file}")
        return True
        
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def query_examples():
    """Show example queries for the inflation database"""
    
    print("\n" + "="*50)
    print("EXAMPLE SQL QUERIES")
    print("="*50)
    
    examples = [
        ("Get latest inflation rate", 
         "SELECT date, inflation_rate FROM cpi_data WHERE inflation_rate IS NOT NULL ORDER BY date DESC LIMIT 1;"),
        
        ("Get highest inflation in dataset", 
         "SELECT date, inflation_rate FROM cpi_data WHERE inflation_rate = (SELECT MAX(inflation_rate) FROM cpi_data);"),
        
        ("Get average inflation over time periods", 
         "SELECT strftime('%Y', date) as year, ROUND(AVG(inflation_rate), 2) as avg_inflation FROM cpi_data WHERE inflation_rate IS NOT NULL GROUP BY strftime('%Y', date);"),
        
        ("Get all data for specific year", 
         "SELECT * FROM cpi_data WHERE strftime('%Y', date) = '2024';"),
        
        ("Get inflation trend (last 6 months)", 
         "SELECT date, inflation_rate FROM cpi_data WHERE inflation_rate IS NOT NULL ORDER BY date DESC LIMIT 6;")
    ]
    
    for desc, query in examples:
        print(f"\n{desc}:")
        print(f"  {query}")

if __name__ == "__main__":
    success = create_inflation_database()
    if success:
        query_examples()
        print(f"\nTo query the database:")
        print(f"  sqlite3 inflation_data.db")
        print(f"Or use Python with sqlite3 module")