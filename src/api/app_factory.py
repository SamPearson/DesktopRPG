from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from src.database.db import db
from src.database.users.user_models import BlacklistedToken
from src.database.config_db import DatabaseConfig, initialize_database
from src.api.config.config import Config


def create_app():
    app = Flask(__name__)
    
    # Load API configuration
    app.config.from_object(Config)
    
    # Load Database configuration
    app.config.from_object(DatabaseConfig)

    # Configure CORS
    CORS(app, 
        resources={r"/*": {
            "origins": Config.CORS_ORIGINS,
            "methods": Config.CORS_METHODS,
            "allow_headers": Config.CORS_ALLOW_HEADERS,
            "supports_credentials": Config.CORS_SUPPORTS_CREDENTIALS
        }})

    # Initialize extensions
    db.init_app(app)

    # Initialize JWT
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        token = BlacklistedToken.query.filter_by(jti=jti).first()
        return token is not None

    # Add JWT error handlers
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"msg": "Invalid token"}), 422

    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({"msg": "Missing Authorization Header"}), 422

    with app.app_context():
        initialize_database(app)

    return app
