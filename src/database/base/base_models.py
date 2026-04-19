from typing import Any, Dict

from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship, backref

from src.database.db import db



class BaseModel(db.Model):
    """
    Abstract base class for all models.
    Provides common fields and functionality.
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True)

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name automatically from class name."""
        return cls.__name__.lower()

    def as_dict(self, user_timezone: str = 'UTC') -> Dict[str, Any]:
        """
        Convert model to dictionary representation.
        """

        return {
            'id': self.id,
        }

class UserOwnedModel(BaseModel):
    """
    Abstract base class for models owned by a user.
    Provides user relationship and ownership validation.
    """
    __abstract__ = True

    @declared_attr
    def user_id(cls):
        return Column(Integer, db.ForeignKey('user.id'), nullable=False, index=True)

    @declared_attr
    def user(cls):
        return relationship(
            "User",
            backref=backref(
                f'{cls.__tablename__}_list',
                cascade="all, delete-orphan"
            )
        )


    def as_dict(self, user_timezone: str = 'UTC') -> Dict[str, Any]:
        """
        Convert model to dictionary representation including user_id.
        
        Args:
            user_timezone: User's timezone for timestamp conversion (IANA format)
        """
        data = super().as_dict(user_timezone=user_timezone)
        data['user_id'] = self.user_id
        return data

