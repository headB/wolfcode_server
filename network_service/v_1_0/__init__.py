from flask import Blueprint

register_api = Blueprint("register",__name__)
postman_api = Blueprint("postman",__name__)
network_api = Blueprint("network",__name__)


from .network_manager import ssh
from .postman import postman
from .register import register