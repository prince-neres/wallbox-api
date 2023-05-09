from sqlalchemy import or_
from flask import make_response, jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from . import api
from utils import wallpaper_upload_validate, wallpaper_update_validate
from app import db, Config, s3
from models import Wallpaper, User
from schemas import WallpaperSchema, UserSchema
from services import s3_image_upload


@api.route('/wallpaper/<int:id>', methods=['GET'])
@jwt_required()
@cross_origin(origins=Config.CLIENT_URL)
def get_wallpaper(id):
    wallpaper = Wallpaper.query.filter_by(id=id).first_or_404(
        description=f"Wallpaper com id {id} não encontrado!")

    wallpaper_schema = WallpaperSchema()
    serialized_wallpaper = wallpaper_schema.dump(wallpaper)

    return jsonify(serialized_wallpaper), 200


@api.route('/wallpapers', methods=['GET'])
@cross_origin(origins=Config.CLIENT_URL)
def get_wallpapers():
    query = request.args.get('query')
    page = request.args.get('page', 1, type=int)
    per_page = 9  # Define quantos itens serão mostrados por página

    # Utiliza join para obter os dados do usuário associado a cada imagem
    wallpapers = db.session.query(Wallpaper, User).join(
        User, Wallpaper.user_id == User.id)

    # Se uma query foi fornecida, filtra por título ou descrição
    if query:
        wallpapers = wallpapers.filter(
        or_(Wallpaper.title.ilike(f'%{query}%'),
            Wallpaper.description.ilike(f'%{query}%'),
            Wallpaper.tags.any(f'{query}'))
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
    # Obtém o ID do usuário a partir do token JWT
    user_id = get_jwt_identity().get('id')

    # Define a página atual e a quantidade de itens por página
    page = request.args.get('page', 1, type=int)
    per_page = 9

    # Obtém o parâmetro de busca (query) da URL, se houver
    query = request.args.get('query')

    # Cria a query inicial, filtrando por usuário
    user_wallpapers = Wallpaper.query.filter_by(user_id=user_id)

    # Se houver parâmetro de busca, filtra por título ou descrição que contenham o termo
    if query:
        user_wallpapers = user_wallpapers.filter(or_(Wallpaper.title.ilike(f'%{query}%'),
                                                     Wallpaper.description.ilike(f'%{query}%')))

    # Pagina os resultados da query
    user_wallpapers = user_wallpapers.paginate(page=page, per_page=per_page)

    # Faz o dump dos dados usando o schema de Wallpaper
    wallpaper_schema = WallpaperSchema(many=True)
    result = wallpaper_schema.dump(user_wallpapers.items)

    # Cria um objeto de resposta com as informações de paginação
    total_results = user_wallpapers.total
    has_next_page = (page * per_page) < total_results
    has_previous_page = page > 1
    response_data = {'wallpapers': result,
                     'hasNextPage': has_next_page,
                     'hasPreviousPage': has_previous_page}

    # Retorna a resposta em JSON com código HTTP 200 (OK)
    return make_response(jsonify(response_data), 200)


@api.route('/upload_wallpaper', methods=['POST'])
@jwt_required()
@cross_origin(origins=Config.CLIENT_URL)
def upload_wallpaper():
    # Obtém dados da requisição
    user = get_jwt_identity()
    form_data = request.form
    file = request.files.get('image')
    title = form_data.get('title')
    tags = form_data.get('tags')
    description = form_data.get('description')

    # Validar dados do wallpaper
    error = wallpaper_upload_validate(title, file, description, tags)
    if error:
        return make_response(jsonify(error), 400)

    # Realiza upload da imagem para o bucket S3
    try:
        image_url, filename = s3_image_upload(file)
    except Exception as e:
        error_data = {
            'message': f'Erro ao tentar enviar imagem para o bucket S3: {str(e)}',
            'code': 'ERROR'
        }
        return make_response(jsonify(error_data), 500)

    # Cria um novo wallpaper e adiciona ao banco de dados
    new_wallpaper = Wallpaper(
        user_id=user['id'],
        title=title,
        description=description,
        filename=filename,
        image=image_url,
        tags=eval(tags)
    )
    db.session.add(new_wallpaper)
    db.session.commit()

    # Retorna dados do wallpaper criado
    wallpaper_schema = WallpaperSchema()
    wallpaper_data = wallpaper_schema.dump(new_wallpaper)

    return make_response(jsonify(wallpaper_data), 201)


@api.route('/wallpaper/<int:id>', methods=['DELETE'])
@jwt_required()
@cross_origin(origins=Config.CLIENT_URL)
def delete_wallpaper(id):
    # Busca o wallpaper pelo id, ou retorna um erro 404 se não encontrado
    wallpaper = Wallpaper.query.get_or_404(
        id, description=f"Wallpaper com id {id} não encontrado!")

    # Remove o wallpaper do banco de dados
    db.session.delete(wallpaper)
    db.session.commit()

    # Retorna a mensagem de sucesso
    response_data = {
        'message': 'Wallpaper deletado com sucesso!', 'code': 'SUCCESS'}
    return make_response(jsonify(response_data), 200)


@api.route('/wallpaper/<int:id>', methods=['PUT'])
@jwt_required()
@cross_origin(origins=Config.CLIENT_URL)
def update_wallpaper(id):
    user = get_jwt_identity()

    # Obtém os dados da requisição
    form_data = request.form.to_dict(flat=True)
    title = form_data.get('title')
    tags = form_data.get('tags')
    description = form_data.get('description')

    # Verifica se o wallpaper existe
    wallpaper = Wallpaper.query.get_or_404(
        id, description=f"Wallpaper with id {id} not found")

    # Validar dados do Wallpaper
    error = wallpaper_update_validate(
        title, description, tags, wallpaper, user)
    if error:
        return make_response(jsonify(error), 401)

    # Atualiza informações do wallpaper
    wallpaper.title = title
    wallpaper.description = description
    wallpaper.tags = eval(tags)
    wallpaper.date_updated = datetime.now()
    db.session.commit()

    # Retorna o objeto atualizado
    data = WallpaperSchema().dump(wallpaper)
    return make_response(jsonify(data), 200)
