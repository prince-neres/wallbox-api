import uuid
from sqlalchemy import or_
from flask import make_response, jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from . import api
from utils import validate_image, wallpaper_upload_validate, wallpaper_update_validate
from app import db, Config, s3
from models import Wallpaper, User
from schemas import WallpaperSchema, UserSchema


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
    query = request.args.get('query')
    page = request.args.get('page', 1, type=int)
    per_page = 6  # Define quantos itens serão mostrados por página

    # Utiliza join para obter os dados do usuário associado a cada imagem
    wallpapers = db.session.query(Wallpaper, User).join(
        User, Wallpaper.user_id == User.id)

    # Se uma query foi fornecida, filtra por título ou descrição
    if query:
        wallpapers = wallpapers.filter(
            or_(Wallpaper.title.ilike(f'%{query}%'),
                Wallpaper.description.ilike(f'%{query}%'))
        )

    # Pagina os resultados
    wallpapers = wallpapers.paginate(page=page, per_page=per_page)

    wallpapers_list = []

    for wallpaper, user in wallpapers.items:
        user_schema = UserSchema()
        user_json = user_schema.dump(user)

        wallpaper_schema = WallpaperSchema()
        wallpaper_json = wallpaper_schema.dump(wallpaper)

        # Inclui o JSON do usuário dentro do JSON do wallpaper
        wallpaper_json['user'] = user_json
        wallpapers_list.append(wallpaper_json)

    # Calcula o total de resultados e adiciona a informação de hasNextPage e hasPreviousPage
    total_results = wallpapers.total
    has_next_page = (page * per_page) < total_results
    has_previous_page = page > 1
    response_data = {'wallpapers': wallpapers_list,
                     'hasNextPage': has_next_page,
                     'hasPreviousPage': has_previous_page}

    return make_response(jsonify(response_data), 200)


@api.route('/user-wallpapers', methods=['GET'])
@cross_origin(origins=Config.CLIENT_URL)
@jwt_required()
def get_user_wallpapers():
    user_id = get_jwt_identity().get('id')
    page = request.args.get('page', 1, type=int)
    per_page = 6
    query = request.args.get('query')

    user_wallpapers = Wallpaper.query.filter_by(user_id=user_id)

    if query:
        user_wallpapers = user_wallpapers.filter(
            or_(Wallpaper.title.ilike(f'%{query}%'),
                Wallpaper.description.ilike(f'%{query}%'))
        )

    user_wallpapers = user_wallpapers.paginate(page=page, per_page=per_page)
    wallpaper_schema = WallpaperSchema(many=True)
    result = wallpaper_schema.dump(user_wallpapers.items)

    total_results = user_wallpapers.total
    has_next_page = (page * per_page) < total_results
    has_previous_page = page > 1
    response_data = {'wallpapers': result,
                     'hasNextPage': has_next_page,
                     'hasPreviousPage': has_previous_page}

    return make_response(jsonify(response_data), 200)


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

    wallpaper_upload_validate(title, file, description, tags)

    try:
        # Faz o upload do arquivo para o S3
        validate_image(file)
        s3.upload_fileobj(file, Config.AWS_BUCKET_NAME, filename)
        url = f"{Config.AWS_SS3_CUSTOM_DOMAIN}/{filename}"

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
        description=f"Wallpaper com id {id} não encontrado!")
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

    wallpaper_update_validate(title, description, tags)

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
