from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_, and_
from sqlmodel import select, func, and_, join, outerjoin

import datetime

from ...lib.models import Post, User, PostLike, MediaURL, FollowRequest
from ...lib.schemas import UserPublic, PostPublic
from ...lib.exceptions import CouldntGetDashboard, InvalidPageLength
from ...lib.constants import USER_POSTS_PAGE_LENGTH

def get_dashboard(user: UserPublic, db: Session, page: int):

    return get_user_posts_repo(username = user.username, current_user = user, db = db, page = page)


def get_user_posts_repo(username: str, current_user: UserPublic, db: Session, page: int = 1):

    target_user_tuple = db.query(User.user_id).filter(User.username == username).first()
    if not target_user_tuple:
        raise HTTPException(status_code=404, detail="User not found")
    target_user_id = target_user_tuple[0]

    if page < 1:
        raise InvalidPageLength

    offset = (page - 1) * USER_POSTS_PAGE_LENGTH

    statement = (
        select(
            Post,
            func.jsonb_agg(
                func.json_build_object('url', MediaURL.url, 'media_type', MediaURL.media_type)
            ).filter(MediaURL.post_id.isnot(None)).label("media_urls"),
            PostLike.datetime_liked.label("is_liked"),
        )
        .join(User, Post.author_user_id == User.user_id)
        .outerjoin(MediaURL, Post.post_id == MediaURL.post_id)
        .outerjoin(PostLike, and_(PostLike.post_id == Post.post_id, PostLike.liker_user_id == current_user.user_id))
        .group_by(Post.post_id, Post.author_user_id, PostLike.datetime_liked)
        .where(Post.author_user_id == target_user_id)
        .offset(offset)
        .limit(USER_POSTS_PAGE_LENGTH)
    )

    posts = list(db.execute(statement).all())


    def row_to_postpublic(row: tuple) -> PostPublic:
        data = row[0].model_dump()
        dt = data.get('datetime_posted')
        if isinstance(dt, (datetime.datetime, datetime.date)):
            # ensure datetime is ISO string, include timezone if present
            if isinstance(dt, datetime.date) and not isinstance(dt, datetime.datetime):
                # convert date -> datetime at midnight
                dt = datetime.datetime(dt.year, dt.month, dt.day)
            data['datetime_posted'] = dt.isoformat()

        media_urls = row[1]
        is_liked_ts = row[2]

        return PostPublic(
            **data,
            author=username,
            media_urls=media_urls or [],
            is_liked=(is_liked_ts is not None),
        )

    posts = list(map(row_to_postpublic, posts))

    # print("posts got: ", posts)

    return posts


def get_user_profile_repo(target_username: str, current_user: UserPublic, db: Session):

    target = db.query(User).filter(User.username == target_username).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    
    posts_count = db.query(Post).filter(Post.author_user_id == target.user_id).count()

    followers_count = db.query(FollowRequest).filter(
        FollowRequest.requested_user_id == target.user_id,
        FollowRequest.status == "accepted"
    ).count()
    following_count = db.query(FollowRequest).filter(
        FollowRequest.requester_user_id == target.user_id,
        FollowRequest.status == "accepted"
    ).count()


    all_the_requests_between_you_two = db.query(FollowRequest).filter(
        or_(
            and_(
                FollowRequest.requester_user_id == current_user.user_id,
                FollowRequest.requested_user_id == target.user_id,
            ),
            and_(
                FollowRequest.requester_user_id == target.user_id,
                FollowRequest.requested_user_id == current_user.user_id,
            ),
        ),
    ).all()

    # no_of_reqs = len(all_the_requests_between_you_two)

    you_follow_them_status = 0
    they_follow_you_status = 0

    for req in all_the_requests_between_you_two:
        if req.requester_user_id == current_user.user_id and req.status == 'pending':
            # youre an absolute simp
            you_follow_them_status = 0.5
        elif req.requester_user_id == current_user.user_id and req.status == 'accepted':
            you_follow_them_status = 1
        elif req.requester_user_id == target.user_id and req.status == 'pending':
            they_follow_you_status = 0.5
        elif req.requester_user_id == target.user_id and req.status == 'accepted':
            they_follow_you_status = 1


    print("\n\n requests found:")
    print(all_the_requests_between_you_two)

    
    return {
        **target.dict(),
        "posts_count": posts_count,
        "followers_count": followers_count,
        "following_count": following_count,
        "they_follow_you": they_follow_you_status,
        "you_follow_them": you_follow_them_status
    }
    
