# app/models/nose.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.core.time import get_kst_now

class NoseVector(Base):
    """
    Represents a stored nose vector for a dog associated with a user.

    This model stores the unique identifier for the dog's non-print,
    the associated user, and the extracted feature vector.
    """
    __tablename__ = "nose_vectors"

    id = Column(Integer, primary_key=True, index=True)
    # Unique identifier for the dog's nose print. This can be used
    # to link multiple vectors from the same dog if needed, or simply
    # act as the primary identifier for a registered non-print.
    class_id = Column(String, unique=True, nullable=False, index=True) # index=True 추가

    # Foreign key linking this nose vector to a specific user.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # The feature vector extracted from the nose image.
    # Stored as JSON, typically a list of floats.
    vector = Column(JSON, nullable=False)

    created_at = Column(DateTime, default=get_kst_now, nullable=False) # nullable=False 추가

    # Define the relationship back to the User model.
    # Use string literal 'User' to avoid circular import issues.
    user = relationship("User", back_populates="nose_vectors")

    def __repr__(self):
        """
        Provides a helpful representation of the NoseVector object.
        """
        return f"<NoseVector(id={self.id}, class_id='{self.class_id}', user_id={self.user_id})>"