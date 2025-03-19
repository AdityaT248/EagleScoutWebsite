from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)
    author: Optional[str] = Field(None, max_length=100)
    
class CommentCreate(CommentBase):
    product_id: Optional[int] = None
    rating: Optional[float] = Field(None, ge=1, le=5)
    
class CommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=1000)
    approved: Optional[bool] = None
    
class Comment(CommentBase):
    id: int
    product_id: Optional[int] = None
    rating: Optional[float] = None
    image_path: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    approved: bool = False
    
    model_config = {"from_attributes": True}

class CommentResponse(BaseModel):
    comment: Comment

class CommentsResponse(BaseModel):
    comments: List[Comment]
    
# Models for image upload
class ImageUpload(BaseModel):
    comment_id: int
    image: bytes