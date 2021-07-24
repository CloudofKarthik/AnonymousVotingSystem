from flask import Flask, render_template
from flask import Blueprint
from flask import request, redirect, url_for
import datetime

def create_app():
  app = Flask("voting")
  
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
 
      query1 = "Select id, name, password from users where name = '{un}' and password = '{pw}'".format(un = name,pw = password)
      
      cursor.execute(query1)
      rows = cursor.fetchone()
      if not rows:
        return render_template('index.html')
      else:
        ID, name, pwd = rows
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
      if value1=="CREATE POLL":
        return redirect(url_for("create_polls", ID=ID), 302)
      elif value2=="VIEW POLLS":
        return redirect(url_for("view_polls", ID=ID), 302)
      
  @app.route("/polls/<ID>/create_poll", methods=['GET','POST'])
  def create_polls(ID):
    conn = db.get_db()
    cursor = conn.cursor()
    if request.method == "GET":
      return render_template('create_poll.html',ID = ID)
    elif request.method == "POST":
      poll_name = request.form.get("poll_name")
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
      
      table_name=str(poll_name+str(rows[0]))
      table_name = table_name.replace(" ","_")
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
    cursor.execute("select id, poll_name, deadline from polls where owner = %s", (ID,))
    polls = cursor.fetchall()
    if not polls:
      return redirect(url_for("polls", ID=ID), 302)
    job = cursor.fetchone()
    if request.method == "GET":
      return render_template('view_polls.html',ID = ID, polls = polls)
      
    
      
    
  return app
