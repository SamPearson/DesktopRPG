from src.database.base.base_repositories import UserOwnedRepository
from src.database.kaijuchan.kaijuchan_models import Kaijuchan


class KaijuchanRepository(UserOwnedRepository[Kaijuchan]):
    def __init__(self, session):
        super().__init__(session, Kaijuchan)