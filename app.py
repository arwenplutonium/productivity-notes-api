from flask import Flask

from backend.config import config
from backend.extensions import api, bcrypt, db, jwt, migrate
from backend.routes import (
    LoginResource,
    MeResource,
    NoteDetailResource,
    NotesListResource,
    SignupResource,
)


def create_app(config_name='development'):
    """Build the Flask app. The config name lets the tests swap in an
    in-memory database without touching the development one."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)

    # Flask-JWT-Extended returns its own error shape by default, so these
    # handlers are overridden to match the JSON the rest of the API returns.
    @jwt.unauthorized_loader
    def handle_missing_token(error):
        return {"error": "missing or invalid authorization token"}, 401

    @jwt.invalid_token_loader
    def handle_invalid_token(error):
        return {"error": "missing or invalid authorization token"}, 401

    @jwt.expired_token_loader
    def handle_expired_token(jwt_header, jwt_payload):
        return {"error": "token has expired"}, 401

    api.add_resource(SignupResource, '/signup')
    api.add_resource(LoginResource, '/login')
    api.add_resource(MeResource, '/me')
    api.add_resource(NotesListResource, '/notes')
    api.add_resource(NoteDetailResource, '/notes/<int:note_id>')

    @app.get('/')
    def health_check():
        return {"message": "Productivity API is running"}

    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True)
