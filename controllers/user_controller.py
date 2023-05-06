import json
import datetime
import uuid
from flask import make_response, jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash
from . import api
from utils import validate_image, user_login_validate, user_register_validate, user_update_validate
from app import db, Config, s3
from schemas import UserSchema
from models import User


@api.route("/user/<int:id>", methods=["PUT"])
@jwt_required()
@cross_origin(origins=Config.CLIENT_URL)
def update_user(id):
    current_user = get_jwt_identity()
    form_data = request.form
    file = request.files.get('image')
    username = form_data.get('username')

    user_update_validate(current_user, username)

    try:
        user = User.query.filter_by(id=id).first()
        user.username = username

        if file:
            # Faz o upload do arquivo para o S3
            validate_image(file)
            uuid_code = str(uuid.uuid4())
            filename = f'{uuid_code}-{file.filename.strip()}'
            s3.upload_fileobj(file, Config.AWS_BUCKET_NAME, filename)
            url = f"{Config.AWS_SS3_CUSTOM_DOMAIN}/{filename}"
            user.image = url

        # Atualiza usuário no banco
        db.session.commit()

        # Cria os objetos de schema e faz o dump dos dados
        user_schema = UserSchema()
        user_data = user_schema.dump(user)
        expires = datetime.timedelta(days=7)
        user_data.update({"token": create_access_token(user_data, expires)})

        return make_response(jsonify(user_data), 201)
    except:
        # Erro genérico
        error_data = {
            'message': 'Erro ao tentar editar usuário',
            'code': 'ERROR'
        }
        return make_response(jsonify(error_data), 500)


@api.route("/register", methods=["POST"])
@cross_origin(origins=Config.CLIENT_URL)
def register():
    data = json.loads(request.data)
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    user = User.query.filter_by(email=email).first()

    user_login_validate(username, email, password, confirm_password, user)

    try:
        new_user = User(username=username, email=email,
                        password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        user_schema = UserSchema()
        user_json = user_schema.dump(new_user)

        expires = datetime.timedelta(days=7)
        user_json.update({"token": create_access_token(user_json, expires)})
        return make_response(jsonify(user_json), 201)
    except:
        # Erro genérico
        error_data = {
            'message': 'Erro ao tentar criar usuário',
            'code': 'ERROR'
        }
        return make_response(jsonify(error_data), 500)


@api.route("/login", methods=["POST"])
@cross_origin(origins=Config.CLIENT_URL)
def login():
    try:
        data = json.loads(request.data)
        email = data.get('email', None)
        password = data.get('password', None)
        user = User.query.filter_by(email=email).first()

        user_register_validate(email=email, password=password, user=user)

        user_schema = UserSchema()
        user_json = user_schema.dump(user)

        expires = datetime.timedelta(days=7)
        user_json.update({"token": create_access_token(user_json, expires)})

        return make_response(jsonify(user_json), 200)

    except:
        # Erro genérico
        error_data = {
            'message': 'Erro ao tentar efetuar login', 'code': 'ERROR'}
        return make_response(jsonify(error_data), 400)
