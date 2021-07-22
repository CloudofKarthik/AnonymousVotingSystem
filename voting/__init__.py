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
    return render_template('login.html')
  
  @app.route("/register", methods=['GET','POST'])
  def SignUp():
    conn = db.get_db()
    cursor = conn.cursor()
    if request.method == "GET":  
      print("qwerty")
      return render_template('reg.html')
    elif request.method == "POST":
      username = request.form.get("Username")
      email = request.form.get("email")
      password = request.form.get("password")
      print("asdfg")
      cursor.execute("""INSERT INTO
        users (name, email, password) 
        VALUES (%s, %s, %s)""",(username, email, password))
      conn.commit()
      return redirect('/')
    
  return app
