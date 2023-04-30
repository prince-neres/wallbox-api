import spotipy
from flask_cors import cross_origin
from flask import make_response, jsonify
from spotipy.oauth2 import SpotifyClientCredentials
from . import api
from app import Config


@api.route('/tier_phonks', methods=['GET'])
@cross_origin(origins='http://localhost:5173')
def get_top_10_phonks():
    # Autenticar e obter uma chave de acesso da API do Spotify
    client_credentials_manager = SpotifyClientCredentials(
        client_id=Config.SPOTIFY_CLIENT_ID,
        client_secret=Config.SPOTIFY_CLIENT_SECRET
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Pesquisar por um termo ou categoria correspondente ao gênero musical desejado
    results = sp.search(q='genre: phonk', type='track', limit=50)

    # Filtrar os resultados da pesquisa para obter apenas as músicas
    tracks = results.get('tracks').get('items')

    # Ordenar as músicas por popularidade (ou número de reproduções)
    tracks.sort(key=lambda x: x.get('popularity'), reverse=True)

    # Limitar os resultados a apenas 10 músicas
    top_10_tracks = tracks[:10]

    # Guardando músicas em lista e para retornar
    response_tracks = [
        f"{track.get('name')} - {track.get('artists')[0].get('name')}" for track in top_10_tracks]

    if response_tracks:
        return make_response(jsonify(response_tracks), 200)
    else:
        return make_response(jsonify({'message': 'Músicas não encontrada', 'code': 'ERROR'}), 400)
