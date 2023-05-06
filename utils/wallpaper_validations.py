import requests
import json
from flask import jsonify, make_response
from app import Config


def request_to_detect_nsfw_image(image):
    params = {
        'models': 'nudity-2.0,offensive,face-attributes,gore,tobacco',
        'api_user': Config.SIGHTENGINE_API_USER,
        'api_secret': Config.SIGHTENGINE_API_SECRET
    }
    files = {'media': image}
    r = requests.post(
        Config.SIGHTENGINE_API, files=files, data=params)

    output = json.loads(r.text)

    return output


def validate_nsfw_in_image(output,
                           gore_threshold=0.1,
                           nudity_threshold=0.1,
                           offensive_threshold=0.1,
                           tobacco_threshold=0.1
                           ):
    """
    Valida um JSON de detecção de imagem para verificar se a imagem contém conteúdo impróprio.

    Parâmetros:
    output (dict): O JSON de detecção de imagem.
    gore_threshold (float): O limite de probabilidade para o campo "gore".
    nudity_threshold (float): O limite de probabilidade para os campos "erotica", "sexual_activity" e "sexual_display" em "nudity".
    offensive_threshold (float): O limite de probabilidade para os campos "confederate", "middle_finger", "nazi", "supremacist" e "terrorist" em "offensive".
    tobacco_threshold (float): O limite de probabilidade para o campo "tobacco".

    Retorna:
    bool: True se a imagem é considerada segura, False caso contrário.
    """

    if output["gore"]["prob"] >= gore_threshold:
        return False

    nudity_prob = max(output["nudity"]["erotica"], output["nudity"]
                      ["sexual_activity"], output["nudity"]["sexual_display"])
    if nudity_prob >= nudity_threshold:
        return False

    offensive_prob = max(output["offensive"][key]
                         for key in output["offensive"].keys() if key != "prob")
    if offensive_prob >= offensive_threshold:
        return False

    if output["tobacco"]["prob"] >= tobacco_threshold:
        return False

    return True


def validate_image(file):
    # Valida se há conteúdo NSFW na imagem
    result_detected_image = request_to_detect_nsfw_image(file)
    is_safe = validate_nsfw_in_image(result_detected_image)
    if not is_safe:
        error_data = {
            'message': 'Conteúdo inadequado detectado na imagem',
            'code': 'NSFW_DETECTED'
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


def wallpaper_upload_validate(title, file, description, tags):
    # Valida se campos foram preenchidos
    if not title or not file or not description or not tags:
        error_data = {
            'message': 'O campo título, descrição, tags e a anexação da imagem precisam ser preenchidos',
            'code': 'INVALID_FILE_EXTENSION'
        }
        return make_response(jsonify(error_data), 400)


def wallpaper_update_validate(title, description, tags):
    if not title or not description or not tags:
        error_data = {
            'message': 'O campo título, descrição e tags precisam ser preenchidos',
            'code': 'INVALID_DATA'
        }
        return make_response(jsonify(error_data), 400)
