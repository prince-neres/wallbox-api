from flask import make_response, jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt_identity
from os import getenv
from . import api
from app import db, Config, s3
from app.models import Wallpaper, User
import uuid


@api.route('/upload_wallpaper', methods=['POST'])
@jwt_required()
@cross_origin(origins=Config.CLIENT_URL)
def upload_image():
    # Obtém dados da requisição
    user = get_jwt_identity()
    form_data = request.form
    file = request.files['image']
    title = form_data.get('title')
    tags = form_data.get('tags').split('/')
    description = form_data.get('description')
    uuid_code = str(uuid.uuid4())
    filename = f'{uuid_code}-{file.filename.strip()}'

    # Verifica tamanho do arquivo
    max_image_size = 10 * 1024 * 1024  # 10 MB
    if len(file.read()) > max_image_size:
        error_data = {
            'message': 'Tamanho da imagem excedido',
            'code': 'ERROR'
        }
        return make_response(jsonify(error_data), 400)
    file.seek(0)

    # Verifica a extensão do arquivo
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if not '.' in file.filename or file.filename.split('.')[-1].lower() not in allowed_extensions:
        error_data = {
            'message': 'O arquivo precisa ter uma extensão válida (png, jpg, jpeg ou gif)',
            'code': 'INVALID_FILE_EXTENSION'
        }
        return make_response(jsonify(error_data), 400)

    try:
        # Faz o upload do arquivo para o S3
        s3.upload_fileobj(file, getenv('AWS_BUCKET_NAME'), filename)
        url = f"{getenv('AWS_SS3_CUSTOM_DOMAIN')}/{filename}"

        # Adicionar imagem no banco
        new_wallpaper = Wallpaper(
            user_id=user.get('id'), title=title, description=description, filename=filename, image=url, tags=tags)
        db.session.add(new_wallpaper)
        db.session.commit()
        data = {
            'id': new_wallpaper.id,
            'title': new_wallpaper.title,
            'description': new_wallpaper.description,
            'tags': new_wallpaper.tags,
            'filename': new_wallpaper.filename,
            'image': new_wallpaper.image,
            'date_created': new_wallpaper.date_created,
            'date_updated': new_wallpaper.date_updated,
        }
        return make_response(jsonify(data), 201)
    except:
        # Erro genérico
        error_data = {
            'message': 'Erro ao tentar criar imagem',
            'code': 'ERROR'
        }
        return make_response(jsonify(error_data), 500)


@api.route('/wallpapers', methods=['GET'])
@cross_origin(origins=Config.CLIENT_URL)
def get_wallpapers():
    # Utiliza join para obter os dados do usuário associado a cada imagem
    wallpapers = db.session.query(Wallpaper, User).join(
        User, Wallpaper.user_id == User.id).all()

    wallpapers_list = []
    for wallpaper, user in wallpapers:
        user_json = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'date_created': user.date_created,
            'date_updated': user.date_updated
        }

        wallpaper_json = {
            'id': wallpaper.id,
            'user': user_json,
            'title': wallpaper.title,
            'description': wallpaper.description,
            'tags': wallpaper.tags,
            'filename': wallpaper.filename,
            'image':  wallpaper.image,
            'date_created': wallpaper.date_created,
            'date_updated': wallpaper.date_updated,
        }

        wallpapers_list.append(wallpaper_json)

    return make_response(jsonify(wallpapers_list), 200)
