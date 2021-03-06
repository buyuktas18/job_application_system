from flask import Flask, render_template, request, url_for, redirect, send_file, session
from datetime import date
from flask import json
from io import BytesIO
import os
import psycopg2

data = 0


DATABASE_URL = os.environ['DATABASE_URL']

mydb = psycopg2.connect(DATABASE_URL, sslmode='require')

print(mydb)
app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

@app.route("/", methods=['GET', 'POST'])
def home_page():
    global data
    mycursor = mydb.cursor()

    mycursor.execute("SELECT companies.name, title, announcement_id FROM announcements JOIN companies ON announcements.company_id = companies.company_id")
    myresult = mycursor.fetchall()
    mycursor.execute("SELECT name, score FROM companies ORDER BY SCORE DESC")
    
    scores = mycursor.fetchall()
    return render_template("home.html", data = myresult, scores= scores)

@app.route("/confirm", methods=['GET', 'POST'])
def confirm_page():
    global data
    mycursor = mydb.cursor()
    check = 0
    sql = "SELECT announcement_id FROM job_applications WHERE applicant_id = %s"
    val = (session['username'], )
    mycursor.execute(sql, val)
    checking = mycursor.fetchall()
    
    for i in range(0, len(checking)):
        print(checking[i][0])

        if str(checking[i][0]) == request.form['apply']:
            
            check = 1
    if check == 0:
        sql = "INSERT INTO job_applications(applicant_id, announcement_id, status) VALUES (%s, %s, %s)"
        val = (session['username'], request.form['apply'], "WAITING")
        mycursor.execute(sql, val)  
        mydb.commit()
        return render_template("confirm.html", message="Your application has been accepted")
    else:
        return render_template("confirm.html", message="You have already applied for this position")

@app.route("/announcements", methods=['GET', 'POST'])
def ans_page():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * from companies")
    options = mycursor.fetchall()
    print(options)
    if request.method == "GET":
        mycursor = mydb.cursor()
        mycursor.execute("SELECT companies.name, title, announcement_id FROM announcements JOIN companies ON announcements.company_id = companies.company_id")
        myresult = mycursor.fetchall()
        mycursor.execute("SELECT name, score FROM companies ORDER BY SCORE DESC")
        
        scores = mycursor.fetchall()
        return render_template("announcements.html", data = myresult, scores= scores, options = options)
    else:
        if request.form.get("searchb"):
            title = request.form['search']
            mycursor = mydb.cursor()
            sql = "SELECT companies.name, title, announcement_id FROM announcements JOIN companies ON announcements.company_id = companies.company_id WHERE title = %s"
            val = (title, )
            mycursor.execute(sql, val)
            myresult = mycursor.fetchall()
            mycursor.execute("SELECT name, score FROM companies ORDER BY SCORE DESC")
            scores = mycursor.fetchall()
            return render_template("announcements.html", data = myresult, scores= scores, options = options)
        else:
            return confirm_page()

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    global data
    data = 0
    return home_page()


@app.route("/job_page", methods=['GET', 'POST'])
def job_page():
    global data
    if request.method == "GET":
        return render_template("job_page.html", var=session['username'])
    else:
        form_title = request.form["title"]
        deadline = request.form["deadline"]
        salary = request.form["salary"]
        working_day = request.form["workday"]
        if working_day.isdigit() == False:
            return render_template("job_page.html", error_message = "working day should be integer")
        if int(working_day) > 7:
            return render_template("job_page.html", error_message = "working day should be <= 7")
        if salary.isdigit() == False:
            return render_template("job_page.html", error_message = "salary should be integer")
        

        mycursor = mydb.cursor()
        sql = "INSERT INTO announcements(title, company_id, initial_date, deadline, working_day, salary) VALUES (%s, %s,%s,%s, %s,%s)"
        val = (form_title,session['username'] , date.today(), deadline, working_day, salary)
        mycursor.execute(sql, val)
        mydb.commit()
        sql = "UPDATE companies SET score = score+10 WHERE company_id = %s"
        val = (session['username'], )
        mycursor.execute(sql, val)
        mydb.commit()

        return cprofile_page()


@app.route("/announcement" ,methods=['GET', 'POST'])
def annons_page():
    form_title = request.args.get('ann')
    mycursor = mydb.cursor()
    sql = "SELECT announcements.*, name, description FROM announcements JOIN companies ON announcements.company_id = companies.company_id WHERE announcement_id =%s"
    val = (form_title, )
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    return render_template("announcement.html", title = myresult)

