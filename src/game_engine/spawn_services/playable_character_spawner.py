from src.database.playable_character.playable_character_service import PlayableCharacterService
from src.database.species.species_repository import SpeciesRepository
import random
import logging

logger = logging.getLogger(__name__)


class PlayableCharacterSpawner:
    def __init__(
        self, 
        playable_character_service: PlayableCharacterService,
        species_repo: SpeciesRepository
    ):
        self.pc_service = playable_character_service
        self.species_repo = species_repo

    def generate_playable_character(self, spawn_conditions: dict) -> dict | None:
        """
        Generate a wild encounter based on spawn conditions.
        Returns character data dict or None if spawn failed.
        """
        if not self._validate_spawn_conditions(spawn_conditions):
            logger.error("Invalid spawn conditions")
            return None

        # Determine what should spawn
        species = self._select_species(spawn_conditions)
        if not species:
            logger.debug("No species matched spawn conditions")
            return None

        # Build character data
        char_data = {
            'species_id': species.id,
            'level': self._calculate_level(spawn_conditions, species),
            'sex': self._random_sex(species),
            'personality_type': self._random_personality(),
            'elemental_affinities': self._random_affinities(species),
            'name': None  # Wild encounters have no name
        }

        # Validate through the service
        try:
            return self.pc_service.generate_character(char_data)
        except ValueError as e:
            logger.error(f"Failed to generate valid character: {e}")
            return None

    def _validate_spawn_conditions(self, spawn_conditions: dict) -> bool:
        """Validate that spawn_conditions has required fields."""
        # required = ['location', 'time_of_day']  # adjust as needed
        # return all(k in spawn_conditions for k in required)

        return True

    def _select_species(self, spawn_conditions: dict):
        """
        Select a species based on spawn conditions.
        """
        # Placeholder - just pick one at random
        all_species = self.species_repo.list()
        return random.choice(all_species) if all_species else None

    def _calculate_level(self, spawn_conditions: dict, species) -> int:
        """Calculate level based on area, player level, etc."""
        base_level = spawn_conditions.get('min_level', 1)
        level_range = spawn_conditions.get('level_range', 3)
        return random.randint(base_level, base_level + level_range)

    def _random_sex(self, species) -> str:
        """Randomly select sex (could be weighted or exclusive based on species)."""
        return random.choice(['male', 'female'])

    def _random_personality(self) -> str:
        """Randomly select personality."""
        from src.game_engine.definitions.personalities import PERSONALITY_KEYS
        return random.choice(PERSONALITY_KEYS)

    def _random_affinities(self, species) -> list:
        """Randomly select elemental affinities based on species rules."""
        from src.game_engine.definitions.elements import ELEMENTAL_AFFINITIES
        
        allowed = species.allowed_elemental_affinities or ELEMENTAL_AFFINITIES
        
        # Start with base affinities if defined
        affinities = list(species.base_elemental_affinities or [])
        
        # Randomly add 0-2 affinities (up to max 2 total)
        while len(affinities) < 2 and random.random() < 0.5:
            available = [a for a in allowed if a not in affinities]
            if available:
                affinities.append(random.choice(available))
        
        return affinities