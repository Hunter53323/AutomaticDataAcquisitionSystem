from flask import Blueprint

socketio_http = Blueprint("socketio_http", __name__)

from . import real_time_dataapi
