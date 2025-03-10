from typing import List, Dict, Any

# Type definitions for availability
Availability = Dict[str, bool]

# Type definitions for comments
Comment = str
CommentsList = List[Comment]

# Type definitions for user
class User:
    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email

# Type definitions for contact information
ContactInfo = Dict[str, str]

# Type definitions for file upload response
FileUploadResponse = Dict[str, Any]