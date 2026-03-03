import sqlite3

conn = sqlite3.connect("practice.db")
conn.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        table_name TEXT NOT NULL,
        row_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()
conn.close()
print(" Таблица audit_logs создана напрямую в БД (не через модели)")
 