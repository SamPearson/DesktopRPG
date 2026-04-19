from flask import jsonify

from src.database.playable_character.playable_character_service import PlayableCharacterService
from src.database.playable_character.playable_character_repository import PlayableCharacterRepository
from src.game_engine.spawn_services.playable_character_spawner import PlayableCharacterSpawner
from flask_jwt_extended import jwt_required
from src.database.db import db
from src.database.species.species_repository import SpeciesRepository

pc_service = PlayableCharacterService(
    PlayableCharacterRepository(db.session),
    SpeciesRepository(db.session)
)

pc_spawner = PlayableCharacterSpawner(pc_service, SpeciesRepository(db.session))


@jwt_required()
def generate_playable_character():
    char = pc_spawner.generate_playable_character({})
    return jsonify(char)