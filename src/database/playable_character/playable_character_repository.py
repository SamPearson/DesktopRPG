from src.database.base.base_repositories import UserOwnedRepository
from src.database.playable_character.playable_character_models import PlayableCharacter


class PlayableCharacterRepository(UserOwnedRepository[PlayableCharacter]):
    def __init__(self, session):
        super().__init__(session, PlayableCharacter)