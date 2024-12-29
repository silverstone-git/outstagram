from sqlalchemy.orm import Session, selectinload
from ...lib.models import Post
from ...lib.schemas import UserPublic
from ...lib.exceptions import CouldntGetDashboard

def get_dashboard(user: UserPublic, db: Session):
    # returns a comprehensive dictionary of data
    
    posts = []
    try:
        # posts with mediaurl objs
        posts = (
            db.query(Post)
            .options(
                selectinload(Post.media_urls)
            )
            .filter(Post.author_user_id == user.user_id)
            .all()
        )
    except:
        raise CouldntGetDashboard
    
    return {**user.model_dump(), "posts": posts}