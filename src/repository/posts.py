
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlmodel import select, func, and_, exists, desc
from ...lib.models import Post, User, MediaURL, PostLike, PostCategory, FollowRequest
from ...lib.schemas import Post, PostPublic, UserPublic, PostCreate
from ...lib.exceptions import CouldntGetLikes, InvalidPageLength, PostNotFound, InvalidCategory
from ...lib.constants import LIKE_PAGE_LENGTH, FEED_PAGE_LENGTH
from ...lib.s3_client import S3ClientManager
from uuid import uuid4
from datetime import datetime, timedelta, timezone, date
from typing import List
from uuid import uuid4

s3_manager = S3ClientManager()
s3_client = s3_manager.get_client()
s3_bucket = s3_manager.get_bucket()

def is_valid_category(category_str: str) -> bool:
    try:
        PostCategory(category_str)
        return True
    except ValueError:
        return False

# Function to create a new post
def create_post(db: Session, post: PostCreate, author_user_id: int, author_username: str) -> PostPublic:

    post_id_formulated = uuid4()

    media_url_objects = []
    for media_url in post.media_urls:
        media_url_object = MediaURL(post_id=str(post_id_formulated), url=media_url.url, media_type=media_url.media_type)
        media_url_objects.append(media_url_object)
        db.add(media_url_object)

    new_post = Post(
        post_id=str(post_id_formulated),
        caption=post.caption,
        post_category=post.post_category,
        author_user_id=int(author_user_id),
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return PostPublic(
        post_id=str(new_post.post_id),
        caption=new_post.caption,
        post_category=new_post.post_category,
        datetime_posted=new_post.datetime_posted.isoformat(),
        author_user_id=new_post.author_user_id or 0,
        author=author_username,
        highlighted_by_author=new_post.highlighted_by_author,
        media_urls=media_url_objects,
        is_liked=False
    )

# Function to retrieve a post by its ID
def get_post(post_id: str, current_user: UserPublic, db: Session) -> PostPublic:
    post = db.query(Post).filter(Post.post_id == post_id).first()
    
    #author = db.query(User).filter(User.user_id == post.author_user_id).first()

    #media_urls = db.scalars(select(MediaURL.url).where(MediaURL.post_id == post_id)).all()
    

    # condensed query using sqlalchemy's Eager Loading strategy
    post_with_is_liked = (
        db.query(Post, exists().where(
        and_(
            PostLike.post_id == Post.post_id,
            PostLike.liker_user_id == current_user.user_id
        )
        ).label('is_liked'))
        .options(
            joinedload(Post.author),
            selectinload(Post.media_urls)
        )
        .filter(Post.post_id == post_id)
        .first()
    )

    post, is_liked = post_with_is_liked

    if post is None:
        raise PostNotFound
    
    refreshed_media_urls = []
    for media in post.media_urls:
        try:
            # Extract object key from URL
            object_key = media.url.split(s3_bucket)[1].split('?')[0][1:]
            
            # Extract timestamp from object key
            timestamp_str = object_key.split('-')[0]
            creation_time = datetime.fromtimestamp(int(timestamp_str))

            # Check if the URL is older than 7 days
            if datetime.now(timezone.utc) - creation_time > timedelta(days=7):
                # Generate new presigned URL
                new_presigned_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': s3_bucket, 'Key': object_key},
                    ExpiresIn=604800  # 7 days
                )
                
                # Update the database
                media.url = new_presigned_url
                db.add(media)
                db.commit()
                db.refresh(media)
                refreshed_media_urls.append(media)
            else:
                refreshed_media_urls.append(media)
        except Exception as e:
            # if parsing fails, just append the original url
            refreshed_media_urls.append(media)


    dt= post.datetime_posted
    if isinstance(dt, (datetime, date)):
        # ensure datetime is ISO string, include timezone if present
        if isinstance(dt, date) and not isinstance(dt, datetime):
            # convert date -> datetime at midnight
            dt = datetime(dt.year, dt.month, dt.day)
        post.datetime_posted= dt.isoformat()


    return PostPublic(
        **post.model_dump(),
        is_liked = is_liked,
        author= post.author.username,
        media_urls = refreshed_media_urls
    )


def like_post_repo(post_id: str, liker: UserPublic, db: Session) -> PostLike:
    # like a post and return a PostLike

    post_like_existing = db.get(PostLike, (post_id, liker.user_id))

    if not post_like_existing:
        postLike = PostLike(post_id=post_id, liker_user_id=liker.user_id)
        db.add(postLike)
        db.commit()
        db.refresh(postLike)
        return postLike
    
    return post_like_existing


def unlike_post_repo(post_id: str, liker: UserPublic, db: Session) -> bool:
    # unlike a post
    post_like = db.get(PostLike, (post_id, liker.user_id))

    if post_like:
        db.delete(post_like)
        db.commit()
        return True
    
    return False


