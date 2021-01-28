"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask, session, render_template, redirect, request
import pymysql
from hashlib import md5
app = Flask(__name__)
import os
app.secret_key = os.urandom(12)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

def create_connection():
    return pymysql.connect(host='enricoserrano.mysql.pythonanywhere-services.com',
								user='enricoserrano',
								password='13COM13COM',
								db='enricoserrano$workshopinternal',
								charset='utf8mb4',
								cursorclass=pymysql.cursors.DictCursor)


@app.route('/')
def index():
    if 'user_name' in session:
        user_name = session['user_name']
        userdetailsfirstname = session['FirstName']
        userdetailslastname = session['LastName']
        return render_template('index.html', user_name = user_name, logged_in = True, role = session["roleid"],userdetailsfirstname = userdetailsfirstname, userdetailslastname = userdetailslastname)
    return render_template('index.html')

@app.route('/admin', methods=['POST','GET'])
def admin():
    if 'logged_in' in session:
        user_data = ""
        workshop_data = ""
        userdetailsfirstname = session['FirstName']
        userdetailslastname = session['LastName']
        connection=create_connection()
        try: 
            with connection.cursor() as cursor:
                select_sql = "SELECT tblusers.UserID, tblusers.UserName, tblusers.Password, tblusers.LastName, tblusers.FirstName, tblroles.roleid, tblroles.role FROM tblroles INNER JOIN tblusers ON tblroles.roleid = tblusers.roleid WHERE tblusers.UserID != 1"
                cursor.execute(select_sql)
                user_data = cursor.fetchall()
                user_data=list(user_data)
        finally: 
                pass
        try: 
            with connection.cursor() as cursor:
                select_sql = "SELECT tblworkshop.WorkshopID, tblworkshop.School, tblsubject.SubjectID, tblworkshop.Area, tblworkshop.Time, tblsubject.Subject, tblworkshop.Teacher FROM tblsubject INNER JOIN tblworkshop ON tblsubject.SubjectID = tblworkshop.SubjectID;"
                cursor.execute(select_sql)
                workshop_data = cursor.fetchall()
                workshop_data=list(workshop_data)
        finally: 
                pass
        try: 
            with connection.cursor() as cursor:
                select_sql = "SELECT * FROM `tblsubject`"
                cursor.execute(select_sql)
                subject_data = cursor.fetchall()
                subject_data=list(subject_data)
        finally: 
                pass
        if request.method == 'POST':
            form_values = request.form 
            submitbutton = (form_values["submitbutton"])

            if submitbutton == "hiddendeleteuserbutton":
                admindeletevalue = form_values["admindeletevalue"]
                try:
                    with connection.cursor() as cursor:
                        sql = "DELETE from tblusers WHERE UserID=%s"
                        cursor.execute(sql,admindeletevalue)
                        connection.commit()
                        cursor.close()
                finally:
                    connection.close()
                    return redirect('/admin')

            if submitbutton == "hiddendeletesubjectbutton":
                workshopsubjecthiddenvalue = form_values["workshopsubjecthiddenvalue"]
                try:
                    with connection.cursor() as cursor:
                        sql = "DELETE from tblsubject WHERE SubjectID = %s"
                        cursor.execute(sql,workshopsubjecthiddenvalue)
                        connection.commit()
                        cursor.close()
                finally:
                    connection.close()
                    return redirect('/admin')
            if submitbutton == "logoutbutton":
                session.clear()
                return redirect('/login')
            if submitbutton == "changerolebutton":
                selectrole = form_values["selectrole"]
                userid = form_values["userid"]
                try:
                    with connection.cursor() as cursor:
                        sql = "UPDATE tblusers SET roleid=%s WHERE UserID=%s"
                        val=(selectrole,userid)
                        cursor.execute(sql,(val))
                        connection.commit()
                        cursor.close()
                finally:
                    connection.close()
                    return redirect('/admin')
            if submitbutton == "hiddendeletebutton":
                workshopidhiddenvalue = form_values["workshopidhiddenvalue"]
                try:
                    with connection.cursor() as cursor:
                        sql = "DELETE from tblworkshop WHERE WorkshopID = %s"
                        cursor.execute(sql,workshopidhiddenvalue)
                        connection.commit()
                        cursor.close()
                finally:
                    connection.close()
                    return redirect('/admin')

            if submitbutton == "workshopbutton":
                teachersubjectchoice = form_values["teachersubjectchoice"]
                workshoparea = form_values["workshoparea"]
                workshoptime = form_values["workshoptime"]
                workshopteacher = form_values["teachername"]
                useridlogon = session['UserID']
                try:
                    with connection.cursor() as cursor:
                        sql = "INSERT INTO `tblworkshop` (School,SubjectID,Area,Time,Teacher,UserID) VALUES (%s,%s,%s,%s,%s,%s)"
                        val=('Pakuranga College',teachersubjectchoice,workshoparea,workshoptime,workshopteacher,useridlogon)
                        cursor.execute(sql,(val))
                        connection.commit()
                        cursor.close()
                finally:
                    connection.close()
                    return redirect('/admin')

            if submitbutton == "subjectbutton":
                workshopsubject = form_values["workshopsubject"]
                try:
                    with connection.cursor() as cursor:
                        sql = "INSERT INTO `tblsubject` (Subject) VALUES (%s)"
                        val=(workshopsubject)
                        cursor.execute(sql,(val))
                        connection.commit()
                        cursor.close()
                finally:
                    connection.close()
                    return redirect('/admin')
        return render_template('admin.html', logged_in = True, role = session["roleid"], user_results = user_data, workshop_results = workshop_data, subject_results = subject_data, userdetailsfirstname = userdetailsfirstname, userdetailslastname = userdetailslastname)
    else:
        return render_template('admin.html', logged_in = False)


