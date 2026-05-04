from src.database.kaijuchan.kaijuchan_models import Kaijuchan
from src.database.kaijuchan.kaijuchan_repository import KaijuchanRepository
from src.database.species.species_repository import SpeciesRepository
from src.game_engine.definitions.elements import ELEMENTAL_AFFINITIES
from src.game_engine.definitions.personalities import PERSONALITY_KEYS


class KaijuchanService:
    def __init__(
        self,
        pc_repo: KaijuchanRepository,
        species_repo: SpeciesRepository
    ):
        self.pc_repo = pc_repo
        self.species_repo = species_repo


    def generate_kaijuchan(self, data: dict) -> dict:
        species = self._get_species(data.get("species_id"))


        self._validate_level(data.get("level", 1))
        self._validate_sex(data.get("sex"), species)
        self._validate_personality(data.get("personality_type"))
        self._validate_elemental_affinities(data.get("elemental_affinities"), species)

        payload = {
            "species_id": species.id,
            "species_name": species.name,
            "name": data.get("name"),
            "level": data.get("level", 1),
            "sex": data["sex"],
            "personality_type": data["personality_type"],
            "elemental_affinities": data["elemental_affinities"],
        }

        return payload


    def register_kaijuchan(self, user_id: int, char_data: dict) -> Kaijuchan:

        char_data['user_id'] = user_id

        return self.pc_repo.create(**char_data)

    def create_kaijuchan(self, user_id: int, data: dict) -> Kaijuchan:
        """Generate and persist a kaijuchan in one step."""
        char_data = self.generate_kaijuchan(data)
        return self.register_kaijuchan(user_id, char_data)


    def _get_species(self, species_id: int):
        species = self.species_repo.get(species_id)
        if not species:
            raise ValueError("Invalid species_id")
        return species

    def _validate_level(self, level: int):
        if not isinstance(level, int) or level < 1:
            raise ValueError("Level must be >= 1")

    def _validate_sex(self, sex: str, species):
        if not isinstance(sex, str):
            raise ValueError("Invalid sex")

        # optional: enforce species-specific rules later

    def _validate_personality(self, personality: str):
        if personality not in PERSONALITY_KEYS:
            raise ValueError(f"Invalid personality: {personality}")

    def _validate_elemental_affinities(self, elemental_affinities, species):
        if not isinstance(elemental_affinities, list):
            raise ValueError("Elemental Affinities must be a list")

        if len(elemental_affinities) > 2:
            raise ValueError("Max 2 elemental affinities allowed")

        if len(set(elemental_affinities)) != len(elemental_affinities):
            raise ValueError("Duplicate elemental affinities not allowed")

        for affinity in elemental_affinities:
            if affinity not in ELEMENTAL_AFFINITIES:
                raise ValueError(f"Invalid elemental affinity: {affinity}")

        if species.allowed_elemental_affinities:
            for affinity in elemental_affinities:
                if affinity not in species.allowed_elemental_affinities:
                    raise ValueError(f"{affinity} not allowed for this species")