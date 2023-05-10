import json
import datetime
from flask import make_response, jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from . import api
from utils import user_login_validate, user_register_validate, user_update_validate
from app import db, Config, s3
from schemas import UserSchema
from models import User
from services import s3_image_upload


@api.route("/user/<int:id>", methods=["PUT"])
@jwt_required()
@cross_origin(origins=Config.CLIENT_URL)
def update_user(id):
    # Obtém o ID do usuário autenticado a partir do token JWT
    current_user = get_jwt_identity()

    # Obtém os dados do formulário e o arquivo de imagem (se fornecido)
    form_data = request.form
    file = request.files.get('image')
    username = form_data.get('username')

    # Validação de entrada
    error = user_update_validate(current_user, id, username)
    if error:
        return make_response(jsonify(error), 401)

    try:
        # Busca o usuário a ser atualizado no banco de dados
        user = User.query.filter_by(id=id).first()

        # Atualiza as informações do usuário
        user.username = username
        if file:
            # Faz o upload da nova imagem para o armazenamento S3
            url, filename = s3_image_upload(file, image='avatar')
            user.image = url

        # Salva as alterações no banco de dados
        db.session.commit()

        # Prepara os dados de retorno para o cliente
        user_schema = UserSchema()
        user_data = user_schema.dump(user)
        expires = datetime.timedelta(days=7)
        user_data['token'] = create_access_token(
            user_data, expires_delta=expires)

        # Retorna a resposta de sucesso
        return make_response(jsonify(user_data), 201)

    except Exception as error:
        # Retorna uma resposta de erro genérico para o cliente
        error_data = {
            'message': f'Erro ao tentar editar usuário: {str(error)}',
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

    # Validar dados do usuário
    error = user_register_validate(
        username, email, password, confirm_password, user)
    if error:
        return make_response(jsonify(error), 401)

    try:
        # Criar novo usuário
        new_user = User(username=username, email=email,
                        password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        # Gerar token de acesso
        user_schema = UserSchema()
        user_json = user_schema.dump(new_user)
        expires = datetime.timedelta(days=7)
        user_json.update({"token": create_access_token(
            user_json, expires_delta=expires)})

        # Responder com dados do usuário e token de acesso
        return make_response(jsonify(user_json), 201)
    except Exception as e:
        # Responder com erro genérico
        error_data = {
            'message': f'Erro ao tentar criar usuário: {str(e)}',
            'code': 'ERROR'
        }
        return make_response(jsonify(error_data), 500)


@api.route("/login", methods=["POST"])
@cross_origin(origins=Config.CLIENT_URL)
def login():
    try:
        data = json.loads(request.data)
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        # Válida dados do usuário
        error = user_login_validate(email, password, user)
        if error:
            return make_response(jsonify(error), 401)

        user_schema = UserSchema()
        user_json = user_schema.dump(user)

        # Gera um token de acesso com validade de 7 dias
        expires = datetime.timedelta(days=7)
        user_json.update({"token": create_access_token(
            user_json, expires_delta=expires)})

        return make_response(jsonify(user_json), 200)

    except Exception as e:
        error_data = {
            'message': f'Erro ao tentar efetuar login: {str(e)}',
            'code': 'ERROR'
        }
        return make_response(jsonify(error_data), 500)
