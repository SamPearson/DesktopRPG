from flask import Blueprint
from . import kaijuchan_routes

kaijuchan_bp = Blueprint('kaijuchan', __name__)

kaijuchan_bp.add_url_rule('/api/kaijuchan/generate', view_func=kaijuchan_routes.generate_kaijuchan, endpoint='generate', methods=['GET'])
