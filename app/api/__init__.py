
from flask import Blueprint

api = Blueprint('api', __name__)
from . import authentication, spotify, wallpaper  # nopep8
