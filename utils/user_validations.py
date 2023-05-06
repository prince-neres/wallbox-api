from flask import make_response, jsonify
from werkzeug.security import check_password_hash


def user_register_validate(username, email, password, confirm_password, user):
    # Verifica se todos os campos estão presentes
    if not username or not email or not password:
        error_data = {
            'message': 'Nome de usuário, email ou senha ausente',
            'code': 'ERROR'
        }
        return make_response(jsonify(error_data), 400)

    # Verifica se a senha e a confirmação são iguais
    if not password == confirm_password:
        error_data = {
            'message': 'As senhas não coi	ncidem',
            'code': 'ERROR'
        }
        return make_response(jsonify(error_data), 400)

    # Verifica se já existe um usuário com o mesmo email
    if user is not None:
        error_data = {
            'message': 'Já existe um usuário com esse email',
            'code': 'ERROR'
        }
        return make_response(jsonify(error_data), 409)


def user_login_validate(email, user, password):
    # Validação de entrada de dados
    if not email or not isinstance(email, str):
        return make_response(jsonify({'message': 'Email inválido', 'code': 'INVALID_EMAIL'}), 400)

    if not password or not isinstance(password, str):
        return make_response(jsonify({'message': 'Senha inválida', 'code': 'INVALID_PASSWORD'}), 400)

    if user is None:
        # Usuário não encontrado
        return make_response(jsonify({'message': 'Email incorreto', 'code': 'USER_NOT_FOUND'}), 404)

    if not check_password_hash(user.password, password):
        # Senha incorreta
        return make_response(jsonify({'message': 'Senha incorreta', 'code': 'INVALID_PASSWORD'}), 401)


def user_update_validate(current_user, id, username):
    if current_user.get('id') != id:
        error_data = {
            'message': 'Sem permissão',
            'code': 'NOT_PERMISSION'
        }
        return make_response(jsonify(error_data), 400)

    if not username:
        error_data = {
            'message': 'O campo usuário precisa ser preenchido',
            'code': 'INVALID_DATA'
        }
        return make_response(jsonify(error_data), 400)
