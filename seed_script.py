import sqlite3

def setup_database():
    # 1. Connect to the database (creates 'ecommerce.db' file in your folder)
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()

    # 2. Create Tables
    print("Creating tables...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            signup_date DATE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_name TEXT,
            amount DECIMAL(10,2),
            order_date TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
    ''')

    # 3. Add Dummy Records
    print("Inserting dummy data...")
    
    # Inserting Users
    users = [
        ('Alice Smith', 'alice@example.com', '2023-01-15'),
        ('Bob Jones', 'bob@example.com', '2023-03-22'),
        ('Charlie Brown', 'charlie@example.com', '2023-05-10')
    ]
    cursor.executemany('INSERT OR IGNORE INTO Users (name, email, signup_date) VALUES (?, ?, ?)', users)

    # Inserting Orders
    orders = [
        (1, 'Laptop', 1200.00, '2023-05-01 10:00:00'),
        (1, 'Mouse', 25.50, '2023-05-05 14:30:00'),
        (2, 'Monitor', 300.00, '2023-06-10 09:15:00'),
        (3, 'Keyboard', 75.00, '2023-07-01 11:00:00'),
        (2, 'Desk Lamp', 45.00, '2023-07-05 16:45:00')
    ]
    cursor.executemany('INSERT INTO Orders (user_id, product_name, amount, order_date) VALUES (?, ?, ?, ?)', orders)

    # 4. Commit and Close
    conn.commit()
    conn.close()
    print("Database setup complete! 'ecommerce.db' is ready.")

if __name__ == "__main__":
    setup_database()