from fastapi import HTTPException, status

class AlreadyLiked(HTTPException):
    def __init__(self, detail: str = "User has already liked the post"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ProblemCommenting(HTTPException):
    def __init__(self, detail: str = "There was a problem while adding your comment to the database"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
