# API Layer

## Overview

The API layer provides RESTful HTTP endpoints for interacting with the game. It follows a clear architectural pattern:

- **Routes**: HTTP endpoint definitions and request validation
- **Services**: Business logic and data validation (in database layer)
- **Authentication**: JWT-based user authentication

**Golden Rule**: Route handlers validate request **shape**, service layer validates data **legitimacy**.

## Directory Structure

    api/
    ├── config/
    │   ├── config.py           # API configuration (JWT, CORS)
    │   └── .env                # Environment variables
    ├── routes/
    │   ├── users/
    │   │   ├── __init__.py     # Blueprint registration
    │   │   └── user_routes.py  # Route handlers
    │   ├── species/
    │   │   ├── __init__.py
    │   │   └── species_routes.py
    │   └── playable_characters/
    │       ├── __init__.py
    │       └── playable_character_routes.py
    ├── api.py                  # Application entry point
    └── app_factory.py          # Flask app configuration

## Request Flow

1. Client sends HTTP request
2. Flask routes to appropriate blueprint
3. Route handler validates request shape (required fields, data types)
4. Service layer validates business rules and data legitimacy
5. Response formatted and returned to client

## Response Format

### Success Responses

Return the data directly with appropriate HTTP status code:

**Single entity (200 OK):**

    {
      "id": 1,
      "name": "Wolf",
      "base_stats": {
        "phys_attack": 10,
        "phys_defense": 10,
        "magic_attack": 10,
        "magic_defense": 10,
        "agility": 10,
        "charisma": 10
      }
    }

**List of entities (200 OK):**

    [
      {"id": 1, "name": "Wolf"},
      {"id": 2, "name": "Fox"}
    ]

**List with pagination metadata (200 OK):**

    {
      "items": [...],
      "pagination": {
        "page": 1,
        "limit": 20,
        "total": 100,
        "pages": 5
      }
    }

**Creation success (201 Created):**

    {
      "message": "User created successfully",
      "user": {
        "id": 1,
        "username": "player1"
      }
    }

**Action success (200 OK):**

    {
      "message": "Password changed successfully"
    }

### Error Responses

Always include an `error` object with `message`, `code`, and optional `details`:

**Validation error (400 Bad Request):**

    {
      "error": {
        "message": "Missing required fields",
        "code": "VALIDATION_ERROR",
        "details": {
          "missing_fields": ["username", "password"]
        }
      }
    }

**Not found (404 Not Found):**

    {
      "error": {
        "message": "Species not found",
        "code": "NOT_FOUND"
      }
    }

**Unauthorized (401 Unauthorized):**

    {
      "error": {
        "message": "Invalid username or password",
        "code": "UNAUTHORIZED"
      }
    }

**Forbidden (403 Forbidden):**

    {
      "error": {
        "message": "You do not own this resource",
        "code": "FORBIDDEN"
      }
    }

**Server error (500 Internal Server Error):**

    {
      "error": {
        "message": "An unexpected error occurred",
        "code": "INTERNAL_ERROR"
      }
    }

### Standard HTTP Status Codes

- **200 OK** - Successful GET, PATCH, DELETE
- **201 Created** - Successful POST (resource created)
- **400 Bad Request** - Invalid request data/format
- **401 Unauthorized** - Missing or invalid authentication
- **403 Forbidden** - Authenticated but not authorized
- **404 Not Found** - Resource doesn't exist
- **500 Internal Server Error** - Server-side error

### Standard Error Codes

- `VALIDATION_ERROR` - Request data validation failed
- `NOT_FOUND` - Requested resource doesn't exist
- `UNAUTHORIZED` - Authentication failed or missing
- `FORBIDDEN` - Insufficient permissions for action
- `DUPLICATE_RESOURCE` - Resource already exists (e.g., username taken)
- `INTERNAL_ERROR` - Unexpected server error

## Authentication

### JWT Token Authentication

Protected routes require a JWT token in the Authorization header:

    Authorization: Bearer <token>

### Getting a Token

Request:

    POST /api/auth/login
    Content-Type: application/json

    {
      "username": "player1",
      "password": "securepassword"
    }

Response:

    {
      "message": "Login successful",
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "user": {
        "id": 1,
        "username": "player1"
      }
    }

### Using the Token

    GET /api/playable_characters
    Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

