import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# STUDENT
cursor.execute("INSERT INTO users(username,password,role) VALUES('arjun','1234','student')")

# TEACHER
cursor.execute("INSERT INTO users(username,password,role) VALUES('teacher','1234','teacher')")

# PRINCIPAL
cursor.execute("INSERT INTO users(username,password,role) VALUES('principal','1234','principal')")

conn.commit()
conn.close()

print("Users Inserted Successfully")