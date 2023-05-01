from flask import make_response, jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
import json
from . import api
from app import db, Config
from app.models import User


@api.route("/protected", methods=["GET"])
@jwt_required()
@cross_origin(origins=Config.CLIENT_URL)
def protected():
    current_user = get_jwt_identity()
    return make_response(jsonify(logged_in_as=current_user), 200)


@api.route("/register", methods=["POST"])
@cross_origin(origins=Config.CLIENT_URL)
def register():
    data = json.loads(request.data)
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    # Verifica se todos os campos estão presentes
    if not username or not email or not password:
        error_data = {
            'message': 'Nome de usuário, email ou senha ausente',
            'code': 'ERROR'
        }
        return make_response(jsonify(error_data), 400)

    # Verifica se a senha e a confirmação são iguais
    if not password == confirm_password:
        error_data = {
            'message': 'As senhas não coincidem',
            'code': 'ERROR'
        }
        return make_response(jsonify(error_data), 400)

    # Verifica se já existe um usuário com o mesmo email
    user = User.query.filter_by(email=email).first()
    if user is not None:
        error_data = {
            'message': 'Já existe um usuário com esse email',
            'code': 'ERROR'
        }
        return make_response(jsonify(error_data), 409)

    try:
        new_user = User(username=username, email=email,
                        password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        data = {
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email,
            'date_created': new_user.date_created,
            'date_updated': new_user.date_updated
        }
        data.update({"token": create_access_token(data)})
        return make_response(jsonify(data), 201)
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

        # Validação de entrada de dados
        if not email or not isinstance(email, str):
            return make_response(jsonify({'message': 'Email inválido', 'code': 'INVALID_EMAIL'}), 400)

        if not password or not isinstance(password, str):
            return make_response(jsonify({'message': 'Senha inválida', 'code': 'INVALID_PASSWORD'}), 400)

        user = User.query.filter_by(email=email).first()

        if user is None:
            # Usuário não encontrado
            return make_response(jsonify({'message': 'Email incorreto', 'code': 'USER_NOT_FOUND'}), 404)

        if not check_password_hash(user.password, password):
            # Senha incorreta
            return make_response(jsonify({'message': 'Senha incorreta', 'code': 'INVALID_PASSWORD'}), 401)

        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'date_created': user.date_created,
            'date_updated': user.date_updated
        }

        data.update({"token": create_access_token(data)})

        return make_response(jsonify(data), 200)

    except:
        # Erro genérico
        data = {'message': 'Erro ao tentar efetuar login', 'code': 'ERROR'}
        return make_response(jsonify(data), 400)