@app.route('/viewenroll', methods=['POST','GET'])
def viewenroll():
    if 'logged_in' in session:
        enrolled_data = ""
        connection=create_connection()
        try: 
            with connection.cursor() as cursor:
                select_sql ="SELECT tblenrollment.EnrollID, tblusers.FirstName, tblusers.LastName, tblworkshop.WorkshopID, tblworkshop.School, tblsubject.SubjectID, tblworkshop.Area, tblworkshop.Time, tblsubject.Subject, tblworkshop.Teacher FROM tblusers INNER JOIN ((tblsubject INNER JOIN tblworkshop ON tblsubject.SubjectID = tblworkshop.SubjectID) INNER JOIN tblenrollment ON tblworkshop.WorkshopID = tblenrollment.WorkshopID) ON tblusers.UserID = tblenrollment.UserID WHERE tblenrollment.WorkshopID = %s"
                cursor.execute(select_sql,session['dogshit'])
                enrolled_data = cursor.fetchall()
                enrolled_data=list(enrolled_data)
        finally:
            pass
        if request.method == 'POST':
            form_values = request.form 
            submitbutton = (form_values["submitbutton"])

            if submitbutton == "backbutton":
                return redirect('/teacher')

        return render_template('viewenrolled.html', logged_in = True, role = session["roleid"], enrolled_results = enrolled_data)
    else:
        return render_template('viewenrolled.html', logged_in = False)