@app.route("/login" ,methods=['GET', 'POST'])
def login_page():
    global data
    if request.method == "GET":
        return render_template("login.html")
    else:
        mycursor = mydb.cursor()
        
        
        if request.form.get("signin"):
            new_username = request.form["usernamenew"]
            new_password = request.form["passwordnew"]
            desc = request.form["desc"]
            cname = request.form["cname"]
            mail = request.form["mail"]
            phone = request.form["phone"]
            sql = "INSERT INTO users(username, password, membership) VALUES (%s, %s,%s)"
            val = (new_username, new_password, "C")
            mycursor.execute(sql, val)
            mydb.commit()
            sql = "SELECT user_id FROM users WHERE username=%s"
            val = (new_username,)
            mycursor.execute(sql, val)
            myresult = mycursor.fetchall()
            sql = "INSERT INTO companies(name, score, email, phone, membership_date, user_id, description) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (cname, 0, mail, phone, date.today(), myresult[0][0], desc)
            mycursor.execute(sql, val)
            mydb.commit()
            sql2 = "SELECT company_id FROM companies WHERE user_id=%s"
            val2 = (myresult[0][0], )
            mycursor.execute(sql2, val2)
            company = mycursor.fetchall()
            session['username'] = company[0][0]
            return cprofile_page()
        else:
            form_username = request.form["username"]
            password = request.form["password"]
            sql = "SELECT password, user_id FROM users WHERE username=%s"
            val = (form_username,)
            mycursor.execute(sql, val)
            myresult = mycursor.fetchall()
            if len(myresult) == 0:
                return render_template("login.html", pass2 ="unsuccessfull login")
            
            if myresult[0][0] == password:
                sql2 = "SELECT company_id FROM companies WHERE user_id=%s"
                val2 = (myresult[0][1], )
                mycursor.execute(sql2, val2)
                company = mycursor.fetchall()
                session['username'] = company[0][0]
                
                return cprofile_page()
            else:
                
                return render_template("login.html", pass2 ="unsuccessfull login")

@app.route("/cprofile", methods=['GET', 'POST'])
def cprofile_page():
    global data
    print("data")
    print(data)
    if request.form.get("cv"):
        return render_template("login.html")


    if request.form.get("accepted"):
        txt = request.form['accepted']
        key = txt.split()
        sql = "UPDATE job_applications SET status = %s WHERE applicant_id = %s AND announcement_id = %s"
        val = ("ACCEPTED", key[0], key[1])
        mycursor = mydb.cursor()
        mycursor.execute(sql, val)
        mydb.commit()
        sql = "UPDATE companies SET score = score+5 WHERE company_id = %s"
        val = (session['username'], )
        mycursor.execute(sql, val)
        mydb.commit()
    if request.form.get("denied"):
        txt = request.form['denied']
        key = txt.split()
        sql = "UPDATE job_applications SET status = %s WHERE applicant_id = %s AND announcement_id = %s"
        val = ("DENIED", key[0], key[1])
        mycursor = mydb.cursor()
        mycursor.execute(sql, val)
        mydb.commit()
        sql = "UPDATE companies SET score = score+5 WHERE company_id = %s"
        val = (session['username'], )
        mycursor.execute(sql, val)
        mydb.commit()

    
    mycursor = mydb.cursor()
    sql = "SELECT COUNT(*) FROM announcements WHERE company_id=%s"
    val = (session['username'], )
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    sql = """
    SELECT COALESCE(applicants.name, '0'), announcements.announcement_id, applicants.applicant_id, applicants.surname, applicants.phone, applicants.email, applicants.cv, announcements.title
    FROM job_applications JOIN applicants ON applicants.applicant_id = job_applications.applicant_id
    RIGHT JOIN announcements ON announcements.announcement_id = job_applications.announcement_id
    WHERE company_id =%s
    ORDER BY announcements.announcement_id
    """
    mycursor.execute(sql, val)

    number = myresult[0][0]
    result = mycursor.fetchall()
    sql = """
    SELECT COUNT(*), announcements.ANNOUNCEMENT_ID, COMPANY_ID 
    FROM JOB_APPLICATIONS 
    RIGHT JOIN announcements ON announcements.announcement_id = job_applications.announcement_id
    GROUP BY announcements.ANNOUNCEMENT_ID
    HAVING company_id =%s
    
    
    
    """
    mycursor.execute(sql, val)
    iters = mycursor.fetchall()
    numbers = []
    orders = []
    for i in range(len(iters)):
        numbers.append(iters[i][0])
        
    for i in range(len(iters)):
        
        a = sum(int(i) for i in numbers[0:i])
        orders.append(a)
   
    size = len(result)
    print(iters)
    print(numbers)
    return render_template("cprofile.html", count = number,data1=result, loops = numbers, orders = orders, size=size)



@app.route("/profile", methods=['GET', 'POST'])
def profile_page():
    global data
    mycursor = mydb.cursor()
    sql = "SELECT name FROM applicants WHERE applicant_id=%s"
    val = (session['username'], )
    print(val)
    mycursor.execute(sql, val)
    my_result = mycursor.fetchall()
    sql = """SELECT companies.name, announcements.title, job_applications.status 
    FROM announcements 
    JOIN companies ON announcements.company_id = companies.company_id 
    JOIN job_applications ON announcements.announcement_id = job_applications.announcement_id
    WHERE job_applications.applicant_id = %s"""
    val = (session['username'], )
    mycursor.execute(sql, val)
    result = mycursor.fetchall()
    return render_template("profile.html", title = my_result, data = result)



