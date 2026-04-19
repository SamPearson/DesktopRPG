from src.database.base.base_repositories import BaseRepository
from src.database.species.species_models import Species


class SpeciesRepository(BaseRepository[Species]):
    def __init__(self, session):
        super().__init__(session, Species)