import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
enrollment TEXT,
department TEXT,
year TEXT,
username TEXT,
password TEXT,
role TEXT
)
""")

conn.commit()
conn.close()

print("Students Table Added Successfully")