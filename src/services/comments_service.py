from typing import List
from src.models.comments_model import Comment

class CommentsService:
    def __init__(self):
        self.comments: List[Comment] = []

    def add_comment(self, comment: Comment) -> None:
        self.comments.append(comment)

    def get_comments(self) -> List[Comment]:
        return self.comments

    def clear_comments(self) -> None:
        self.comments.clear()