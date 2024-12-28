from sqlalchemy.orm import Session
from sqlalchemy import select
from ...lib.schemas import PostCommentSchema, UserPublic
from ...lib.models import PostComment
from ...lib.exceptions import ProblemCommenting, CouldntGetComments, InvalidPageLength
from ...lib.constants import COMMENT_PAGE_LENGTH

def add_comment_repo(content: str, post_id: str, current_user: UserPublic, db: Session):
    # add the comment and be good
    
    try:
        newcomment = PostComment(post_id = post_id, content = content, author_user_id = current_user.user_id)
        db.add(newcomment)
        db.commit()
        db.refresh(newcomment)  # Refresh the instance to get the latest data from the database
        return newcomment
    except e:
        print(e)
        raise ProblemCommenting


def get_comments(post_id: str, db: Session, page: int):
    if page < 1:
        raise InvalidPageLength

    try:
        offset = (page - 1) * COMMENT_PAGE_LENGTH

        statement = select(PostComment).filter_by(post_id=post_id).limit(COMMENT_PAGE_LENGTH).offset(offset)
        res = db.scalars(statement).all()
        print("\n\n\n\nres: ", res)
        return res
    
    except:
        raise CouldntGetComments