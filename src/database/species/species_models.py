from sqlalchemy import Column, String, JSON, Integer

from src.database.base.base_models import BaseModel


class Species(BaseModel):
    """
    Static definition of a playable character template.
    """
    __tablename__ = "species"
    __table_args__ = {'extend_existing': True}


    name = Column(String, nullable=False, unique=True, index=True)

    # base stat block (stats at level 1 for this species)
    phys_attack = Column(Integer, nullable=False)
    phys_defense = Column(Integer, nullable=False)
    magic_attack = Column(Integer, nullable=False)
    magic_defense = Column(Integer, nullable=False)
    agility = Column(Integer, nullable=False)
    charisma = Column(Integer, nullable=False)


    # Stat growth rates
    # using a json blob here as the data shape is much more likely to change than base stat data shape.
    growth_rates = Column(JSON, nullable=False)

    # optional: restrict what elemental affinities are allowed
    allowed_elemental_affinities = Column(JSON, nullable=True)

    # optional: default elemental affinities applied on creation
    base_elemental_affinities = Column(JSON, nullable=True)

    # sex-based stat modifiers
    # example:
    # {
    #   "male": {"phys_attack": 2},
    #   "female": {"agility": 2}
    # }
    sex_modifiers = Column(JSON, nullable=True)

    def as_dict(self, user_timezone: str = 'UTC'):
        data = super().as_dict(user_timezone=user_timezone)
        data.update({
            "name": self.name,
            "base_stats": {
                "phys_attack": self.phys_attack,
                "phys_defense": self.phys_defense,
                "magic_attack": self.magic_attack,
                "magic_defense": self.magic_defense,
                "agility": self.agility,
                "charisma": self.charisma
            },
            "allowed_elemental_affinities": self.allowed_elemental_affinities,
            "base_elemental_affinities": self.base_elemental_affinities,
            "sex_modifiers": self.sex_modifiers,
        })
        return data