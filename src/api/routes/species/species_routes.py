from flask import jsonify
from flask_jwt_extended import jwt_required
from src.database.species.species_service import SpeciesService
from src.database.species.species_repository import SpeciesRepository
from src.database.db import db

# Create a single instance of the service
species_service = SpeciesService(SpeciesRepository(db.session))


@jwt_required()
def list_species():
    """List all species"""
    species_list = species_service.list_species()
    return jsonify([species.as_dict() for species in species_list])