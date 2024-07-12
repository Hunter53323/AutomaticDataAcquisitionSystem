from flask import Blueprint

autocollect = Blueprint("collect", __name__)

from . import auto_collectapi
