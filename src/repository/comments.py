from sqlalchemy.orm import Session
from ...lib.schemas import PostCommentSchema, UserPublic
from ...lib.models import PostComment
from ...lib.exceptions import ProblemCommenting

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

