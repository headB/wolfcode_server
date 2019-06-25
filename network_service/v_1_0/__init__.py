from flask import Blueprint

register_api = Blueprint("register",__name__)
micro_app_api = Blueprint("micro_app",__name__)

from . import micro_app
from . import activity
from .register import register
