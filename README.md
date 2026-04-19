# Monster Catching Game

A monster catching and battling game with a Flask-based API backend. Currently in early development with foundational architecture in place.

## Project Status

This project is in the **proof-of-concept** phase. Current functionality includes:

- User registration and authentication
- Species registry with stat systems and elemental affinities
- Random monster generation
- RESTful API with JWT authentication

The focus is on establishing clean architecture patterns before expanding gameplay features.

## Quick Start

### Prerequisites

- Python 3.10 or higher
- virtualenv

### Installation

1. Clone the repository

2. Create and activate virtual environment:

       python3 -m venv venv
       source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:

       pip install -r requirements.txt

4. Set up environment variables:

       # Create .env file in src/api/config/
       echo "JWT_SECRET_KEY=your-secret-key-here" > src/api/config/.env

5. Run the application:

       python3 src/api/api.py

The API will be available at `http://localhost:5050`

### Verify Installation

Check the health endpoint:

    curl http://localhost:5050/api/health

Expected response:

    {"status": "healthy"}

## Project Structure

    DesktopRPG/
    ├── src/
    │   ├── api/                 # REST API layer
    │   ├── database/            # Data persistence layer
    │   ├── game_engine/         # Game mechanics and generation
    │   └── scripts/             # Database seeding and utilities
    ├── instance/                # SQLite database (auto-created)
    ├── requirements.txt
    └── README.md

## Architecture

The project follows a layered architecture with clear separation of concerns:

### API Layer

RESTful HTTP endpoints with JWT authentication. Handles request validation and response formatting.

**Documentation:** [api/README.md](src/api/README.md)

### Database Layer

Three-tier architecture (Models, Repositories, Services) managing data persistence and business rules.

**Documentation:** [database/README.md](src/database/README.md)

### Game Engine

Procedural generation and game mechanics. Handles spawn logic, randomization, and future gameplay systems.

**Documentation:** [game_engine/README.md](src/game_engine/README.md)

### Scripts

Utility scripts for database management, primarily seeding initial game data.

## Key Features

### Authentication

- User registration with password hashing
- JWT token-based authentication
- Secure logout with token blacklisting
- Account management (update profile, change password, delete account)

### Species System

- Pre-defined monster species templates
- Stat system: physical attack/defense, magic attack/defense, agility, charisma
- Elemental affinity system (fire, water, earth, plant, air, light, dark)
- Growth rates for stat progression
- Sex-based stat modifiers

### Monster Generation

- Random monster spawning from species templates
- Randomized attributes: sex, personality, elemental affinities
- Level-based generation
- User ownership and persistence

## Current Entities

- **Users** - Player accounts with authentication
- **Species** - Shared monster templates (Wolf, Fox, Turtle, Fire Drake, Bird)
- **PlayableCharacter** - User-owned monster instances

## Development

### Database

The project uses SQLite for development. The database is automatically created and seeded on first run.

To manually seed the database (shouldn't be necessary):

    python3 src/scripts/db_seed/seed_db.py


## Design Philosophy

### Clean Architecture

- **Separation of concerns** - API, database, and game logic are isolated
- **Dependency injection** - Services receive dependencies explicitly
- **Single responsibility** - Each layer has a clearly defined purpose

### Extensibility

- **Base classes** - Shared functionality through inheritance
- **Generic repositories** - Minimal boilerplate for new entities
- **Service pattern** - Business logic separated from data access

### Documentation-Driven

- Comprehensive README files for each layer
- Established patterns before feature expansion
- Developer-focused documentation for maintenance

## Technology Stack

- **Flask** - Web framework
- **SQLAlchemy** - ORM and database toolkit
- **Flask-JWT-Extended** - JWT authentication
- **Flask-CORS** - Cross-origin resource sharing
- **SQLite** - Development database
- **Python 3.10** - Language runtime

## Development

Issue tracking at https://redmine.ocelotcodesystems.com/projects/desktoprpg