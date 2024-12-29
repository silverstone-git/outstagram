
from sqlalchemy.orm import Session, joinedload, selectinload
#from sqlalchemy import select, exists, case, and_, delete
from sqlmodel import select, func, and_, join, outerjoin, case, exists, delete, desc
from sqlalchemy.exc import IntegrityError
from ...lib.models import Post, User, MediaURL, PostLike, PostCategory, FollowRequest
from ...lib.schemas import Post, PostPublic, UserPublic, PostCreate
from ...lib.exceptions import AlreadyLiked, CouldntGetLikes, InvalidPageLength, PostNotFound, InvalidCategory
from ...lib.constants import LIKE_PAGE_LENGTH, FEED_PAGE_LENGTH
from uuid import uuid4
from datetime import datetime
from typing import List
from uuid import uuid4

def is_valid_category(category_str: str) -> bool:
    try:
        PostCategory(category_str)
        return True
    except ValueError:
        return False

# Function to create a new post
def create_post(db: Session, post: PostCreate, author_user_id: int, author_username: str) -> PostPublic:

    post_id_formulated = uuid4()

    """
    print("\n\n\npost is: : ")
    print(post)
    print(post.caption, type(post.caption))
    print(post.post_category, type(post.post_category))
    print(author_user_id, type(author_user_id))
    """

    media_url_objects = []
    for media_url in post.media_urls:
        media_url_object = MediaURL(post_id = post_id_formulated, url = media_url)
        media_url_objects.append(media_url_object)
        db.add(media_url_object)

    # Create a new Post instance
    new_post = Post(
        post_id=post_id_formulated,
        caption=post.caption,  # Assign caption from the request
        post_category=post.post_category,  # Assign post category from the request
        author_user_id=int(author_user_id),  # Set the author user ID
    )
    
    # Add the new post to the session and commit to the database
    db.add(new_post)
    db.commit()
    db.refresh(new_post)  # Refresh the instance to get the latest data from the database

    #print("\n\n\ndb operations done\n\n\n")
    
    return PostPublic(
        post_id=new_post.post_id,
        caption=new_post.caption,
        post_category=new_post.post_category,
        datetime_posted=new_post.datetime_posted.isoformat(),
        author_user_id=new_post.author_user_id,
        author = author_username,
        highlighted_by_author = new_post.highlighted_by_author,
        media_urls = post.media_urls,
        # abhi abhi bani h toh liked kese hogi
        is_liked = False
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
    
    return PostPublic(
        **post.model_dump(),
        is_liked = is_liked,
        author= post.author.username,
        media_urls = map(lambda x: x.url, post.media_urls)
    )


def like_post_repo(post_id: str, liker: UserPublic, db: Session):
    # like a post and return a PostLike

    post_like_existing = db.get(PostLike, (post_id, liker.user_id))
    print("\n\npost like existing: ", post_like_existing)

    if not post_like_existing:
        postLike = PostLike(post_id = post_id, liker_user_id = liker.user_id)
        db.add(postLike)
        db.commit()
        db.refresh(postLike)  # Refresh the instance to get the latest data from the database
        return postLike
    else:
        statement = delete(PostLike).where(and_(PostLike.liker_user_id == liker.user_id, PostLike.post_id == post_id))
        db.execute(statement)
        db.commit()
        print("\n\nUnliked\n\n")
        return PostLike(post_id = '', liker_user_id = 0)


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


def get_feed_repo(current_user: UserPublic, db: Session, category: str = None, page: int = 1) -> List[PostPublic]:

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
                func.group_concat(MediaURL.url).label("media_urls"),
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
                func.group_concat(MediaURL.url).label("media_urls"),
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

    posts = list(map(lambda x: PostPublic(**x[0].model_dump(), author = x[1], media_urls = x[2].split(','), is_liked = True if x[3] is not None else False), posts))

    #print("\n\n\ngot posts: ", posts, type(posts), type(posts[0]))

    
    return posts


# Function to update a post
def update_post(db: Session, post_id: str, updated_data: Post) -> PostPublic:
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
        author_user_id=post.author_user_id
    )

# Function to delete a post
def delete_post(db: Session, post_id: str) -> bool:
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if post is None:
        return False  # Return False if the post is not found
    
    db.delete(post)  # Delete the post from the session
    db.commit()  # Commit the changes to the database
    return True  # Return True to indicate successful deletion