@app.route('/teacher', methods=['POST','GET'])
def teacher():
    if 'logged_in' in session:
        userdetailsfirstname = session['FirstName']
        userdetailslastname = session['LastName']
        workshop_data = ""
        subject_data = ""
        allworkshop_data = ""
        enrolled_data = ""
        enrollworkshopidhiddenvalue = 0
        useridlogon = session['UserID']
        connection=create_connection()
        try: 
            with connection.cursor() as cursor:
                select_sql = "SELECT tblworkshop.WorkshopID, tblworkshop.School, tblsubject.SubjectID, tblworkshop.Area, tblworkshop.Time, tblsubject.Subject, tblworkshop.Teacher FROM tblsubject INNER JOIN tblworkshop ON tblsubject.SubjectID = tblworkshop.SubjectID WHERE tblworkshop.UserID = %s"
                cursor.execute(select_sql,useridlogon)
                workshop_data = cursor.fetchall()
                workshop_data=list(workshop_data)
        finally: 
                pass
        try: 
            with connection.cursor() as cursor:
                select_sql = "SELECT tblworkshop.WorkshopID, tblworkshop.School, tblsubject.SubjectID, tblworkshop.Area, tblworkshop.Time, tblsubject.Subject, tblworkshop.Teacher FROM tblsubject INNER JOIN tblworkshop ON tblsubject.SubjectID = tblworkshop.SubjectID WHERE tblworkshop.UserID != %s"
                cursor.execute(select_sql,useridlogon)
                allworkshop_data = cursor.fetchall()
                allworkshop_data=list(allworkshop_data)
        finally: 
                pass
        try: 
            with connection.cursor() as cursor:
                select_sql = "SELECT * FROM `tblsubject`"
                cursor.execute(select_sql)
                subject_data = cursor.fetchall()
                subject_data=list(subject_data)
        finally: 
                pass

        if request.method == 'POST':
            form_values = request.form 
            submitbutton = (form_values["submitbutton"])

            if submitbutton == "hiddendeletesubjectbutton":
                workshopsubjecthiddenvalue = form_values["workshopsubjecthiddenvalue"]
                try:
                    with connection.cursor() as cursor:
                        sql = "DELETE from tblsubject WHERE SubjectID = %s"
                        cursor.execute(sql,workshopsubjecthiddenvalue)
                        connection.commit()
                        cursor.close()
                finally:
                    connection.close()
                    return redirect('/teacher')

            if submitbutton == "logoutbutton":
                session.clear()
                return redirect('/login')
            if submitbutton == "viewenrollbutton":
                enrollworkshopidhiddenvalue = form_values["enrollworkshopidhiddenvalue"]
                session['dogshit'] = [enrollworkshopidhiddenvalue]
                print(session['dogshit'])
                return redirect('/viewenroll')

            if submitbutton == "hiddendeletebutton":
                workshopidhiddenvalue = form_values["workshopidhiddenvalue"]
                try:
                    with connection.cursor() as cursor:
                        sql = "DELETE from tblworkshop WHERE WorkshopID = %s"
                        cursor.execute(sql,workshopidhiddenvalue)
                        connection.commit()
                        cursor.close()
                finally:
                    connection.close()
                    return redirect('/teacher')
            if submitbutton == "workshopbutton":
                teachersubjectchoice = form_values["teachersubjectchoice"]
                workshoparea = form_values["workshoparea"]
                workshoptime = form_values["workshoptime"]
                workshopteacher = form_values["teachername"]
                useridlogon = session['UserID']
                try:
                    with connection.cursor() as cursor:
                        sql = "INSERT INTO `tblworkshop` (School,SubjectID,Area,Time,Teacher,UserID) VALUES (%s,%s,%s,%s,%s,%s)"
                        val=('Pakuranga College',teachersubjectchoice,workshoparea,workshoptime,workshopteacher,useridlogon)
                        cursor.execute(sql,(val))
                        connection.commit()
                        cursor.close()
                finally:
                    connection.close()
                    return redirect('/teacher')

            if submitbutton == "subjectbutton":
                workshopsubject = form_values["workshopsubject"]
                try:
                    with connection.cursor() as cursor:
                        sql = "INSERT INTO `tblsubject` (Subject) VALUES (%s)"
                        val=(workshopsubject)
                        cursor.execute(sql,(val))
                        connection.commit()
                        cursor.close()
                finally:
                    connection.close()
                    return redirect('/teacher')
            

        return render_template('teacher.html', logged_in = True, role = session["roleid"], workshop_results = workshop_data, subject_results = subject_data, allworkshop_results = allworkshop_data, enrolled_results = enrolled_data, userdetailsfirstname = userdetailsfirstname, userdetailslastname = userdetailslastname)
    else:
        return render_template('teacher.html', logged_in = False)

