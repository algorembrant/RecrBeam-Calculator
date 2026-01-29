import sqlite3
import json
from datetime import datetime

DB_NAME = "beam_calc.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            inputs TEXT,
            results TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_calculation(inputs: dict, results: dict):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('INSERT INTO calculations (timestamp, inputs, results) VALUES (?, ?, ?)',
              (timestamp, json.dumps(inputs), json.dumps(results)))
    conn.commit()
    conn.close()

def get_history(limit=10):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id, timestamp, inputs, results FROM calculations ORDER BY id DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            'id': row[0],
            'timestamp': row[1],
            'inputs': json.loads(row[2]),
            'results': json.loads(row[3])
        })
    return history
