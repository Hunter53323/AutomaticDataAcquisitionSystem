from flask import Blueprint

control = Blueprint("control", __name__)

from . import device_controlapi
