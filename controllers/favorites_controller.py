from flask import jsonify, make_response
from flask_cors import cross_origin
from flask_jwt_extended import get_jwt_identity, jwt_required
from config import Config
from models import Favorite, Wallpaper
from . import api
from app import db


@api.route('/wallpaper/<int:id>/downloads', methods=['POST'])
@cross_origin(origins=Config.CLIENT_URL)
def add_download(id):
    try:
        wallpaper = Wallpaper.query.get_or_404(id)
        wallpaper.increment_download()
        return make_response(jsonify({'message': 'Download adicionado com sucesso!', 'CODE': 'SUCCESS'}), 200)
    except Exception as error:
        return make_response(jsonify({'message': f'Erro ao adicionar download {str(error)}', 'CODE': 'ERROR'}), 500)


@api.route('/wallpaper/user_favorites', methods=['GET'])
@jwt_required()
@cross_origin(origins=Config.CLIENT_URL)
def user_favorites():
    try:
        user_id = get_jwt_identity().get('id')
        user_favorites = Favorite.query.filter_by(user_id=user_id)
        user_favorites = [favorite.wallpaper_id for favorite in user_favorites]
        return make_response(jsonify(user_favorites), 200)
    except Exception as error:
        return make_response(jsonify({'message': f'Erro favoritos não encontrados {str(error)}', 'CODE': 'ERROR'}), 500)


@api.route('/wallpaper/<int:id>/favorite', methods=['POST'])
@jwt_required()
@cross_origin(origins=Config.CLIENT_URL)
def add_favorite(id):
    user_id = get_jwt_identity().get('id')

    already_favorite = Favorite.query.filter_by(
        user_id=user_id, wallpaper_id=id).first()

    if already_favorite:
        return make_response(jsonify({'message': 'Wallpaper já é favorito!', 'CODE': 'ERROR'}), 406)

    wallpaper = Wallpaper.query.get_or_404(id)
    favorite = Favorite(wallpaper_id=wallpaper.id, user_id=user_id)
    favorite.add_favorite()
    return make_response(jsonify({'message': 'Favoritado com sucesso!', 'CODE': 'SUCCESS'}), 200)


@api.route('/wallpaper/<int:id>/disfavor', methods=['DELETE'])
@jwt_required()
@cross_origin(origins=Config.CLIENT_URL)
def favorite_delete(id):
    user_id = get_jwt_identity().get('id')
    favorite = Favorite.query.filter_by(
        user_id=user_id, wallpaper_id=id).first()

    if favorite:
        favorite.remove_favorite()
        return make_response(jsonify({'message': 'Desfavoritado com sucesso!', 'CODE': 'SUCCESS'}), 200)
    return make_response(jsonify({'message': 'Favorito não econtrado', 'CODE': 'ERROR'}), 404)
