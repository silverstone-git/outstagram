from fastapi import HTTPException, status

class AlreadyLiked(HTTPException):
    def __init__(self, detail: str = "User has already liked the post"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ProblemCommenting(HTTPException):
    def __init__(self, detail: str = "There was a problem while adding your comment to the database"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class CouldntGetLikes(HTTPException):
    def __init__(self, detail: str = "There was a problem while fetching all the likes for this post"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
        

class InvalidPageLength(HTTPException):
    def __init__(self, detail: str = "The Page length is invalid in the request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class CouldntGetComments(HTTPException):
    def __init__(self, detail: str = "The comments on this post couldnt be fetched"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class PostNotFound(HTTPException):
    def __init__(self, detail: str = "We couldnt find the post you have requested"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        

class CouldntGetDashboard(HTTPException):
    def __init__(self, detail: str = "We couldnt get the posts for this user"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class InvalidCategory(HTTPException):
    def __init__(self, detail: str = "This category input is invalid"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

