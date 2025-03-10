from pydantic import BaseModel, Field
from typing import List, Optional

class Comment(BaseModel):
    id: int
    content: str = Field(..., max_length=500)
    author: Optional[str] = Field(None, max_length=100)
    created_at: str

class CommentCreate(BaseModel):
    content: str = Field(..., max_length=500)
    author: Optional[str] = Field(None, max_length=100)

class CommentResponse(BaseModel):
    comment: Comment

class CommentsResponse(BaseModel):
    comments: List[Comment]