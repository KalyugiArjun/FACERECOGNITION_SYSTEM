import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# ----------- TEACHER ------------
cursor.execute("""
INSERT INTO users(name,enrollment,department,year,username,password,role)
VALUES(?,?,?,?,?,?,?)
""",("Manoj Kumar","T001","CSE","Staff","teacher","1234","teacher"))

# ----------- PRINCIPAL ----------
cursor.execute("""
INSERT INTO users(name,enrollment,department,year,username,password,role)
VALUES(?,?,?,?,?,?,?)
""",("Admin","P001","Management","Staff","admin","1234","principal"))

conn.commit()
conn.close()

print("Teacher & Principal Added Successfully!")