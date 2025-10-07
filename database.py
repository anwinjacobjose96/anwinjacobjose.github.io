import sqlite3
from datetime import datetime, timedelta

def get_db_connection():
    conn = sqlite3.connect('period_tracker.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # Users table (only one user allowed)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Periods table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS periods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                    (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        # User already exists
        pass
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ? AND password = ?',
        (username, password)
    ).fetchone()
    conn.close()
    return user

def add_period(user_id, start_date):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO periods (user_id, start_date) VALUES (?, ?)',
        (user_id, start_date)
    )
    conn.commit()
    conn.close()

def get_periods(user_id):
    conn = get_db_connection()
    periods = conn.execute(
        'SELECT * FROM periods WHERE user_id = ? ORDER BY start_date DESC',
        (user_id,)
    ).fetchall()
    conn.close()
    return periods

def get_cycle_stats(user_id):
    conn = get_db_connection()
    periods = conn.execute(
        'SELECT start_date FROM periods WHERE user_id = ? ORDER BY start_date',
        (user_id,)
    ).fetchall()
    conn.close()
    
    if len(periods) < 2:
        return {
            'avg_cycle_length': None,
            'next_period': None,
            'last_period': periods[0]['start_date'] if periods else None
        }
    
    # Calculate average cycle length
    cycle_lengths = []
    for i in range(1, len(periods)):
        prev_date = datetime.strptime(periods[i-1]['start_date'], '%Y-%m-%d')
        curr_date = datetime.strptime(periods[i]['start_date'], '%Y-%m-%d')
        cycle_length = (curr_date - prev_date).days
        cycle_lengths.append(cycle_length)
    
    avg_cycle_length = sum(cycle_lengths) // len(cycle_lengths)
    
    # Calculate next expected period using the LAST period in the list
    last_period = datetime.strptime(periods[-1]['start_date'], '%Y-%m-%d')
    next_period = last_period + timedelta(days=avg_cycle_length)
    
    return {
        'avg_cycle_length': avg_cycle_length,
        'next_period': next_period.strftime('%Y-%m-%d'),
        'last_period': periods[-1]['start_date']
    }

def clear_periods(user_id):
    conn = get_db_connection()
    conn.execute(
        'DELETE FROM periods WHERE user_id = ?',
        (user_id,)
    )
    conn.commit()
    conn.close()
