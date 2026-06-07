from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
import os
from datetime import datetime
import csv

app = Flask(__name__)
app.secret_key = "attendance_system"


# ---------------- LOGIN ----------------

@app.route('/')
def login():
    return render_template('login.html')
# ---------------- REGISTER PAGE OPEN ----------------

@app.route('/register_page')
def register_page():
    return render_template('register.html')
# ---------------- REGISTER SAVE ----------------
@app.route('/login', methods=['POST'])
def do_login():

    username = request.form['username'].lower()
    password = request.form['password']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id,name,role FROM users
    WHERE LOWER(username)=? AND password=?
    """,(username,password))

    user = cursor.fetchone()

    if user is None:
        return "Invalid Username or Password!"

    session['id'] = user[0]     # ✅ ID STORE KARO
    session['user'] = user[1]
    session['role'] = user[2]

    if session['role']=="student":
        return redirect('/student')

    elif session['role']=="teacher":
        return redirect('/teacher')

    elif session['role']=="principal":
        return redirect('/principal')
@app.route('/register', methods=['POST'])
def register():

    name = request.form['name']
    enroll = request.form['enrollment']
    dept = request.form['department']
    year = request.form['year']
    username = request.form['username'].lower()
    password = request.form['password']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO users(name,enrollment,department,year,username,password,role)
    VALUES(?,?,?,?,?,?,?)
    """,(name,enroll,dept,year,username,password,"student"))

    conn.commit()
    conn.close()

    # ---------- DATASET FOLDER AUTO CREATE ----------
    path = "dataset/" + name.lower()
    if not os.path.exists(path):
        os.makedirs(path)

    # ---------- CAMERA AUTO START ----------
    os.system(f'python capture.py {name.lower()}')
    os.system("python train.py")

    return redirect('/')
# ---------------- STUDENT DASHBOARD ----------------

@app.route('/student')
def student():

    if 'user' not in session:
        return redirect('/')

    username = session['user'] # Username ko lowercase mein access karenge

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT date,time FROM attendance WHERE name=?", (username,))
    data = cursor.fetchall()

    present = len(data)
    total = 30

    percent = 0
    if total != 0:
        percent = round((present/total)*100,2)

    return render_template('student_dashboard.html',
                           data=data,
                           total=total,
                           present=present,
                           percent=percent,
                           name=username)
@app.route('/profile')
def profile():

    if 'id' not in session:
        return redirect('/')

    uid = session['id']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("""
    SELECT name,enrollment,department,year,username,image
    FROM users WHERE id=?
    """,(uid,))

    profile = cursor.fetchone()

    return render_template("student_profile.html",profile=profile)


@app.route('/update_profile',methods=['POST'])
def update_profile():

    uid = session['id']

    name = request.form['name']
    dept = request.form['department']
    year = request.form['year']
    password = request.form['password']

    file = request.files['image']

    img_name = ""

    if file.filename != "":
        img_name = file.filename
        file.save("static/profile/"+img_name)

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE users SET name=?,department=?,year=?,password=?,image=?
        WHERE id=?
        """,(name,dept,year,password,img_name,uid))

    else:

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE users SET name=?,department=?,year=?,password=?
        WHERE id=?
        """,(name,dept,year,password,uid))

    conn.commit()
    conn.close()

    return redirect('/profile')
# ---------------- TEACHER DASHBOARD ----------------
@app.route('/teacher')
def teacher():

    if 'user' not in session:
        return redirect('/')

    if session['role'] != "teacher":
        return "Unauthorized"

    students = os.listdir('dataset')
    total_students = len(students)

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("SELECT name FROM attendance WHERE date=?", (today,))
    data = cursor.fetchall()

    present_list = [i[0].lower() for i in data]
    absent_list = [s.lower() for s in students if s.lower() not in present_list]

    present_count = len(present_list)
    absent_count = len(absent_list)

    if total_students == 0:
        percent = 0
    else:
        percent = int((present_count/total_students)*100)

    return render_template("teacher_dashboard.html",
                           total=total_students,
                           present=present_count,
                           absent=absent_count,
                           percent=percent,
                           plist=present_list,
                           alist=absent_list)

@app.route('/manual_mark/<name>')
def manual_mark(name):

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")

    cursor.execute("SELECT * FROM attendance WHERE name=? AND date=?", (name,today))
    data = cursor.fetchone()

    if data is None:
        cursor.execute("INSERT INTO attendance(name,date,time) VALUES(?,?,?)",(name,today,time))
        conn.commit()

    return redirect('/teacher')

@app.route('/delete/<name>')
def delete(name):

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("DELETE FROM attendance WHERE name=? AND date=?",(name,today))
    conn.commit()

    return redirect('/teacher')

