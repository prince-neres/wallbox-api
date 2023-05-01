import base64
from flask import make_response, jsonify, request, send_file
from flask_cors import cross_origin
from io import BytesIO
from PIL import Image
from . import api
from app import db, Config
from app.models import Wallpaper


@api.route('/wallpapers')
@cross_origin(origins=Config.CLIENT_URL)
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
@cross_origin(origins=Config.CLIENT_URL)
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
@cross_origin(origins=Config.CLIENT_URL)
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
