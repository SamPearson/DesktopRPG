
# Game Engine

## Overview

The game engine handles **procedural generation** and **game mechanics**. It sits between the API layer and database layer, generating game content and applying game rules before data is validated and persisted.

**Core Purpose**: Transform high-level game events into concrete data through algorithms, randomization, and game rules.

## Architecture
    ↓ API Route ↓ 
    ↓ Game Engine Service (procedural generation & mechanics) ↓
    ↓ Database Service (validation & persistence) ↓
    Database Repository (CRUD operations)


**Example Flow:**
1. Player triggers encounter → API calls game engine
2. Spawner generates random character attributes (level, sex, stats, affinities)
3. Database service validates the generated data is legal
4. Repository saves to database

## Directory Structure

    game_engine/
    ├── definitions/
    │   ├── elements.py          # Elemental affinity types
    │   ├── personalities.py     # Personality types
    │   └── stats.py             # Stat attribute names
    └── spawn_services/
        └── kaijuchan_spawner.py

## Core Concepts

### Definitions

Definitions provide reference data and constants used throughout the game engine and database validation.

**Purpose:**
- Centralize game constants
- Provide enums for validation
- Enable consistent randomization

**Examples:**

**Stats** (`stats.py`):

    STAT_KEYS = [
        "phys_attack",
        "phys_defense",
        "magic_attack",
        "magic_defense",
        "agility",
        "charisma",
    ]

**Elements** (`elements.py`):

    ELEMENTAL_AFFINITIES = [
        "fire",
        "water",
        "earth",
        "plant",
        "air",
        "light",
        "dark"
    ]

**Personalities** (`personalities.py`):

    PERSONALITY_KEYS = [
        "Bold",
        "Shy",
        "Spiritual"
    ]

**When to add definitions:**
- Game-wide constants that don't change
- Enums for randomization or validation
- Reference lists used across multiple systems

### Services

Game engine services implement procedural generation and game mechanics.

**Key Characteristics:**
- Take high-level inputs (spawn conditions, combat actions, etc.)
- Apply game rules and algorithms
- Generate concrete, ready-to-validate data
- Pass results to database services

**Current Services:**

#### KaijuchanSpawner

Handles wild encounter generation.

**Input:** Spawn conditions (location, difficulty, etc.)  
**Process:** 
- Selects appropriate species
- Randomizes sex, personality, elemental affinities
- Calculates level based on conditions
- Generates stat values using growth rates and modifiers

**Output:** Complete character data ready for validation

**Example usage:**

    from src.game_engine.spawn_services.kaijuchan_spawner import KaijuchanSpawner

    spawner = KaijuchanSpawner(kaijuchan_service, species_repo)
    
    spawn_conditions = {
        'min_level': 5,
        'level_range': 3,
        'location': 'forest'
    }
    
    character_data = spawner.generate_kaijuchan(spawn_conditions)

## Responsibilities

### Game Engine DOES

- **Procedural generation** - Randomize attributes, generate encounters
- **Game mechanics** - Apply formulas, calculate derived values
- **Probability & randomness** - Encounter tables, loot drops, critical hits
- **Algorithm implementation** - Stat calculations, level scaling
- **Game rules** - What can spawn where, progression formulas

### Game Engine DOES NOT

- **Data validation** - Database service validates generated data is legal
- **Persistence** - Repository handles database operations
- **Authentication** - API layer handles user context
- **Business rules** - Database service enforces "can this action occur"

## Game Engine vs Database Service

Understanding the boundary between these layers:

### Example: Character Spawning

**Game Engine (Spawner):**
- Determines spawn should happen
- Selects species based on location/conditions
- Randomizes sex, personality, affinities
- Calculates level (5-8 based on area difficulty)
- Generates stat values using growth formulas

**Database Service:**
- Validates species exists
- Confirms affinities are in allowed list
- Checks stats are positive integers
- Verifies all required fields present
- Saves to database

### Example: Stat Calculation (Future)

**Game Engine (Calculator):**
- Applies level-up formula
- Calculates stat gains from growth rates
- Applies personality modifiers
- Applies sex modifiers