@app.route('/export_today')
def export_today():

    today = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM attendance WHERE date=?", (today,))
    data = cursor.fetchall()

    with open('today_attendance.csv','w',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID','Name','Date','Time'])
        writer.writerows(data)

    return send_file('today_attendance.csv',as_attachment=True)


@app.route('/date_filter', methods=['POST'])
def date_filter():

    if 'user' not in session:
        return redirect('/')

    selected_date = request.form['date']

    students = os.listdir('dataset')
    total = len(students)

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM attendance WHERE date=?", (selected_date,))
    data = cursor.fetchall()

    present = [i[0].lower() for i in data]
    absent = [s.lower() for s in students if s.lower() not in present]

    present_count = len(present)
    absent_count = len(absent)

    percent = 0
    if total != 0:
        percent = int((present_count/total)*100)

    return render_template("teacher_dashboard.html",
                           total=total,
                           present=present_count,
                           absent=absent_count,
                           percent=percent,
                           plist=present,
                           alist=absent)
# ---------------- PRINCIPAL DASHBOARD ----------------
@app.route('/principal')
def principal():

    if 'role' not in session or session['role']!='principal':
        return redirect('/')

    conn=sqlite3.connect('database.db')
    cursor=conn.cursor()

    today=datetime.now().strftime("%Y-%m-%d")

    # ALL STUDENTS
    cursor.execute("""
    SELECT name,enrollment,department,year
    FROM users WHERE role='student'
    """)
    students=cursor.fetchall()

    total_students=len(students)

    # PRESENT TODAY
    cursor.execute("""
    SELECT name FROM attendance WHERE date=?
    """,(today,))
    data=cursor.fetchall()

    present_list=[i[0] for i in data]
    absent_list=[s[0] for s in students if s[0] not in present_list]

    present_students=len(present_list)
    absent_students=len(absent_list)

    percent=int((present_students/total_students)*100) if total_students!=0 else 0

    return render_template('principal_dashboard.html',
    students=students,
    total_students=total_students,
    present_students=present_students,
    absent_students=absent_students,
    percent=percent,
    plist=present_list,
    alist=absent_list)
@app.route('/delete_student/<enroll>')
def delete_student(enroll):

    conn=sqlite3.connect('database.db')
    cursor=conn.cursor()

    cursor.execute("DELETE FROM users WHERE enrollment=?",(enroll,))
    conn.commit()
    conn.close()

    return redirect('/principal')

@app.route('/system_reset')
def system_reset():

    if 'role' not in session or session['role'] != 'principal':
        return redirect('/')

    # ================= DELETE DATABASE DATA =================
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE role='student'")
    cursor.execute("DELETE FROM attendance")

    conn.commit()
    conn.close()

    # ================= DELETE DATASET FOLDERS =================
    dataset_path = "dataset"

    if os.path.exists(dataset_path):
        for folder in os.listdir(dataset_path):
            folder_path = os.path.join(dataset_path, folder)
            if os.path.isdir(folder_path):
                for file in os.listdir(folder_path):
                    os.remove(os.path.join(folder_path, file))
                os.rmdir(folder_path)

    # ================= DELETE TRAINER FILE =================
    trainer_file = "trainer/trainer.yml"
    if os.path.exists(trainer_file):
        os.remove(trainer_file)

    # ================= DELETE CSV FILES =================
    if os.path.exists("attendance.csv"):
        os.remove("attendance.csv")

    if os.path.exists("today_attendance.csv"):
        os.remove("today_attendance.csv")

    print("🔥 SYSTEM FULLY RESET DONE")

    return redirect('/principal')

@app.route('/add_student', methods=['POST'])
def add_student():

    name=request.form['name']
    enroll=request.form['enrollment']
    dept=request.form['department']
    year=request.form['year']
    username=request.form['username'].lower()
    password=request.form['password']

    conn=sqlite3.connect('database.db')
    cursor=conn.cursor()

    cursor.execute("""
    INSERT INTO users(name,enrollment,department,year,username,password,role)
    VALUES(?,?,?,?,?,?,?)
    """,(name,enroll,dept,year,username,password,"student"))

    conn.commit()
    conn.close()

    return redirect('/principal')

@app.route('/edit_student/<enroll>')
def edit_student(enroll):

    if 'role' not in session or session['role']!='principal':
        return redirect('/')

    conn=sqlite3.connect('database.db')
    cursor=conn.cursor()

    cursor.execute("""
    SELECT name,enrollment,department,year
    FROM users WHERE enrollment=?
    """,(enroll,))

    student=cursor.fetchone()

    return render_template('edit_student.html',student=student)

@app.route('/update_student',methods=['POST'])
def update_student():

    name=request.form['name']
    enroll=request.form['enrollment']
    dept=request.form['department']
    year=request.form['year']

    conn=sqlite3.connect('database.db')
    cursor=conn.cursor()

    cursor.execute("""
    UPDATE users
    SET name=?,department=?,year=?
    WHERE enrollment=?
    """,(name,dept,year,enroll))

    conn.commit()
    conn.close()

    return redirect('/principal')

@app.route('/principal_date_filter', methods=['POST'])
def principal_date_filter():

    selected_date = request.form['date']

    conn=sqlite3.connect('database.db')
    cursor=conn.cursor()

    cursor.execute("""
    SELECT COUNT(DISTINCT name)
    FROM attendance WHERE date=?
    """,(selected_date,))
    
    present_students=cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM users WHERE role='student'
    """)
    
    total_students=cursor.fetchone()[0]

    absent_students=total_students-present_students

    percent=int((present_students/total_students)*100) if total_students!=0 else 0

    cursor.execute("""
    SELECT name,enrollment,department,year
    FROM users WHERE role='student'
    """)
    
    students=cursor.fetchall()

    return render_template('principal_dashboard.html',
    students=students,
    total_students=total_students,
    present_students=present_students,
    absent_students=absent_students,
    percent=percent)
# ---------------- DOWNLOAD ----------------

@app.route('/download')
def download():

    username = session['user'].lower()  # Username ko lowercase mein access karenge

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT date,time FROM attendance WHERE name=?", (username,))
    data = cursor.fetchall()

    with open('attendance.csv','w',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Date','Time'])
        writer.writerows(data)

    return send_file('attendance.csv', as_attachment=True)

@app.route('/start_attendance')
def start_attendance():

    if 'role' not in session:
        return redirect('/')

    if session['role'] != "teacher":
        return "Unauthorized Access"

    import os
    os.system("python recognize.py")

    return redirect('/teacher')

# ---------------- LOGOUT ----------------

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


app.run(debug=True)