@app.route('/student', methods=['POST','GET'])
def student():
    if 'logged_in' in session:
        print("Logged in")
        userdetailsfirstname = session['FirstName']
        userdetailslastname = session['LastName']
        workshop_data = ""
        enrollment_data = ""
        useridlogon = ""
        connection=create_connection()
        useridlogon = session['UserID']
        try: 
            with connection.cursor() as cursor:
                select_sql = "SELECT tblworkshop.WorkshopID, tblworkshop.School, tblsubject.SubjectID, tblworkshop.Area, tblworkshop.Time, tblsubject.Subject, tblworkshop.Teacher FROM tblsubject INNER JOIN tblworkshop ON tblsubject.SubjectID = tblworkshop.SubjectID;"
                cursor.execute(select_sql)
                workshop_data = cursor.fetchall()
                workshop_data=list(workshop_data)
        finally: 
                pass
        try: 
            with connection.cursor() as cursor:
                select_sql ="SELECT tblenrollment.EnrollID, tblenrollment.UserID UserID, tblusers.FirstName, tblusers.LastName, tblworkshop.WorkshopID, tblworkshop.School, tblsubject.SubjectID, tblworkshop.Area, tblworkshop.Time, tblsubject.Subject, tblworkshop.Teacher FROM tblusers INNER JOIN ((tblsubject INNER JOIN tblworkshop ON tblsubject.SubjectID = tblworkshop.SubjectID) INNER JOIN tblenrollment ON tblworkshop.WorkshopID = tblenrollment.WorkshopID) ON tblusers.UserID = tblenrollment.UserID WHERE tblenrollment.UserID = %s"
                cursor.execute(select_sql,useridlogon)
                enrollment_data = cursor.fetchall()
                enrollment_data=list(enrollment_data)
        finally: 
                pass
        if request.method == 'POST':
            form_values = request.form 
            submitbutton = (form_values["submitbutton"])
            if submitbutton == "logoutbutton":
                session.clear()
                return redirect('/login')

            if submitbutton == "hiddenunenrollbutton":
                enrollid = form_values["enrollid"]
                try:
                    with connection.cursor() as cursor:
                        sql = "DELETE from tblenrollment WHERE EnrollID = %s"
                        cursor.execute(sql,enrollid)
                        connection.commit()
                        cursor.close()
                finally:
                    connection.close()
                    return redirect('/student')

            if submitbutton == "hiddenenrollbutton":
                workshopid = form_values["workshopid"]
                try:
                    with connection.cursor() as cursor:
                        sql = "INSERT INTO `tblenrollment` (UserID,WorkshopID) VALUES (%s,%s)"
                        val=(useridlogon,workshopid)
                        cursor.execute(sql,(val))
                        connection.commit()
                        cursor.close()
                finally:
                    connection.close()
                    print(useridlogon)
                    return redirect('/student')
         
            print(useridlogon)
        return render_template('student.html', logged_in = True, role = session["roleid"], workshop_results = workshop_data, useridlogon = useridlogon, enrollment_results = enrollment_data, userdetailsfirstname = userdetailsfirstname, userdetailslastname = userdetailslastname)
    else:
        
        return render_template('student.html', logged_in = False)



@app.route('/login', methods =['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form['user_name']
        password = request.form['password']
        password = md5(password.encode()).hexdigest()
        connection = create_connection()
        with connection.cursor() as cursor:
                sql = "SELECT * FROM tblusers WHERE UserName = %s AND password = %s"
                val=(user_name, password)
                cursor.execute(sql,(val))
                user_details = cursor.fetchall()
                connection.close()
                if len(user_details) == 0:
                    return render_template("login.html")
                else:
                    session['user_name'] = user_name
                    session['logged_in'] = True
                    session['UserID'] = user_details[0]["UserID"]
                    session['FirstName'] = user_details[0]["FirstName"]
                    session['LastName'] = user_details[0]["LastName"]
                    print(user_details[0]["UserID"])
                    print(session['UserID'])                    
                    session["roleid"] = user_details[0]["roleid"]

                    return redirect('/')
    return render_template('login.html')

@app.route('/signup',  methods =['GET', 'POST'])
def signup():
    data = ""
    connection=create_connection()
    if request.method == 'POST':
        form_values = request.form 
        firstname = form_values["firstname"]
        lastname = form_values["lastname"]
        username = form_values["username"]
        password = form_values["password"]
        password = md5(password.encode()).hexdigest()
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO `tblusers` (FirstName,Lastname,UserName,Password,roleid) VALUES (%s,%s,%s,%s,%s) "
                val=(firstname,lastname,username,password,'3')
                cursor.execute(sql,(val))
                connection.commit()
                cursor.close()
        finally:
            return render_template('signup.html', signed_in = True)
    return render_template('signup.html')

if __name__ == '__main__':
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
