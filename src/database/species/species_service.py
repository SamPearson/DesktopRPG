from src.database.species.species_models import Species
from src.database.species.species_repository import SpeciesRepository
from src.game_engine.definitions.stats import STAT_KEYS
from src.game_engine.definitions.elements import ELEMENTAL_AFFINITIES

class SpeciesService:
    def __init__(self, repo: SpeciesRepository):
        self.repo = repo

    def list_species(self):
        """List all species"""
        return self.repo.list()


    def get_species(self, species_id: int) -> Species:
        """Get a specific species"""
        return self.repo.get(species_id)


    def create_species(self, data: dict) -> Species:
        self._validate_base_stats(data)
        self._validate_growth_rates(data.get("growth_rates"))
        self._validate_elemental_affinities(data.get("elemental_affinities", []))

        return self.repo.create(**data)

    def _validate_base_stats(self, data: dict):
        for stat in STAT_KEYS:
            if stat not in data:
                raise ValueError(f"Missing stat: {stat}")
            if not isinstance(data[stat], int):
                raise ValueError(f"{stat} must be int")
            if data[stat] < 0:
                raise ValueError(f"{stat} must be non-negative")

    def _validate_growth_rates(self, growth_rates: dict):
        if not isinstance(growth_rates, dict):
            raise ValueError("growth_rates must be a dict")

        for key, value in growth_rates.items():
            if not isinstance(value, (int, float)):
                raise ValueError(f"growth rate for {key} must be numeric")
            if value <= 0:
                raise ValueError(f"growth rate for {key} must be > 0")


    def _validate_elemental_affinities(self, affinities):
        for affinity in affinities:
            if affinity not in ELEMENTAL_AFFINITIES:
                raise ValueError(f"Invalid elemental affinity: {affinity}")