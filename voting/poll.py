from flask import render_template, request, redirect, url_for
from flask import g
from . import db
from flask import Blueprint



bp = Blueprint("voting", "voting", url_prefix="/polls")

@bp.route("/<ID>")
def polls(ID):

  return render_template('polls.html',ID = ID)

