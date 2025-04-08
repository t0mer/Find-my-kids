"""
Request models for training and collection management endpoints.
"""

from pydantic import BaseModel, Field

class TrainRequest(BaseModel):
    """
    Request model for training and collection management operations.
    Used by /train and /collection/delete endpoints.
    """
    collection_id: str = Field(
        ...,  # ... means required
        description="Unique identifier for the face collection",
        example="kid_1"
    )
