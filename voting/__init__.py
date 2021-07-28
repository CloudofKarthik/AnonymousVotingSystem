from flask import Flask, render_template
from flask import Blueprint, session
from flask import request, redirect, url_for
import datetime
from datetime import date
import re

def create_app():
  app = Flask("voting")
  app.secret_key = "super secret key"
  
  app.config.from_mapping(DATABASE="AVS")
  
  from . import db 
  db.init_app(app)
  
  @app.route("/", methods=['GET','POST'])
  def login():
    conn = db.get_db()
    cursor = conn.cursor()
    if request.method == "GET":
      return render_template('index.html')
    elif request.method == "POST":
      
      name = request.form.get("login")
      password = request.form.get("password")
 
      query1 = "Select id, name,email, password from users where name = '{un}' and password = '{pw}'".format(un = name,pw = password)
      
      cursor.execute(query1)
      rows = cursor.fetchone()
      if not rows:
        return render_template('index.html', message="Username or password is incorrect")
      else:
        session['name'] = rows[1]
        session['email'] = rows[2]
        ID, name, email, pwd = rows
        return redirect(url_for("polls", ID=ID), 302)
        
  
  @app.route("/register", methods=['GET','POST'])
  def SignUp():
    conn = db.get_db()
    cursor = conn.cursor()
    if request.method == "GET":  
      return render_template('reg.html')
    elif request.method == "POST":
      username = request.form.get("Username")
      email = request.form.get("email")
      password = request.form.get("password")
      cursor.execute("select name from users where name = '{n}' or email ='{e}'".format(n = username,e = email))
      rows = cursor.fetchone()
      if rows:
        message = "Username or email already exists"
        return render_template('reg.html',message = message)
      else:  
        cursor.execute("""INSERT INTO
          users (name, email, password) 
          VALUES (%s, %s, %s)""",(username, email, password))
        conn.commit()
        return redirect('/')
      
  @app.route("/polls/<ID>", methods=['GET','POST'])
  def polls(ID):
    conn = db.get_db()
    cursor = conn.cursor()
    if request.method == "GET":
      query1 = "Select name from users where id = '{ID}'".format(ID = ID)
      cursor.execute(query1)
      rows = cursor.fetchone()
      return render_template('polls.html',ID = ID)
      
    if request.method == "POST":
      value1 = request.form.get("commit_create")
      value2 = request.form.get("commit_view")
      value3 = request.form.get("commit_logout")
      if value1=="CREATE POLL":
        return redirect(url_for("create_polls", ID=ID), 302)
      elif value2=="VIEW POLLS":
        return redirect(url_for("view_polls", ID=ID), 302)
      elif value3=="LOGOUT":
        session.clear()
        return redirect(url_for("polls", ID=ID), 302)
      
  @app.route("/polls/<ID>/create_poll", methods=['GET','POST'])
  def create_polls(ID):
    conn = db.get_db()
    cursor = conn.cursor()
    if request.method == "GET":
      return render_template('create_poll.html',ID = ID)
    elif request.method == "POST":
      poll_name = request.form.get("poll_name").strip()
      no_of_polls = request.form.get("no_of_options")
      deadline = request.form.get("deadline")
      cursor.execute("""INSERT INTO
        polls (owner, poll_name, no_of_options, deadline) 
        VALUES ({ID}, '{pn}', {nop}, '{deadline}')""".format(ID=ID, pn=poll_name, nop=no_of_polls, deadline=deadline))
      conn.commit()
      query1 = "Select max(id) from polls where owner = '{ID}'".format(ID = ID)
      cursor.execute(query1)
      rows = cursor.fetchone()
      options = request.form.get("options")
      options = options.strip()
      option_list = list(options.split("\n"))
      l = len(option_list)
      for j in range(l):
        option_list[j] = option_list[j].replace(" ","_")
        option_list[j] = "c_"+option_list[j]
        
      
      table_name=str(poll_name+str(rows[0]))
      table_name = table_name.strip()
      table_name = table_name.replace(" ","_")
      table_name = table_name.translate({ord(c): "_" for c in "!@#$%^&*()[]{};:,./<>?\|`~-=+"})
      
      table_name = "table_"+table_name
      
      
      pid = rows[0]
      cursor.execute("""CREATE TABLE {table_name}(pid int, constraint fk_options foreign key(pid) REFERENCES polls(id))""".format(table_name = table_name))
      conn.commit()
      query3 = "insert into {table_name}(pid) values({pid})".format(table_name=table_name, pid = pid)
      cursor.execute(query3)
      conn.commit()
      for i in range(l):
        query2 = """Alter table {table_name} add column {column} integer""".format(table_name=table_name, column=option_list[i])
        cursor.execute(query2)
        conn.commit()
        query4 = "update {table_name} set {option}=0".format(table_name=table_name, option=option_list[i])
        cursor.execute(query4)
        conn.commit()
      return redirect(url_for("polls", ID=ID), 302)
      
  @app.route("/polls/<ID>/view_polls", methods=['GET','POST'])
  def view_polls(ID):
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("select id, owner, poll_name, deadline from polls where owner = %s", (ID,))
    polls = cursor.fetchall()
    if not polls:
      return redirect(url_for("polls", ID=ID), 302)
    job = cursor.fetchone()
    if request.method == "GET":
      return render_template('view_polls.html',ID = ID, polls = polls)
      
  @app.route("/polls/<ID>/<pid>", methods=['GET','POST'])
  def poll_details(ID,pid):
    conn = db.get_db()
    cursor = conn.cursor()
    if request.method == "GET":
      cursor.execute("select poll_name, deadline from polls where id = %s", (pid,))
      row = cursor.fetchone()
      pollname=row[0]
      deadline=row[1]
      curdate = date.today()
      pollname1 = pollname
      pollname = pollname.replace(' ','_')
      pollname = pollname.translate({ord(c): "_" for c in "!@#$%^&*()[]{};:,./<>?\|`~-=+"})
      pollname = pollname+str(pid)
      pollname = 'table_'+pollname
        
      pollname2 = pollname.lower()
     
      cursor.execute("select column_name from information_schema.columns where table_name = %s",(pollname2,))
      rows = cursor.fetchall()
      row_list = []
   
      for r in rows:
        row_list.append(r[0])
      row_list = row_list[1:len(row_list)]
      l = len(row_list)
      for i in range(l):
        row_list[i] = row_list[i][2:len(row_list[i])]
      cursor.execute("select * from {table_name}".format(table_name=pollname))
   
      row1 = cursor.fetchone()
      row1 = list(row1[1:len(row1)])

      dict1 = dict(zip(row_list, row1))
      max = 0
      list1 = []
      for k in range(len(row1)):
        if row1[k] >= max:
          max = row1[k]

      for k in range(len(row1)):
        if row1[k] == max:
          list1.append(k)

      winners = ""
      winners = winners + row_list[list1[0]]
      for i in range(1, len(list1)):
        winners = winners +", "+str(row_list[list1[i]])
        


      
     
      return render_template('poll_details.html', ID=ID, pid=pid, rows=row_list,deadline=deadline,curdate=curdate, pollname=pollname1, row = row1, dictionary = dict1, winners = winners) 
      
    
  @app.route("/polls/edit_poll/<pid>", methods=['GET','POST'])
  def edit_poll(pid):
    conn = db.get_db()
    cursor = conn.cursor()
    if request.method == "GET":
      cursor.execute("select poll_name, deadline from polls where id = %s", (pid,))
      row = cursor.fetchone()
      pollname = row[0]
      curdate = date.today()
      deadline = row[1]
      pollname1 = pollname
      pollname = pollname.replace(" ","_")
      pollname = pollname+str(pid)
      pollname = "table_"+pollname
      pollname = pollname.translate({ord(c): "_" for c in "!@#$%^&*()[]{};:,./<>?\|`~-=+"})     
      pollname2 = pollname.lower()
      cursor.execute("select column_name from information_schema.columns where table_name = %s",(pollname2,))
      rows = cursor.fetchall()
      row_list = []
      for r in rows:
        row_list.append(r[0])
      row_list = row_list[1:len(row_list)]
      l = len(row_list)
      for i in range(l):
        row_list[i] = row_list[i][2:len(row_list[i])]
      cursor.execute("select * from {table_name}".format(table_name=pollname))
      row1 = cursor.fetchone()
      row1 = list(row1[1:len(row1)])
      return render_template('edit_poll.html', row1=row_list, pollname=pollname1, pid=pid, deadline=str(deadline), curdate=str(curdate))
      
    elif request.method == "POST":
     
      option = request.form.get("Options")
      option = "c_"+option
      query1 = "select poll_name from polls where id={pid}".format(pid=pid)
      cursor.execute(query1)
      row = cursor.fetchone()
      table_name = row[0]
      table_name = table_name.replace(" ","_")
      table_name = "table_"+table_name+str(pid)
      table_name = table_name.translate({ord(c): "_" for c in "!@#$%^&*()[]{};:,./<>?\|`~-=+"})
      query2 = "update {table_name} set {option}={option}+1".format(table_name=table_name, option=option)
     
      cursor.execute(query2)
      conn.commit()
      return redirect('/')
    
  return app
