from . import api
from app.models import Wallpaper, User
from flask import make_response, jsonify, request, send_file
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO
from PIL import Image
from app import db
import json
import base64


# Authentication Enpoints
@api.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return make_response(jsonify(logged_in_as=current_user), 200)


@api.route("/register", methods=["POST"])
def register():
    data = json.loads(request.data)
    print(data)
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
        print(e)
        data = {'message': 'Erro ao tentar efetuar login', 'code': 'ERROR'}
    return make_response(jsonify(data), 400)


# Wallpapers Endpoints
@api.route('/wallpapers')
@cross_origin(origins='http://localhost:5173')
def get_wallpapers():
    wallpapers = Wallpaper.query.all()
    wallpapers_list = []
    for wallpaper in wallpapers:
        base64_data = base64.b64encode(wallpaper.image).decode('utf-8')

        wallpapers_list.append({
            'id': wallpaper.id,
            'title': wallpaper.title,
            'image': base64_data
        })
    return make_response(jsonify(wallpapers_list), 200)


@api.route('/wallpaper/<int:id>')
@cross_origin(origins='http://localhost:5173')
def get_wallpaper(id):
    wallpaper = Wallpaper.query.filter_by(id=id).first()
    # Convertendo a imagem de bytea para um objeto de imagem
    image = Image.open(BytesIO(wallpaper.image))

    # Salvando a imagem em um buffer de Bytes
    img_buffer = BytesIO()
    image.save(img_buffer, format='JPEG')
    img_buffer.seek(0)

    # Retornando a imagem no formato original
    return send_file(img_buffer, mimetype='image/jpeg')


@api.route('/upload_image', methods=['POST'])
@cross_origin(origins='http://localhost:5173')
def upload_image():
    form_data = request.form
    image = request.files['image']
    filename = image.filename
    byte_image = image.read()
    title = form_data.get('title')
    user_id = form_data.get('user_id')
    tags = eval(form_data.get('tags'))
    description = form_data.get('description')

    new_image = Wallpaper(
        title=title,
        filename=filename,
        image=byte_image,
        user_id=user_id,
        tags=tags,
        description=description
    )

    db.session.add(new_image)
    db.session.commit()

    return jsonify({'message': 'Imagem salva com sucesso', 'CODE': 'SUCCESS'}), 200
