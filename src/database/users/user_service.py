from typing import Optional, Dict
from .user_repository import UserRepository
from .user_models import User
from src.database.base.exceptions import ValidationError


class UserValidationError(ValidationError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)



class UserService:
    """Service layer for user operations"""

    def __init__(self, repository: UserRepository):
        self.repository = repository


    def register_user(self, username: str, password: str,
                     name: Optional[str] = None) -> User:
        """Register a new user"""
        # Validate username
        username = (username or "").strip()
        if not username:
            raise UserValidationError("Username is required")
        
        if len(username) < 3:
            raise UserValidationError("Username must be at least 3 characters")
        
        if len(username) > 80:
            raise UserValidationError("Username cannot exceed 80 characters")
        
        if self.repository.username_exists(username):
            raise UserValidationError("Username already exists")
        
        # Validate password
        if not password:
            raise UserValidationError("Password is required")
        
        if len(password) < 6:
            raise UserValidationError("Password must be at least 6 characters")

        # Create the user
        return self.repository.create_user(
            username=username,
            password=password,
            name=name
        )

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password"""
        if not username or not password:
            return None
        
        user = self.repository.get_by_username(username)
        if user and user.check_password(password):
            return user
        
        return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID"""
        return self.repository.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username"""
        return self.repository.get_by_username(username)

    def update_user(self, user: User, data: Dict) -> User:
        """Update user information"""
        update_data = {}
        
        if 'name' in data:
            name = (data['name'] or "").strip() if data['name'] else None
            if name and len(name) > 64:
                raise UserValidationError("Name cannot exceed 64 characters")
            update_data['name'] = name

        
        if update_data:
            return self.repository.update(user, **update_data)
        
        return user

    def change_password(self, user: User, old_password: str, new_password: str) -> User:
        """Change a user's password"""
        if not user.check_password(old_password):
            raise UserValidationError("Current password is incorrect")
        
        if not new_password:
            raise UserValidationError("New password is required")
        
        if len(new_password) < 6:
            raise UserValidationError("New password must be at least 6 characters")
        
        return self.repository.update_password(user, new_password)

    def delete_user(self, user: User) -> None:
        """Delete a user account"""
        # All cascade deletes are handled by the User model relationships
        self.repository.delete(user)