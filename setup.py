
#!/usr/bin/env python
import os
import json
import sqlite3
import shutil
import sys

def create_directories():
    """Create necessary directories for the project"""
    print("Creating data directories...")
    
    # Create data directory
    data_dir = os.path.join("data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Create vector store directory
    vector_store_dir = os.path.join("data", "vector_store")
    os.makedirs(vector_store_dir, exist_ok=True)
    
    print("Directories created successfully.")

def create_sample_database():
    """Create a sample SQLite database for testing"""
    print("Creating sample database...")
    
    # Connect to the sample database
    db_path = os.path.join("data", "example.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create sales table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY,
        date TEXT,
        product_id INTEGER,
        region TEXT,
        amount REAL
    )
    """)
    
    # Create products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        category TEXT,
        price REAL
    )
    """)
    
    # Insert sample products
    sample_products = [
        (1, "Laptop", "Electronics", 1299.99),
        (2, "Smartphone", "Electronics", 899.99),
        (3, "Headphones", "Electronics", 199.99),
        (4, "Office Chair", "Furniture", 249.99),
        (5, "Desk", "Furniture", 349.99),
        (6, "Coffee Maker", "Appliances", 79.99),
        (7, "Blender", "Appliances", 49.99),
        (8, "Monitor", "Electronics", 399.99),
        (9, "Keyboard", "Electronics", 129.99),
        (10, "Mouse", "Electronics", 59.99)
    ]
    
    cursor.executemany(
        "INSERT OR REPLACE INTO products (id, name, category, price) VALUES (?, ?, ?, ?)",
        sample_products
    )
    
    # Insert sample sales
    # Only insert if the table is empty
    cursor.execute("SELECT COUNT(*) FROM sales")
    if cursor.fetchone()[0] == 0:
        import random
        from datetime import datetime, timedelta
        
        regions = ["North", "South", "East", "West", "Central"]
        sales = []
        
        # Generate 1000 sample sales records
        start_date = datetime(2023, 1, 1)
        for i in range(1, 1001):
            date = start_date + timedelta(days=random.randint(0, 364))
            product_id = random.randint(1, 10)
            region = random.choice(regions)
            amount = round(random.uniform(1, 5) * sample_products[product_id-1][3], 2)
            
            sales.append((i, date.strftime("%Y-%m-%d"), product_id, region, amount))
        
        cursor.executemany(
            "INSERT OR REPLACE INTO sales (id, date, product_id, region, amount) VALUES (?, ?, ?, ?, ?)",
            sales
        )
    
    conn.commit()
    conn.close()
    
    print(f"Sample database created at {db_path}")

def clean_up():
    """Clean up any temporary files or directories"""
    print("Cleaning up...")
    
    # Clean up any temporary files
    temp_files = [
        # Add any temporary files here that should be removed
    ]
    
    for file_path in temp_files:
        if os.path.exists(file_path):
            os.remove(file_path)
    
    print("Clean up completed.")

def main():
    """Main setup function"""
    print("Setting up Data Memory System...")
    
    # Create necessary directories
    create_directories()
    
    # Create sample database
    create_sample_database()
    
    # Clean up
    clean_up()
    
    print("Setup completed successfully!")
    print("\nTo run the application:")
    print("1. Start the interactive console:")
    print("   python app/main.py --interactive")
    print("\n2. Or use the Gradio UI:")
    print("   python app/ui/gradio_app.py")

if __name__ == "__main__":
    main()
