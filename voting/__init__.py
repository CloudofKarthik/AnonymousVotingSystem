from flask import Flask, render_template

def create_app():
  app = Flask("voting")
  
  app.config.from_mapping(DATABASE="AVS")
  
  from . import db 
  db.init_app(app)
  
  @app.route("/")
  def login():
    return render_template('login.html')
  
  return app
  
  @app.route("/SignUp")
  def SignUp():
    return render_template('signup.html')
