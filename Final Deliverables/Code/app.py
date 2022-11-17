from flask import Flask, render_template, request , session, url_for
import ibm_db
from datetime import date

app=Flask(__name__)
app.secret_key='a'
conn=ibm_db.connect('DATABASE=bludb ; HOSTNAME=19af6446-6171-4641-8aba-9dcff8e1b6ff.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud; PORT=30699; SECURITY=SSL; SSLServerCertificate=certificate.crt; UID=tkw12011; PWD=eZMQ7GoxrPm60kiw;', '', '')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register",methods=["POST","GET"])
def register():
    return render_template("register.html")

@app.route("/insert",methods=["POST","GET"])
def insert():
     if request.method=="POST":
        un=request.form.get('un')
        ps=request.form.get('ps')
        mail=request.form.get('mail')
        ph=request.form.get('ph')

        if un=="":
            return render_template("register.html",msg="USERNAME MISSING")
        elif ps=="":
            return render_template("register.html",msg="ENTER THE PASSWORD")
        elif mail=="":
            return render_template("register.html",msg="EMAIL MISSING")
        elif ph=="":
            return render_template("register.html",msg="PHONE NUMBER MISSING")
        else:
            sql="SELECT * FROM REG WHERE MAIL=?"
            stmt= ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,mail)
            ibm_db.execute(stmt)
            account = ibm_db.fetch_assoc(stmt)
            
            if account:
                return render_template("register.html",msg="MAIL ID ALREADY EXISTS")
            else:
                insert_sql="Insert INTO REG VALUES(?,?,?,?)"
                prep_stmt=ibm_db.prepare(conn,insert_sql)
                ibm_db.bind_param(prep_stmt,1,un)
                ibm_db.bind_param(prep_stmt,2,ps)
                ibm_db.bind_param(prep_stmt,3,mail)
                ibm_db.bind_param(prep_stmt,4,ph)
                ibm_db.execute(prep_stmt)
                sql="INSERT INTO EXP VALUES(?,?,?)"
                a=0
                stmt=ibm_db.prepare(conn,sql)
                ibm_db.bind_param(stmt,1,mail)
                ibm_db.bind_param(stmt,2,a)
                ibm_db.bind_param(stmt,3,a)
                ibm_db.execute(stmt)
                return render_template("dashboard.html",un=un)

@app.route("/login",methods=["POST","GET"])
def login():
    global userid
    un=request.form.get('un')
    ps=request.form.get('ps')
    if un=="":
        return render_template("index.html",msg="Please enter username")
    elif ps=="":
        return render_template("index.html",msg="Please enter password")    

    if request.method=="POST":
        un=request.form.get('un')
        ps=request.form.get('ps')
        sql="SELECT * FROM REG WHERE username=? AND password=?"
        stmt= ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,un)
        ibm_db.bind_param(stmt,2,ps)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            session['Loggedin']=True
            session['id'] = account['USERNAME']
            userid=account["USERNAME"]
            session['username']=account["USERNAME"]
            return render_template("dashboard.html", un=account["USERNAME"])
        else:
            return render_template("index.html",msg="Incorrect username/password")

@app.route("/logout",methods=["POST","GET"])
def logout():
    return render_template("index.html")