def get_likes(post_id: str, db: Session, page: int):
    # returns Postlike[] array

    if page < 1:
        raise InvalidPageLength

    try:
        offset = (page - 1) * LIKE_PAGE_LENGTH

        statement = (
            select(PostLike, User.username)
            .join(User, PostLike.liker_user_id == User.user_id)
            .where(PostLike.post_id == post_id)  # Use where instead of filter_by
            .limit(LIKE_PAGE_LENGTH)
            .offset(offset)
        )
        
        results = db.execute(statement).all()

        likes_with_usernames = []
        for post_like, username in results:
            like_dict = post_like.dict()
            like_dict['liker_username'] = username
            likes_with_usernames.append(like_dict)
        
        #print("\n\n\n\nres: ", likes_with_usernames)

        return likes_with_usernames


    except:
        raise CouldntGetLikes
    



# Function to retrieve all posts
"""
def get_all_posts(db: Session) -> List[PostPublic]:
    posts = db.query(Post).all()
    return [
        PostPublic(
            post_id=post.post_id,
            media_urls=post.media_urls,
            caption=post.caption,
            post_category=post.post_category,
            datetime_posted=post.datetime_posted.isoformat(),
            author_user_id=post.author_user_id
        )
        for post in posts
    ]
"""


def get_feed_repo(current_user: UserPublic, db: Session, category: str | None = None, page: int | None = 1) -> List[PostPublic]:

    if page is not None and page < 1:
        raise InvalidPageLength
    elif page is None:
        page = 1


    # Get users that current user follows
    following_ids = db.query(FollowRequest.requested_user_id).filter(
        FollowRequest.requester_user_id == current_user.user_id,
        FollowRequest.status == "accepted"
    ).all()
    following_ids = [uid for (uid,) in following_ids]
    

    if category is not None and is_valid_category(category):
        statement = (
            select(
                Post,
                User.username,
                func.string_agg(MediaURL.url, ',').label("media_urls"),
                PostLike.datetime_liked.label("is_liked"),
            )
            .join(User, Post.author_user_id == User.user_id)
            .outerjoin(MediaURL, Post.post_id == MediaURL.post_id)
            .outerjoin(PostLike, and_(PostLike.post_id == Post.post_id, PostLike.liker_user_id == current_user.user_id))
            .group_by(Post.post_id, Post.author_user_id, User.username, PostLike.datetime_liked)
            .where(and_(Post.author_user_id.in_(following_ids), Post.post_category == category))
            .order_by(
                desc(Post.datetime_posted))
            .offset(
                (page - 1) * FEED_PAGE_LENGTH)
            .limit(FEED_PAGE_LENGTH)
        )
    elif category is not None:
        raise InvalidCategory
    else:
        statement = (
            select(
                Post,
                User.username,
                func.string_agg(MediaURL.url, ',').label("media_urls"),
                PostLike.datetime_liked.label("is_liked"),
            )
            .join(User, Post.author_user_id == User.user_id)
            .outerjoin(MediaURL, Post.post_id == MediaURL.post_id)
            .outerjoin(PostLike, and_(PostLike.post_id == Post.post_id, PostLike.liker_user_id == current_user.user_id))
            .group_by(Post.post_id, Post.author_user_id, User.username, PostLike.datetime_liked)
            .where(Post.author_user_id.in_(following_ids))
            .order_by(
                desc(Post.datetime_posted))
            .offset(
                (page - 1) * FEED_PAGE_LENGTH)
            .limit(FEED_PAGE_LENGTH)
        )

    posts = list(db.execute(statement).all())

    posts = list(map(lambda x: PostPublic(**x[0].model_dump(), author = x[1], datetime_posted= x[0].datetime_posted.isoformat(), media_urls = x[2].split(','), is_liked = True if x[3] is not None else False), posts))

    #print("\n\n\ngot posts: ", posts, type(posts), type(posts[0]))

    
    return posts


# Function to update a post
def update_post(db: Session, post_id: str, updated_data: Post) -> PostPublic | None:
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if post is None:
        return None  # Return None if the post is not found
    
    # Update the post's attributes
    post.media_urls = updated_data.media_urls
    post.caption = updated_data.caption
    post.post_category = updated_data.post_category
    
    db.commit()  # Commit the changes to the database
    db.refresh(post)  # Refresh the instance to get the latest data
    
    return PostPublic(
        post_id=post.post_id,
        media_urls=post.media_urls,
        caption=post.caption,
        post_category=post.post_category,
        datetime_posted=post.datetime_posted.isoformat(),
        author_user_id=post.author_user_id,
        highlighted_by_author= post.highlighted_by_author,
        author= post.author.username,
        is_liked=None
    )

# Function to delete a post
def delete_post(db: Session, post_id: str) -> bool:
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if post is None:
        return False  # Return False if the post is not found
    
    db.delete(post)  # Delete the post from the session
    db.commit()  # Commit the changes to the database
    return True  # Return True to indicate successful deletion

