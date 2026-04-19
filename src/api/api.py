from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    get_jwt
)


from src.database.config_db import initialize_database
from src.api.app_factory import create_app

from src.api.routes.users import users_bp
from src.api.routes.species import species_bp
from src.api.routes.playable_characters import playable_character_bp

app = create_app()

# Register all blueprints
app.register_blueprint(users_bp)
app.register_blueprint(species_bp)
app.register_blueprint(playable_character_bp)


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200



# Allows starting the server by running this script with the python3 command instead of flask or gunicorn commands
# only do this on local/dev. see README.md for more on server/prod vs local/dev
if __name__ == "__main__":
    app.run(debug=True, port=5050)
