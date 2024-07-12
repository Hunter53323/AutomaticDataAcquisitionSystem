from flask import Blueprint

control = Blueprint("collect", __name__)

from . import device_controlapi
