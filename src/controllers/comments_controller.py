from fastapi import APIRouter, HTTPException
from src.models.comments_model import Comment
from src.services.comments_service import CommentsService

router = APIRouter()
comments_service = CommentsService()

@router.post("/comments/", response_model=Comment)
def post_comment(comment: Comment):
    try:
        return comments_service.add_comment(comment)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/comments/", response_model=list[Comment])
def get_comments():
    return comments_service.get_all_comments()