@app.route("/view", methods=["POST","GET"])
def view():
    msg=" "
    array1=[]
    array2=[]
    sql="SELECT * FROM REG WHERE username=?"
    stmt= ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,userid)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    un=account["USERNAME"]
    mail=account["MAIL"]
    ph=account["CONTACT"]
    
    sql="SELECT * FROM EXP WHERE MAIL=?"
    stmt= ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,mail)
    ibm_db.execute(stmt)
    exp= ibm_db.fetch_assoc(stmt)
    bd=exp["BUDGET"]
    ex=exp["EXPENSE"]
    if bd > ex:
        msg="You have not exceeded your budget limit"
    elif ex > bd:
        msg="You have exceeded your budget limit"
    elif bd == ex:
        msg="You reached your budget limit"
    
    sql="SELECT * FROM CAT WHERE MAIL=?"
    stmt= ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,mail)
    ibm_db.execute(stmt)
    #history1= ibm_db.fetch_tuple(stmt)
    array1=ibm_db.fetch_tuple(stmt)
    while array1 != False:
        array2.append(array1)
        array1=ibm_db.fetch_both(stmt)

    return render_template("view.html", USERNAME=un,CONTACT=ph,EMAIL=mail,BUDGET=bd,EXPENSE=ex,msg=msg,arr=array2)
    #return render_template("view.html",USERNAME=un,CONTACT=ph,EMAIL=mail,BUDGET=bd,EXPENSE=ex,msg=msg,account1=history1,account2=history2,account3=history3,account4=history4,account5=history5)
    
@app.route("/dashboard",methods=["POST","GET"])
def dashboard():
    return render_template("dashboard.html",un=userid)

@app.route("/budget", methods=["GET","POST"])
def budget():
    sql="SELECT * FROM REG WHERE username=?"
    stmt= ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,userid)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    mail=account["MAIL"]
    
    sql="SELECT * FROM EXP WHERE MAIL=?"
    stmt= ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,mail)
    ibm_db.execute(stmt)
    exp= ibm_db.fetch_assoc(stmt)
    bd=exp["BUDGET"]
    return render_template("budget.html",bd=bd)

@app.route("/set_budget", methods=["GET","POST"])
def set_budget():
    bd=0
    sql="SELECT * FROM REG WHERE username=?"
    stmt= ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,userid)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    mail=account["MAIL"]
    
    bd=request.form.get('bd')
    if bd=="":
        return render_template("budget.html",msg="Please enter budget limit")
    sql="UPDATE EXP SET BUDGET=? WHERE MAIL=?"
    stmt= ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,bd)
    ibm_db.bind_param(stmt,2,mail)
    ibm_db.execute(stmt)
    return render_template("budget.html",msg="BUDGET IS SET",bd=bd)

@app.route("/expense", methods=["POST","GET"])
def expense():
    sql="SELECT * FROM REG WHERE username=?"
    stmt= ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,userid)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    mail=account["MAIL"]
    
    sql="SELECT * FROM EXP WHERE MAIL=?"
    stmt= ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,mail)
    ibm_db.execute(stmt)
    exp= ibm_db.fetch_assoc(stmt)
    ex=exp["EXPENSE"]
    return render_template("expense.html",ex=ex)

@app.route("/add_expense", methods=["GET","POST"])
def add_expense():
    sql="SELECT * FROM REG WHERE username=?"
    stmt= ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,userid)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    mail=account["MAIL"]
    
    ex=request.form.get('ex')
    cat=request.form.get('cat')
    today=date.today()
    if ex=="":
        return render_template("expense.html",msg="Please enter expenditure")
    if cat=="":
        return render_template("expense.html",msg="Please choose a category")
    
    sql="SELECT * FROM EXP WHERE MAIL=?"
    stmt= ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,mail)
    ibm_db.execute(stmt)
    exp= ibm_db.fetch_assoc(stmt)
    prev_ex=exp["EXPENSE"]
    tot_ex=prev_ex+int(ex)
   
    sql="UPDATE EXP SET EXPENSE=? WHERE MAIL=?"
    stmt= ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,tot_ex)
    ibm_db.bind_param(stmt,2,mail)
    ibm_db.execute(stmt)
    
    sql="INSERT INTO CAT VALUES(?,?,?,?)"
    stmt= ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,mail)
    ibm_db.bind_param(stmt,2,ex)
    ibm_db.bind_param(stmt,3,cat)
    ibm_db.bind_param(stmt,4,today)
    ibm_db.execute(stmt)
    return render_template("expense.html",msg="EXPENSE IS ADDED",ex=tot_ex)

if __name__=='__main__':
    app.run(host='0.0.0.0',debug=True)