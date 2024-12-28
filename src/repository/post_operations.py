
from sqlalchemy.orm import Session
from ...lib.models import Post, User
from ...lib.schemas import Post, PostPublic
from uuid import uuid4
from datetime import datetime
from typing import List


# Function to create a new post
def create_post(db: Session, post: Post, author_user_id: str) -> PostPublic:
    # Create a new Post instance
    new_post = Post(
        #post_id=str(uuid4()),   Generate a new unique post ID
        media_urls=post.media_urls,  # Assign media URLs from the request
        caption=post.caption,  # Assign caption from the request
        post_category=post.post_category,  # Assign post category from the request
        author_user_id=author_user_id,  # Set the author user ID
        datetime_posted=datetime.utcnow()  # Set the current timestamp
    )
    
    # Add the new post to the session and commit to the database
    db.add(new_post)
    db.commit()
    db.refresh(new_post)  # Refresh the instance to get the latest data from the database
    
    return PostPublic(
        #post_id=new_post.post_id,
        media_urls=new_post.media_urls,
        caption=new_post.caption,
        post_category=new_post.post_category,
        datetime_posted=new_post.datetime_posted.isoformat(),
        author_user_id=new_post.author_user_id
    )

# Function to retrieve a post by its ID
def get_post(db: Session, post_id: str) -> PostPublic:
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if post is None:
        return None  # Return None if the post is not found
    
    return PostPublic(
        post_id=post.post_id,
        media_urls=post.media_urls,
        caption=post.caption,
        post_category=post.post_category,
        datetime_posted=post.datetime_posted.isoformat(),
        author_user_id=post.author_user_id
    )

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