### Protected Routes

Use the `@jwt_required()` decorator:

    from flask_jwt_extended import jwt_required, get_jwt_identity

    @jwt_required()
    def get_user_playable_characters():
        current_user_id = int(get_jwt_identity())
        # ... handler logic

### Token Expiration

Tokens expire after 12 hours (configurable in `api/config/config.py`).

## Endpoint Patterns

### User-Owned Resources

Resources that belong to a specific user (e.g., PlayableCharacter).

**Standard endpoints:**

    GET    /api/{entity}              # List current user's entities
    GET    /api/{entity}/<id>         # Get if owned by current user
    POST   /api/{entity}              # Create for current user
    PATCH  /api/{entity}/<id>         # Update if owned by current user
    DELETE /api/{entity}/<id>         # Delete if owned by current user

**All require authentication** - automatically scoped to current user.

Example:

    GET /api/playable_characters
    Authorization: Bearer <token>

Returns only the authenticated user's characters.

### Shared Resources

Resources available to all users (e.g., Species).

**Standard endpoints:**

    GET    /api/{entity}              # List all (public)
    GET    /api/{entity}/<id>         # Get one (public)

**No creation via API** - Shared resources are managed through database seeding.

Example:

    GET /api/species

Returns all species (no authentication required).

## Pagination

For list endpoints, use query parameters:

    GET /api/species?page=1&limit=20

**Parameters:**
- `page` - Page number (default: 1)
- `limit` - Items per page (default: 20, max: 100)

**Response includes pagination metadata:**

    {
      "items": [...],
      "pagination": {
        "page": 1,
        "limit": 20,
        "total": 100,
        "pages": 5
      }
    }

## Filtering

Use query parameters to filter results:

    GET /api/species?elemental_affinity=fire
    GET /api/playable_characters?species_id=1&level_min=5

**Multiple values for same parameter:**

    GET /api/species?elemental_affinity=fire&elemental_affinity=water

**Combining filters with pagination:**

    GET /api/species?elemental_affinity=fire&page=1&limit=10

Route handlers pass query params to service layer for filtering.

## Adding New Endpoints

Follow these steps to add endpoints for a new entity (e.g., `Item`):

### 1. Create Route Directory

    api/routes/items/
    ├── __init__.py
    └── item_routes.py

### 2. Define Blueprint and URL Rules

    # api/routes/items/__init__.py
    from flask import Blueprint
    from . import item_routes

    items_bp = Blueprint('items', __name__)

    # CRUD endpoints
    items_bp.add_url_rule('/api/items', view_func=item_routes.list_items, endpoint='list', methods=['GET'])
    items_bp.add_url_rule('/api/items/<int:item_id>', view_func=item_routes.get_item, endpoint='get', methods=['GET'])
    items_bp.add_url_rule('/api/items', view_func=item_routes.create_item, endpoint='create', methods=['POST'])
    items_bp.add_url_rule('/api/items/<int:item_id>', view_func=item_routes.update_item, endpoint='update', methods=['PATCH'])
    items_bp.add_url_rule('/api/items/<int:item_id>', view_func=item_routes.delete_item, endpoint='delete', methods=['DELETE'])

