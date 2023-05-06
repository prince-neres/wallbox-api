from flask import make_response, jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
import json
from . import api
from utils.validations import validate_image
from app import db, Config, s3
from schemas.user_schema import UserSchema
from models.user import User
import datetime
import uuid


@api.route("/user/<int:id>", methods=["PUT"])
@jwt_required()
@cross_origin(origins=Config.CLIENT_URL)
def update_user(id):
    current_user = get_jwt_identity()
    form_data = request.form
    file = request.files.get('image')
    username = form_data.get('username')

    if current_user.get('id') != id:
        error_data = {
            'message': 'Sem permissão',
            'code': 'NOT_PERMISSION'
        }
        return make_response(jsonify(error_data), 400)

    if not username:
        error_data = {
            'message': 'O campo usuário precisa ser preenchido',
            'code': 'INVALID_DATA'
        }
        return make_response(jsonify(error_data), 400)

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
            'message': 'As senhas não coi	ncidem',
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
