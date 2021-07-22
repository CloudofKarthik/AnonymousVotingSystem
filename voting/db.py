import psycopg2
import click
from flask import current_app, g
from flask.cli import with_appcontext
from psycopg2 import connect

def get_db():
    if 'db' not in g: # If we've not initialised the database, then
                      # initialise it
        # Notice how we take the name of the database from the
        # config. We initialised this in the __init__.py file.
        dbname = current_app.config['DATABASE'] 
        print(dbname)
        g.db = psycopg2.connect(f"dbname={dbname}")
    return g.db
  
  
def close_db(e=None):
  db = g.pop('db',None)
  
  if db is not None:
    db.close()
    
def init_db():
  db = get_db()
  f = current_app.open_resource("sql/000_create.sql")
  sql_code = f.read().decode("ascii")
  cur= db.cursor()
  cur.execute(sql_code)
  cur.close()
  db.commit()
  
@click.command('initdb', help="initialise database")
@with_appcontext
def init_db_command():
    init_db()
    click.echo('DB initialised')
    
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    
