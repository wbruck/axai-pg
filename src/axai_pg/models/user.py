"""User model for the application."""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    """User model representing application users."""
    
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)

    def __repr__(self):
        """String representation of the User model."""
        return f"<User {self.username}>" 