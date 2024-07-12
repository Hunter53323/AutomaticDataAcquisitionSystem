from flask import Blueprint

db = Blueprint("dbapi", __name__)

from . import dbapi
