from flask import make_response, jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
import json
from . import api
from app import db
from app.models import User


@api.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return make_response(jsonify(logged_in_as=current_user), 200)


@api.route("/register", methods=["POST"])
def register():
    data = json.loads(request.data)
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    error_data = {
        'message': 'Nome de usuário, email ou senha ausente', 'code': 'ERROR'}

    if not username or not email or not password:
        return make_response(jsonify(error_data), 404)

    try:
        new_user = User(username=username, email=email,
                        password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        return make_response(jsonify({'message': 'Usuário criado', 'code': 'SUCCESS'}), 200)
    except Exception as e:
        print(e)
        return make_response(jsonify({'message': 'Erro ao criar usuário', 'code': 'ERROR'}), 500)


@api.route("/login", methods=["POST"])
def login():
    try:
        data = json.loads(request.data)
        email = data.get('email')
        password = data.get('password')
        user = User.query.filter_by(email=email).first()

        error_data = {
            'message': 'Email ou senha incorreto', 'code': 'Error'}

        if user is None:
            return make_response(jsonify(error_data), 404)

        elif not check_password_hash(user.password, password):
            return make_response(jsonify(error_data), 404)

        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'date_created': user.date_created,
            'date_updated': user.date_updated
        }

        data.update({"token": create_access_token(data)})

        return make_response(jsonify(data), 200)
    except Exception as e:
        data = {'message': 'Erro ao tentar efetuar login', 'code': 'ERROR'}
    return make_response(jsonify(data), 400)
