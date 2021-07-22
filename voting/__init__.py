from flask import Flask, render_template

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
    return render_template('reg.html')
    
  return app
