# Endpoints da API;

A seguir, estão listados os endpoints disponíveis nesta API, juntamente com sua descrição, método aceito e payload:

## Usuários:

### Atualizar Usuário

```
/user/<int:id> [PUT]
```

Este endpoint permite atualizar as informações de um usuário existente. É necessário que o usuário autenticado possua permissão para editar o usuário em questão.

### Payload

Os dados a serem atualizados devem ser enviados através de um formulário (`multipart/form-data`). O campo `image` é opcional e deve conter um arquivo de imagem.

| Campo      | Tipo     | Descrição                                                               |
| ---------- | -------- | ----------------------------------------------------------------------- |
| `username` | `string` | Nome de usuário do usuário.                                             |
| `image`    | `file`   | (Opcional) Arquivo de imagem representando a foto de perfil do usuário. |

### Registrar Novo Usuário

```
/register [POST]
```

Este endpoint permite criar um novo usuário na aplicação.

### Payload

Os dados do novo usuário devem ser enviados em formato JSON no corpo da requisição.

| Campo              | Tipo     | Descrição                                     |
| ------------------ | -------- | --------------------------------------------- |
| `username`         | `string` | Nome de usuário do usuário a ser criado.      |
| `email`            | `string` | Endereço de e-mail do usuário a ser criado.   |
| `password`         | `string` | Senha do usuário a ser criado.                |
| `confirm_password` | `string` | Confirmação da senha do usuário a ser criado. |

### Login de Usuário

```
/login [POST]
```

Este endpoint permite autenticar um usuário na aplicação.

### Payload

Os dados de login devem ser enviados em formato JSON no corpo da requisição.

| Campo      | Tipo     | Descrição                                        |
| ---------- | -------- | ------------------------------------------------ |
| `email`    | `string` | Endereço de e-mail do usuário a ser autenticado. |
| `password` | `string` | Senha do usuário a ser autenticado.              |

Nota: Todos os endpoints desta API são acessíveis apenas por usuários autenticados, que devem enviar um token JWT válido no cabeçalho `Authorization` da requisição.

## Wallpapers:

### Obter Wallpapers

```
/wallpapers [GET]
```

Este endpoint permite obter uma lista de wallpapers. Os resultados podem ser paginados e filtrados por uma string de busca.

### Parâmetros

Os parâmetros de busca podem ser passados como query string.

| Campo   | Tipo     | Descrição                                                                                                   |
| ------- | -------- | ----------------------------------------------------------------------------------------------------------- |
| `query` | `string` | (Opcional) String para busca nos campos `title` e `description` dos wallpapers.                             |
| `page`  | `int`    | (Opcional) Página dos resultados. Começa do valor `1` e cada página contém 6 wallpapers. Valor padrão: `1`. |

### Obter Wallpapers do Usuário

```
/user-wallpapers [GET]
```

Este endpoint permite obter uma lista de wallpapers criados por um usuário específico. É necessário que o usuário autenticado seja o mesmo que está sendo consultado, o payload é o mesmo para o endpoint de obter wallpapers.

### Atualizar Wallpaper

```
/wallpaper/<int:id> [PUT]
```

Este endpoint permite atualizar as informações de um wallpaper existente. É necessário que o usuário autenticado seja o mesmo que criou o wallpaper em questão.

### Payload

Os dados a serem atualizados devem ser enviados através de um formulário (`multipart/form-data`).

| Campo         | Tipo               | Descrição                                          |
| ------------- | ------------------ | -------------------------------------------------- |
| `title`       | `string`           | (Opcional) Título do wallpaper.                    |
| `description` | `string`           | (Opcional) Descrição do wallpaper.                 |
| `tags`        | `array de strings` | (Opcional) lista de tags relacionadas ao wallpaper |

## Criar novo Wallpaper

```
/wallpapers [POST]
```

Este endpoint permite criar um novo wallpaper.

### Payload

Os dados do novo wallpaper devem ser enviados através de um formulário (`multipart/form-data`).

| Campo         | Tipo               | Descrição                                          |
| ------------- | ------------------ | -------------------------------------------------- |
| `title`       | `string`           | Título do wallpaper.                               |
| `tags`        | `array de strings` | (Opcional) lista de tags relacionadas ao wallpaper |
| `description` | `string`           | Descrição do wallpaper.                            |
| `image`       | `file`             | Arquivo de imagem representando o wallpaper.       |

## Remover Wallpaper

```
/wallpaper/<int:id> [DELETE]
```

Este endpoint remover um wallpaper.

### Parâmetro

ID do wallpaper