### 3. Implement Route Handlers

    # api/routes/items/item_routes.py
    from flask import jsonify, request
    from flask_jwt_extended import jwt_required, get_jwt_identity
    from src.database.items.item_service import ItemService
    from src.database.items.item_repository import ItemRepository
    from src.database.db import db

    item_service = ItemService(ItemRepository(db.session))

    @jwt_required()
    def list_items():
        """List all items for current user"""
        current_user_id = int(get_jwt_identity())
        
        # Extract pagination params
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        # Extract filters
        filters = {}
        if request.args.get('name'):
            filters['name'] = request.args.get('name')
        
        try:
            items = item_service.list_user_items(current_user_id, page, limit, **filters)
            return jsonify(items), 200
        except Exception as e:
            return jsonify({
                "error": {
                    "message": "Error retrieving items",
                    "code": "INTERNAL_ERROR"
                }
            }), 500

    @jwt_required()
    def get_item(item_id):
        """Get a specific item"""
        current_user_id = int(get_jwt_identity())
        
        try:
            item = item_service.get_user_item(current_user_id, item_id)
            if not item:
                return jsonify({
                    "error": {
                        "message": "Item not found",
                        "code": "NOT_FOUND"
                    }
                }), 404
            
            return jsonify(item.as_dict()), 200
        except Exception as e:
            return jsonify({
                "error": {
                    "message": "Error retrieving item",
                    "code": "INTERNAL_ERROR"
                }
            }), 500

    @jwt_required()
    def create_item():
        """Create a new item for current user"""
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validate request shape
        if not data or not data.get('name'):
            return jsonify({
                "error": {
                    "message": "Missing required field: name",
                    "code": "VALIDATION_ERROR"
                }
            }), 400
        
        try:
            item = item_service.create_item(current_user_id, data)
            return jsonify({
                "message": "Item created successfully",
                "item": item.as_dict()
            }), 201
        except ValueError as e:
            return jsonify({
                "error": {
                    "message": str(e),
                    "code": "VALIDATION_ERROR"
                }
            }), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "error": {
                    "message": "Error creating item",
                    "code": "INTERNAL_ERROR"
                }
            }), 500

    @jwt_required()
    def update_item(item_id):
        """Update an existing item"""
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": {
                    "message": "No update data provided",
                    "code": "VALIDATION_ERROR"
                }
            }), 400
        
        try:
            item = item_service.get_user_item(current_user_id, item_id)
            if not item:
                return jsonify({
                    "error": {
                        "message": "Item not found",
                        "code": "NOT_FOUND"
                    }
                }), 404
            
            updated_item = item_service.update_item(item, data)
            return jsonify(updated_item.as_dict()), 200
        except ValueError as e:
            return jsonify({
                "error": {
                    "message": str(e),
                    "code": "VALIDATION_ERROR"
                }
            }), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "error": {
                    "message": "Error updating item",
                    "code": "INTERNAL_ERROR"
                }
            }), 500

    @jwt_required()
    def delete_item(item_id):
        """Delete an item"""
        current_user_id = int(get_jwt_identity())
        
        try:
            item = item_service.get_user_item(current_user_id, item_id)
            if not item:
                return jsonify({
                    "error": {
                        "message": "Item not found",
                        "code": "NOT_FOUND"
                    }
                }), 404
            
            item_service.delete_item(item)
            return jsonify({"message": "Item deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "error": {
                    "message": "Error deleting item",
                    "code": "INTERNAL_ERROR"
                }
            }), 500

### 4. Register Blueprint

    # api/api.py
    from src.api.routes.items import items_bp

    app.register_blueprint(items_bp)

### 5. Test Endpoints

- Use Postman, curl, or automated tests
- Test authentication, validation, error cases
- Verify response formats match standards

TODO: create custom API client and build a test suite around it

### 6. Document Endpoints

tbd; we can produce informal documentation with zim wiki or use openAPI and potentially hook that directly into an api test framework

## Best Practices

### DO

- Validate request shape in route handlers (required fields, types)
- Use `@jwt_required()` for all user-scoped endpoints
- Extract user ID from JWT with `get_jwt_identity()`
- Return structured error responses with codes
- Use appropriate HTTP status codes
- Pass query params to service layer for filtering
- Roll back database session on errors
- Use service layer for all business logic

### DON'T

- Access repositories directly from routes
- Put business logic in route handlers
- Return raw exception messages to clients
- Skip input validation
- Expose sensitive information in errors
- Mix authentication logic with business logic
- Use GET requests with request bodies
- Hardcode configuration values

## Running the API

### Local Development

    python3 src/api/api.py

Runs on `http://localhost:5050` with debug mode enabled.

### staging/production

tbd - we can rig up a systemd file to use gunicorn and nginx but there's currently not enough of a game to put on a staging/production server. 

## Configuration

API configuration lives in `api/config/config.py`:

- **JWT_SECRET_KEY** - Secret for signing tokens (from `.env`)
- **JWT_ACCESS_TOKEN_EXPIRES** - Token expiration time (default: 12 hours)
- **CORS_ORIGINS** - Allowed origins for CORS
- **CORS_METHODS** - Allowed HTTP methods
- **CORS_ALLOW_HEADERS** - Allowed request headers

Necessary Environment variables are listed  in `api/config/.env.example`:
Copy `.env.example` to `.env` and provide a value for the listed variables
