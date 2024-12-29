from sqlalchemy.orm import Session, selectinload
from sqlmodel import select, func, and_, join, outerjoin
from ...lib.models import Post, User, PostLike, MediaURL
from ...lib.schemas import UserPublic, PostPublic
from ...lib.exceptions import CouldntGetDashboard, InvalidPageLength
from ...lib.constants import USER_POSTS_PAGE_LENGTH

def get_dashboard(user: UserPublic, db: Session, page: int):

    return get_user_posts_repo(username = user.username, current_user = user, db = db, page = page)


def get_user_posts_repo(username: str, current_user: UserPublic, db: Session, page: int = 1):

    target_user_id = db.query(User.user_id).filter(User.username == username).first()
    target_user_id = target_user_id[0]
    if not target_user_id:
        raise HTTPException(status_code=404, detail="User not found")

    if page < 1:
        raise InvalidPageLength

    offset = (page - 1) * USER_POSTS_PAGE_LENGTH

    #print("\n\n\n\ntarget: ", target_user_id)
    

    """
    SELECT post.*, GROUP_CONCAT(mediaurl.url) AS media_urls, postlike.datetime_liked AS is_liked FROM post JOIN user ON post.author_user_id = user.user_id LEFT JOIN mediaurl ON post.post_id = mediaurl.post_id LEFT JOIN postlike ON postlike.post_id = post.post_id AND postlike.liker_user_id = user.user_id GROUP BY post.post_id, post.author_user_id, postlike.datetime_liked;
    """

    statement = (
        select(
            Post,
            func.group_concat(MediaURL.url).label("media_urls"),
            PostLike.datetime_liked.label("is_liked"),
        )
        .join(User, Post.author_user_id == User.user_id)
        .outerjoin(MediaURL, Post.post_id == MediaURL.post_id)
        .outerjoin(PostLike, and_(PostLike.post_id == Post.post_id, PostLike.liker_user_id == current_user.user_id))
        .group_by(Post.post_id, Post.author_user_id, PostLike.datetime_liked)
        .where(Post.author_user_id == target_user_id)
        .limit(USER_POSTS_PAGE_LENGTH)
        .offset(offset)
    )

    posts = list(db.execute(statement).all())

    posts = list(map(lambda x: PostPublic(**x[0].model_dump(), author = username, media_urls = x[1].split(','), is_liked = True if x[2] is not None else False), posts))

    #print("posts got: ", posts)

    return posts
    
