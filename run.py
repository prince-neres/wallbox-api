from app import create_app, Config

app = create_app()

if __name__ == '__main__':
    app.run(debug=True if Config.ENVIRONMENT == 'development' else False)
