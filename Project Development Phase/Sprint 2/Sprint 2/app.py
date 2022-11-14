from flask import Flask, render_template, request , session
import ibm_db

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
            sql="SELECT * FROM REG WHERE CONTACT=?"
            stmt= ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,ph)
            ibm_db.execute(stmt)
            account = ibm_db.fetch_assoc(stmt)
            #account = ibm_db.fetch(stmt)
            print(account[1])
            if account:
                return render_template("register.html",msg="ALREADY EXISTS")
            else:
                insert_sql="Insert INTO REG VALUES(?,?,?,?)"
                prep_stmt=ibm_db.prepare(conn,insert_sql)
                ibm_db.bind_param(prep_stmt,1,un)
                ibm_db.bind_param(prep_stmt,2,ps)
                ibm_db.bind_param(prep_stmt,3,mail)
                ibm_db.bind_param(prep_stmt,4,ph)
                ibm_db.execute(prep_stmt)
                return render_template("dashboard.html",un=un)
        #return render_template("table.html",un=un,ps=ps,mail=mail,ph=ph)

@app.route("/login",methods=["POST","GET"])
def login():
    global userid
    un=request.form.get('un')
    ps=request.form.get('ps')
    msg=" "
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


            return render_template("dashboard.html", un=account["MAIL"])
        else:
            return render_template("index.html",msg="Incorrect username or password")

@app.route("/logout",methods=["POST","GET"])
def logout():
    
    return render_template("index.html")

#@app.route("/view", methods=["POST","GET"])
#def view():


if __name__=='__main__':
    app.run(debug=True)