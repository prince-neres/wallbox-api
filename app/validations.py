import requests
import json
from os import getenv


def detect_nsfw_image(image):
    params = {
        'models': 'nudity-2.0,offensive,face-attributes,gore,tobacco',
        'api_user': getenv('SIGHTENGINE_API_USER'),
        'api_secret': getenv('SIGHTENGINE_API_SECRET')
    }
    files = {'media': image}
    r = requests.post(
        getenv('SIGHTENGINE_API'), files=files, data=params)

    output = json.loads(r.text)

    return output


def validate_image(output, gore_threshold=0.1, nudity_threshold=0.1, offensive_threshold=0.1, tobacco_threshold=0.1):
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