**Database Service:**
- Validates new stats are legal values
- Confirms level increased by 1
- Updates database record

## Extending the Game Engine

### Adding New Definitions

When you need game-wide constants:

1. Create file in `definitions/`:

       # game_engine/definitions/status_effects.py
       STATUS_EFFECTS = [
           "poisoned",
           "burned",
           "frozen",
           "paralyzed"
       ]

2. Import where needed for validation or randomization

3. No service layer needed - just reference data

### Adding New Services

When you need procedural generation or game mechanics:

#### 1. Identify the Domain

Examples:
- Combat/battle simulation
- Level-up/progression
- Loot generation
- AI decision-making

#### 2. Create Service Class

    # game_engine/combat_services/battle_simulator.py
    class BattleSimulator:
        def __init__(self, required_services):
            # Inject any needed database services
            pass
        
        def simulate_turn(self, attacker, defender, action):
            """
            Apply game mechanics to resolve a combat action.
            Returns result data for database service to validate/persist.
            """
            # Calculate damage using formulas
            # Apply stat modifiers
            # Check for critical hits
            # Return structured result
            pass

#### 3. Use Database Services for Validation

    def simulate_turn(self, attacker, defender, action):
        # Generate the result
        result = {
            'damage': calculated_damage,
            'critical': is_critical,
            'effects': applied_effects
        }
        
        # Let database service validate and persist
        return result  # Service validates this is legal

#### 4. Call from API Layer

    # api/routes/combat/combat_routes.py
    from src.game_engine.combat_services.battle_simulator import BattleSimulator
    
    @jwt_required()
    def execute_action():
        # Get action from request
        # Call battle simulator
        result = battle_simulator.simulate_turn(...)
        # Return result

## Future Service Examples

The game engine may eventually include services for:

**Combat & Battle:**
- Damage calculation
- Status effect application
- Turn order determination
- AI opponent decision-making

**Progression:**
- Level-up stat calculation
- Skill/ability unlocking
- Evolution triggers

**World Systems:**
- Encounter rate calculation
- Weather/time effects on spawns
- Area-specific spawn tables

**Rewards & Loot:**
- Item drop generation
- Experience calculation
- Treasure generation

**AI & Behavior:**
- Enemy team composition
- NPC dialogue selection
- Trainer battle logic

## Best Practices

### DO

- Generate complete, valid data in one pass
- Use definitions for constants and enums
- Inject database services as dependencies
- Return structured data dicts for validation
- Log generation failures for debugging
- Use randomization for replayability
- Apply game formulas and algorithms here

### DON'T

- Access repositories directly (use services)
- Perform database operations
- Skip validation by database service
- Hardcode game constants (use definitions)
- Mix API concerns (authentication, HTTP) with mechanics
- Store state in service instances
- Generate invalid data intentionally

## Design Principles

### Stateless Services

Game engine services should be stateless - they don't maintain game state between calls:

    # Good - stateless
    spawner.generate_kaijuchan(conditions)
    
    # Avoid - stateful
    spawner.set_location('forest')
    spawner.generate()

### Determinism vs Randomness

Balance predictability with variety:
- Use seeded random for testability
- Document random ranges and probabilities
- Allow override for testing/debugging

### Separation of Concerns

- **Engine**: How to generate/calculate
- **Database**: Is the result valid
- **API**: When to trigger generation

## Testing Strategy

Game engine services should be tested for:

**Correctness:**
- Generated data matches expected format
- Formulas produce correct results
- Random values fall within expected ranges

**Edge Cases:**
- Minimum/maximum values
- Empty/missing conditions
- Invalid inputs (should fail gracefully)

**Randomness:**
- Distributions are reasonable
- Seeded random produces consistent results
- All outcomes are possible

## Current Limitations

The game engine is in early development. Current limitations:

- Limited spawn conditions (location, level range)
- Single spawner service (kaijuchan only)
- No combat, progression, or loot systems
- Minimal AI or behavior logic

These will be addressed as gameplay features are implemented.

## Future Considerations

- Performance optimization for complex calculations
- Caching for expensive generation operations
- Event-driven architecture for game state changes
- Configuration files for tuning game balance
- Modding support through plugin architecture