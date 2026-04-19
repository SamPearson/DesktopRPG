# Database Layer

## Overview

The database layer follows a three-tier architecture separating concerns between data structure, data access, and business logic:

- **Models**: Define database schema and ORM mappings (SQLAlchemy)
- **Repositories**: Provide CRUD operations for database access
- **Services**: Implement validation and business logic

**Golden Rule**: API routes should never access repositories directly. Always go through the service layer.

## Directory Structure

    database/
    ├── base/
    │   ├── base_models.py       # Abstract base classes for models
    │   ├── repositories.py      # Generic repository implementations
    │   └── exceptions.py        # Custom database exceptions
    ├── config_db.py             # Database configuration and initialization
    ├── db.py                    # SQLAlchemy instance
    ├── users/
    │   ├── user_models.py
    │   ├── user_repository.py
    │   └── user_service.py
    ├── species/
    │   ├── species_models.py
    │   ├── species_repository.py
    │   └── species_service.py
    └── playable_character/
        ├── playable_character_models.py
        ├── playable_character_repository.py
        └── playable_character_service.py

## Core Concepts

### Models

Models define the database schema using SQLAlchemy ORM. All models inherit from one of two base classes:

#### BaseModel

Use for shared resources that are not owned by individual users.

Example:

    from src.database.base.base_models import BaseModel

    class Species(BaseModel):
        __tablename__ = "species"
        name = Column(String, nullable=False, unique=True)
        # ... additional fields

**Provides:**
- Auto-generated `id` (primary key)
- Auto-generated `__tablename__` from class name
- `as_dict()` method for JSON serialization

**Use for**: Species, game configurations, shared reference data

#### UserOwnedModel

Use for user-scoped resources that belong to a specific user.

Example:

    from src.database.base.base_models import UserOwnedModel

    class PlayableCharacter(UserOwnedModel):
        __tablename__ = "playable_character"
        name = Column(String, nullable=True)
        # ... additional fields

**Provides:**
- Everything from `BaseModel`
- `user_id` foreign key (indexed)
- `user` relationship for accessing the owner
- Automatic bidirectional relationship with cascade deletion
- Extended `as_dict()` including `user_id`

**Bidirectional Access:**
- From entity to user: `playable_character.user`
- From user to entities: `user.playable_character_list`

**Cascade Deletion:** When a user is deleted, all their owned entities are automatically deleted.

**Use for**: PlayableCharacter, user inventory, user progress data

#### JSON Fields

For flexible or evolving data structures, use JSON columns:

    growth_rates = Column(JSON, nullable=False)
    elemental_affinities = Column(JSON, nullable=True)

JSON fields allow schema flexibility without migrations but should be validated in the service layer.

### Repositories

Repositories provide CRUD operations only. No validation, no business logic.

#### BaseRepository[T]

Generic repository for shared resources.

Example:

    from src.database.base.repositories import BaseRepository

    class SpeciesRepository(BaseRepository[Species]):
        def __init__(self, session):
            super().__init__(session, Species)

**Provides:**
- `get(id)` - Retrieve by ID
- `list(**filters)` - List all matching filters
- `create(**data)` - Create new record
- `update(instance, **data)` - Update existing record
- `delete(instance)` - Delete record

#### UserOwnedRepository[T]

Repository for user-scoped resources with additional user filtering.

Example:

    from src.database.base.repositories import UserOwnedRepository

    class PlayableCharacterRepository(UserOwnedRepository[PlayableCharacter]):
        def __init__(self, session):
            super().__init__(session, PlayableCharacter)

**Provides:**
- Everything from `BaseRepository`
- `get(id, user_id)` - Retrieve by ID and user
- `list_for_user(user_id, **filters)` - List all for specific user

#### When to Extend

Most repositories can use the base implementation as-is (see `SpeciesRepository`). Only extend when you need domain-specific queries:

    class SpeciesRepository(BaseRepository[Species]):
        def __init__(self, session):
            super().__init__(session, Species)
        
        def list_by_elemental_affinity(self, affinity: str):
            """Get all species with a specific elemental affinity"""
            return self.session.query(self.model_class).filter(
                self.model_class.base_elemental_affinities.contains(affinity)
            ).all()

### Services

Services implement validation and business logic. All external access (API routes) must go through services.

Example:

    class SpeciesService:
        def __init__(self, repo: SpeciesRepository):
            self.repo = repo
        
        def create_species(self, data: dict) -> Species:
            # Validate data
            self._validate_base_stats(data)
            self._validate_growth_rates(data.get("growth_rates"))
            
            # Use repository for persistence
            return self.repo.create(**data)

