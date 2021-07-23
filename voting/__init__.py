from flask import Flask, render_template
from flask import Blueprint
from flask import request, redirect, url_for

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
      return redirect(url_for("create_polls", ID=ID), 302)
      
  @app.route("/polls/<ID>/create_poll", methods=['GET','POST'])
  def create_polls(ID):
    conn = db.get_db()
    cursor = conn.cursor()
    if request.method == "GET":
      return render_template('create_poll.html',ID = ID)
    elif request.method == "POST":
      poll_name = request.form.get("poll_name")
      no_of_polls = request.form.get("no_of_options")
      cursor.execute("""INSERT INTO
        polls (owner, poll_name, no_of_options) 
        VALUES (%s, %s, %s)""",(ID, poll_name, no_of_polls))
      conn.commit()
      return redirect(url_for("polls", ID=ID), 302)
      
    
      
    
  return app
