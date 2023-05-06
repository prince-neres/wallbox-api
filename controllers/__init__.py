from flask import Blueprint

api = Blueprint('api', __name__)
from . import user_controller, wallpaper_controller  # nopep8
