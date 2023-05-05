from flask import make_response, jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt_identity
from os import getenv
from datetime import datetime
from . import api
from ..validations import detect_nsfw_image, validate_image
from app import db, Config, s3
from app.models import Wallpaper, User
from app.schemas import WallpaperSchema, UserSchema
import uuid


@api.route('/wallpaper/<int:id>', methods=['GET'])
@jwt_required()
@cross_origin(origins=Config.CLIENT_URL)
def get_wallpaper(id):
    wallpaper = Wallpaper.query.filter_by(id=id).first_or_404(
        description=f"Wallpaper with id {id} not found")
    wallpaper_schema = WallpaperSchema()
    result = wallpaper_schema.dump(wallpaper)
    return make_response(jsonify(result), 200)


@api.route('/wallpapers', methods=['GET'])
@cross_origin(origins=Config.CLIENT_URL)
def get_wallpapers():
    # Utiliza join para obter os dados do usuário associado a cada imagem
    wallpapers = db.session.query(Wallpaper, User).join(
        User, Wallpaper.user_id == User.id).all()

    wallpapers_list = []

    for wallpaper, user in wallpapers:
        user_schema = UserSchema()
        user_json = user_schema.dump(user)

        wallpaper_schema = WallpaperSchema()
        wallpaper_json = wallpaper_schema.dump(wallpaper)

        # Inclui o JSON do usuário dentro do JSON do wallpaper
        wallpaper_json['user'] = user_json

        wallpapers_list.append(wallpaper_json)

    return make_response(jsonify(wallpapers_list), 200)


@api.route('/user-wallpapers', methods=['GET'])
@cross_origin(origins=Config.CLIENT_URL)
@jwt_required()
def get_user_wallpapers():
    user_id = get_jwt_identity().get('id')
    user_wallpapers = Wallpaper.query.filter_by(user_id=user_id).all()
    wallpaper_schema = WallpaperSchema(many=True)
    result = wallpaper_schema.dump(user_wallpapers)
    return make_response(jsonify(result), 200)


@api.route('/upload_wallpaper', methods=['POST'])
@jwt_required()
@cross_origin(origins=Config.CLIENT_URL)
def upload_image():
    user = get_jwt_identity()
    form_data = request.form
    file = request.files['image']
    title = form_data.get('title')
    tags = eval(form_data.get('tags'))
    description = form_data.get('description')
    uuid_code = str(uuid.uuid4())
    filename = f'{uuid_code}-{file.filename.strip()}'

    # Valida se há conteúdo NSFW na imagem
    result_detected_image = detect_nsfw_image(file)
    is_safe = validate_image(result_detected_image)
    if not is_safe:
        error_data = {
            'message': 'Conteúdo inadequado detectado na imagem',
            'code': 'NSFW_DETECTED'
        }
        return make_response(jsonify(error_data), 400)

    # Valida se campos foram preenchidos
    if not title or not file or not description or not tags:
        error_data = {
            'message': 'O campo título, descrição, tags e a anexação da imagem precisam ser preenchidos',
            'code': 'INVALID_FILE_EXTENSION'
        }
        return make_response(jsonify(error_data), 400)

    # Verifica tamanho do arquivo
    max_image_size = 10 * 1024 * 1024  # 10 MB
    if len(file.read()) > max_image_size:
        error_data = {
            'message': 'Tamanho da imagem excedido',
            'code': 'INVALID_SIZE_IMAGE'
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

        # Cria os objetos de schema e faz o dump dos dados
        wallpaper_schema = WallpaperSchema()
        wallpaper_data = wallpaper_schema.dump(new_wallpaper)

        return make_response(jsonify(wallpaper_data), 201)
    except:
        # Erro genérico
        error_data = {
            'message': 'Erro ao tentar criar imagem',
            'code': 'ERROR'
        }
        return make_response(jsonify(error_data), 500)


@api.route('/wallpaper/<int:id>', methods=['DELETE'])
@jwt_required()
@cross_origin(origins=Config.CLIENT_URL)
def delete_wallpaper(id):
    wallpaper = Wallpaper.query.filter_by(id=id).first_or_404(
        description=f"Wallpaper with id {id} not found")
    db.session.delete(wallpaper)
    db.session.commit()
    return make_response(jsonify({'message': 	'Wallpaper deletado com sucesso!', 'code': 'SUCCESS'}), 200)


@api.route('/wallpaper/<int:id>', methods=['PUT'])
@jwt_required()
@cross_origin(origins=Config.CLIENT_URL)
def update_wallpaper(id):
    # Obtém dados da requisição
    user = get_jwt_identity()
    form_data = request.form
    title = form_data.get('title')
    tags = eval(form_data.get('tags'))
    description = form_data.get('description')

    # Valida se campos foram preenchidos
    if not title or not description or not tags:
        error_data = {
            'message': 'O campo título, descrição e tags precisam ser preenchidos',
            'code': 'INVALID_DATA'
        }
        return make_response(jsonify(error_data), 400)

    # Verifica se o wallpaper existe
    wallpaper = Wallpaper.query.filter_by(id=id).first_or_404(
        description=f"Wallpaper with id {id} not found")

    # Verifica se o usuário é dono do wallpaper
    if wallpaper.user_id != user.get('id'):
        error_data = {
            'message': 'Usuário não autorizado a atualizar este wallpaper',
            'code': 'UNAUTHORIZED'
        }
        return make_response(jsonify(error_data), 401)

    # Atualiza informações do wallpaper
    wallpaper.title = title
    wallpaper.description = description
    wallpaper.tags = tags
    wallpaper.date_updated = datetime.now()
    db.session.commit()

    # Cria o objeto de retorno
    wallpaper_schema = WallpaperSchema()
    data = wallpaper_schema.dump(wallpaper)

    return make_response(jsonify(data), 200)