@app.route("/app_login" ,methods=['GET', 'POST'])
def app_login_page():
    global data
    if request.method == "GET":
        return render_template("app_login.html")
    else:
        mycursor = mydb.cursor()
        
        
        if request.form.get("signin"):
            new_username = request.form["usernamenew"]
            new_password = request.form["passwordnew"]
            new_mail = request.form["mail"]
            new_phone = request.form["phone"]
            cname = request.form["name"]
            cv = request.files["cv"]
            surname = request.form["surname"]
            sql = "INSERT INTO users(username, password, membership) VALUES (%s, %s,%s)"
            val = (new_username, new_password, "A")
            mycursor.execute(sql, val)
            mydb.commit()
            sql = "SELECT user_id FROM users WHERE username=%s"
            val = (new_username,)
            mycursor.execute(sql, val)
            myresult = mycursor.fetchall()
            sql = "INSERT INTO applicants(name, surname, email, phone, membership_date, cv, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (cname, surname, new_mail, new_phone, date.today(), cv.read(), myresult[0][0])
            mycursor.execute(sql, val)
            mydb.commit()
            sql2 = "SELECT applicant_id FROM applicants WHERE user_id=%s"
            val2 = (myresult[0][0], )
            mycursor.execute(sql2, val2)
            company = mycursor.fetchall()
            session['username'] = company[0][0]
            return profile_page()
        else:
            form_username = request.form["username"]
            password = request.form["password"]
            sql = "SELECT password, user_id FROM users WHERE username=%s"
            val = (form_username,)
            mycursor.execute(sql, val)
            myresult = mycursor.fetchall()
            if len(myresult) == 0:
                return render_template("app_login.html", pass2 ="unsuccessfull login")
            if myresult[0][0] == password:
                sql2 = "SELECT applicant_id FROM applicants WHERE user_id=%s"
                val2 = (myresult[0][1], )
                mycursor.execute(sql2, val2)
                company = mycursor.fetchall()
                session['username'] = company[0][0]
                
                return profile_page()
            else:
                
                return render_template("app_login.html", pass2 ="unsuccessfull login")


@app.route("/download",methods=['GET', 'POST'])
def download():
    id = request.form['cv']
    mycursor = mydb.cursor()
    sql = "SELECT cv from applicants WHERE applicant_id = %s"
    val = (id, )
    mycursor.execute(sql, val)
    result = mycursor.fetchall()
    cv = result[0][0]
    
    return send_file(BytesIO(cv), attachment_filename="cv.pdf", as_attachment=True)


@app.route("/clear", methods=['GET', 'POST'])
def clear():
    mycursor = mydb.cursor()
    mycursor.execute("DELETE FROM announcements") 
    mydb.commit()
    mycursor.execute("DELETE FROM applicants") 
    mydb.commit()
    mycursor.execute("DELETE FROM companies")   
    mydb.commit()
    mycursor.execute("DELETE FROM users") 
    mydb.commit()
    mycursor.execute("DELETE FROM job_applications") 
    mydb.commit()

    return home_page()
    
@app.route("/delete", methods=['GET', 'POST'])
def delete():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT user_id FROM companies WHERE company_id = %s", (session['username'], ))
    my_result = mycursor.fetchall()
    mycursor.execute("DELETE FROM users WHERE user_id = %s", (my_result[0][0], ))
    mydb.commit()
    

    return home_page()


@app.route("/app_delete", methods=['GET', 'POST'])
def app_delete():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT user_id FROM applicants WHERE applicant_id = %s", (session['username'], ))
    my_result = mycursor.fetchall()
    mycursor.execute("DELETE FROM users WHERE user_id = %s", (my_result[0][0], ))
    mydb.commit()
    

    return home_page()



@app.route("/alter", methods=['GET', 'POST'])
def alter():
    mycursor = mydb.cursor()
    mycursor.execute("""ALTER TABLE announcements
DROP CONSTRAINT announcements_company_id_fkey;""")

    mydb.commit()
    

    return home_page()

@app.route("/filter", methods=['GET', 'POST'])
def filter():
    comp = request.form.get("comp")
    salary = request.form["salary"]
    working = request.form["options"]
    mycursor = mydb.cursor()
    mycursor.execute("""SELECT companies.name, title, announcement_id 
    FROM announcements JOIN companies ON announcements.company_id = companies.company_id
    WHERE announcements.company_id = %s AND working_day = %s AND salary > %s""", (comp, working ,salary))
    myresult = mycursor.fetchall()
    mycursor.execute("SELECT name, score FROM companies ORDER BY SCORE DESC")
    scores = mycursor.fetchall()
    mycursor.execute("SELECT * from companies")
    options = mycursor.fetchall()



    return render_template("announcements.html", data = myresult, scores= scores, options = options)

    


