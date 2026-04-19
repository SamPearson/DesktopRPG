from flask import Blueprint
from . import species_routes

species_bp = Blueprint('species', __name__)

species_bp.add_url_rule('/api/species', view_func=species_routes.list_species, endpoint='list_species', methods=['GET'])
