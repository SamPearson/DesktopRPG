from flask import Blueprint
from . import playable_character_routes

playable_character_bp = Blueprint('playable_character', __name__)

playable_character_bp.add_url_rule('/api/playable_characters/generate', view_func=playable_character_routes.generate_playable_character, endpoint='generate', methods=['GET'])
