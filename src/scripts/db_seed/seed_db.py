from src.database.db import db
from src.database.species.species_repository import SpeciesRepository
from src.scripts.db_seed.species_seeds import EXAMPLE_SPECIES

def seed_species():
    """Seed the database with initial species data"""
    repo = SpeciesRepository(db.session)
    for spec in EXAMPLE_SPECIES:
        existing = repo.list(name=spec["name"])
        if existing:
            continue  # skip duplicates
        repo.create(**spec)
    db.session.commit()  # Ensure all changes are committed

if __name__ == "__main__":
    # This allows manual seeding if needed
    from src.api.app_factory import create_app
    app = create_app()
    with app.app_context():
        seed_species()
        print("Species seeded successfully.")