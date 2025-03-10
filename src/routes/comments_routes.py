from fastapi import APIRouter, HTTPException
from src.controllers.comments_controller import post_comment, get_comments

router = APIRouter()

@router.post("/comment/")
async def create_comment(comment: str):
    return await post_comment(comment)

@router.get("/comments/")
async def read_comments():
    return await get_comments()