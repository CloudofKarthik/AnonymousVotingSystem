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
      return render_template('login.html')
    elif request.method == "POST":
      
      name = request.form.get("login")
      password = request.form.get("password")
 
      query1 = "Select name, password from users where name = '{un}' and password = '{pw}'".format(un = name,pw = password)
      
      cursor.execute(query1)
      rows = cursor.fetchall()
      if len(rows)==1:
        return redirect("/polls")
      else:
        return render_template('login.html')
  
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
      
      
  @app.route("/polls")
  def polls():
    return render_template('polls.html')
    
  return app
