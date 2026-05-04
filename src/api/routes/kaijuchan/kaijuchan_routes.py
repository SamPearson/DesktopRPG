from flask import jsonify
from src.database.kaijuchan.kaijuchan_service import KaijuchanService
from src.database.kaijuchan.kaijuchan_repository import KaijuchanRepository
from src.game_engine.spawn_services.kaijuchan_spawner import KaijuchanSpawner
from flask_jwt_extended import jwt_required
from src.database.db import db
from src.database.species.species_repository import SpeciesRepository

pc_service = KaijuchanService(
    KaijuchanRepository(db.session),
    SpeciesRepository(db.session)
)

pc_spawner = KaijuchanSpawner(pc_service, SpeciesRepository(db.session))


@jwt_required()
def generate_kaijuchan():
    char = pc_spawner.generate_kaijuchan({})
    return jsonify(char)