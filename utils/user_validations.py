from werkzeug.security import check_password_hash


def user_register_validate(username, email, password, confirm_password, user):
    # Verifica se todos os campos estão presentes
    if not username or not email or not password:
        return {
            'message': 'Nome de usuário, email ou senha ausente',
            'code': 'ERROR'
        }

    # Verifica se a senha e a confirmação são iguais
    if not password == confirm_password:
        return {
            'message': 'As senhas não coi	ncidem',
            'code': 'ERROR'
        }

    # Verifica se já existe um usuário com o mesmo email
    if user is not None:
        return {
            'message': 'Já existe um usuário com esse email',
            'code': 'ERROR'
        }

    return None


def user_login_validate(email, password, user):
    # Validação de entrada de dados
    if not email or not isinstance(email, str):
        return {'message': 'Email inválido', 'code': 'INVALID_EMAIL'}
    if not password or not isinstance(password, str):
        return {'message': 'Senha inválida', 'code': 'INVALID_PASSWORD'}

    # Usuário não encontrado
    if user is None:
        return {'message': 'Email incorreto', 'code': 'USER_NOT_FOUND'}

    # Senha incorreta
    if not check_password_hash(user.password, password):
        return {'message': 'Senha incorreta', 'code': 'INVALID_PASSWORD'}

    return None


def user_update_validate(current_user, id, username):
    # Verifica se usuário da requisição é o mesmo a ser atualizado
    if current_user.get('id') != id:
        return {
            'message': 'Sem permissão',
            'code': 'NOT_PERMISSION'
        }

    # Verifica se o nome do usuário foi informado
    if not username:
        return {
            'message': 'O campo usuário precisa ser preenchido',
            'code': 'INVALID_DATA'
        }

    return None
