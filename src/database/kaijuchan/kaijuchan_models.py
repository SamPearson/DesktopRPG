from sqlalchemy import Column, Integer, String, ForeignKey, JSON

from src.database.base.base_models import UserOwnedModel


class Kaijuchan(UserOwnedModel):
    """
    A user-owned instance of a species.
    Contains only inputs required for stat calculation and identity.
    """
    __tablename__ = "kaijuchan"

    species_id = Column(Integer, ForeignKey("species.id"), nullable=False, index=True)

    # core identity
    name = Column(String, nullable=True)

    # progression
    level = Column(Integer, nullable=False, default=1)

    # stat inputs
    sex = Column(String, nullable=False)
    personality_type = Column(String, nullable=False)

    # up to 2 affinities
    elemental_affinities = Column(JSON, nullable=False)

    def as_dict(self, user_timezone: str = "UTC"):
        data = super().as_dict(user_timezone=user_timezone)
        data.update({
            "species_id": self.species_id,
            "name": self.name,
            "level": self.level,
            "sex": self.sex,
            "personality_type": self.personality_type,
            "elemental_affinities": self.elemental_affinities,
        })
        return data