**Responsibilities:**
- Input validation
- Business rule enforcement
- Data transformation
- Orchestrating multiple repositories (when needed)
- Raising meaningful exceptions

**Not responsible for:**
- Database operations (delegate to repository)
- HTTP concerns (handled by API layer)
- Authentication (handled by API middleware)

## Adding a New Entity

Follow these steps to add a new database entity (e.g., `Item`):

### 1. Create Directory Structure

    database/items/
    ├── __init__.py
    ├── item_models.py
    ├── item_repository.py
    └── item_service.py

**Note**: Use the entity name prefix (e.g., `item_`) to avoid confusion when working with multiple model files.

### 2. Define Model

Choose `BaseModel` or `UserOwnedModel` based on ownership:

    # database/items/item_models.py
    from src.database.base.base_models import UserOwnedModel
    from sqlalchemy import Column, String, Integer, JSON

    class Item(UserOwnedModel):
        __tablename__ = "item"
        
        name = Column(String, nullable=False)
        quantity = Column(Integer, nullable=False, default=1)
        metadata = Column(JSON, nullable=True)
        
        def as_dict(self, user_timezone: str = 'UTC'):
            data = super().as_dict(user_timezone=user_timezone)
            data.update({
                "name": self.name,
                "quantity": self.quantity,
                "metadata": self.metadata
            })
            return data

**Automatic relationships:** By inheriting from `UserOwnedModel`, you automatically get:
- `item.user` - access the owning user
- `user.item_list` - access all items for a user
- Cascade deletion when user is deleted

**No additional configuration needed in the User model!**

### 3. Create Repository

Start with the base implementation:

    # database/items/item_repository.py
    from src.database.base.repositories import UserOwnedRepository
    from src.database.items.item_models import Item

    class ItemRepository(UserOwnedRepository[Item]):
        def __init__(self, session):
            super().__init__(session, Item)

### 4. Implement Service

Add validation and business logic:

    # database/items/item_service.py
    from src.database.items.item_models import Item
    from src.database.items.item_repository import ItemRepository

    class ItemService:
        def __init__(self, repo: ItemRepository):
            self.repo = repo
        
        def create_item(self, user_id: int, data: dict) -> Item:
            self._validate_quantity(data.get("quantity", 1))
            data["user_id"] = user_id
            return self.repo.create(**data)
        
        def _validate_quantity(self, quantity: int):
            if not isinstance(quantity, int) or quantity < 1:
                raise ValueError("Quantity must be a positive integer")

### 5. Register in Database Initialization

Import the model in `config_db.py` to ensure tables are created:

    # Add to imports
    from src.database.items.item_models import Item

### 6. Create Seeds (if applicable)

For shared reference data, add seed scripts in `scripts/db_seed/`.

## Existing Entities

See [ENTITIES.md](./ENTITIES.md) for detailed documentation of each entity in the system.

**Current entities:**
- **Users** - Authentication and user accounts
- **Species** - Shared monster templates
- **PlayableCharacter** - User-owned monster instances

## Database Initialization

### Configuration

Database settings are defined in `database/config_db.py`:
- Database URI (defaults to SQLite in `instance/desktop_rpg.db`)
- SQLAlchemy configuration

**Note**: API configuration (JWT, CORS) lives in `api/config/config.py`.

### Initialization Flow

1. App factory calls `initialize_database(app)`
2. All tables are created via `db.create_all()`
3. If database is new (no existing tables), seed data is loaded
4. Seed scripts in `scripts/db_seed/` populate initial data

### Seeding

Seed scripts run automatically on first initialization. To manually seed:

    python3 src/scripts/db_seed/seed_db.py

Seed scripts check for duplicates and skip existing records.

## Best Practices

### DO

- Inherit from `BaseModel` or `UserOwnedModel`
- Use repositories through services only
- Validate all inputs in the service layer
- Use JSON columns for flexible/evolving data
- Implement `as_dict()` for all models
- Add database indexes for foreign keys and commonly queried fields

### DON'T

- Access repositories directly from API routes
- Put business logic in repositories
- Skip input validation
- Return model instances directly to API (use `as_dict()`)
- Store sensitive data in JSON fields without encryption
- Create circular dependencies between entities

## Troubleshooting

### Tables Not Created

Check that models are imported in `config_db.py` or referenced by imported models.

### Seed Data Not Loading

Verify `initialize_database()` detects a new database (checks for zero existing tables).

### Cascade Deletion Issues

Ensure user-owned entities inherit from `UserOwnedModel`. The cascade deletion is handled automatically through the base class relationship.

## Future Considerations

- Migration strategy (Alembic) when schema changes become frequent
- Soft deletes for audit trails
- Database connection pooling for production
- Read replicas for scaling