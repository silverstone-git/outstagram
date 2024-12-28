from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .lib.database_connection import SessionLocal, engine
from .lib.schemas import UserSchema, PostSchema, PostCommentSchema, UserPublic, PostPublic
from .lib.models import PostLike, User, Post, PostComment, PostCategory
from .src.repository.auth import create_user, authenticate_user, create_access_token
from .src.repository.post_operations import create_post, get_post, get_all_posts, update_post, delete_post
from typing import List, Optional

from sqlmodel import SQLModel

app = FastAPI()

# Create the database tables
SQLModel.metadata.create_all(engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@app.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(user: User, db: Session = Depends(get_db)):
    return create_user(db=db, user=user)



@app.post("/posts/{post_id}/like/{user_id}", response_model=PostLike, status_code=status.HTTP_201_CREATED)
def like_post(post_id: int, user_id: int):
    with Session(engine) as session:
        post = session.get(Post, post_id)
        user = session.get(User, user_id)
        if not post or not user:
            raise HTTPException(status_code=404, detail="Post or User not found")

        like = PostLike(post=post, user=user)
        session.add(like)
        session.commit()
        session.refresh(like)
        return like


@app.post("/posts/{post_id}/comment/{user_id}", response_model=PostComment, status_code=status.HTTP_201_CREATED)
def create_comment(post_id: int, user_id: int, comment_content: str):
    with Session(engine) as session:
        post = session.get(Post, post_id)
        user = session.get(User, user_id)
        if not post or not user:
            raise HTTPException(status_code=404, detail="Post or User not found")

        comment = PostComment(post=post, user=user, content=comment_content)
        session.add(comment)
        session.commit()
        session.refresh(comment)
        return comment


# Endpoint for user login and token generation
@app.post("/login", status_code=status.HTTP_200_OK)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db=db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token(data={"username": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# Endpoint to create a new post
@app.post("/posts", response_model=PostPublic)
async def create_new_post(post: Post, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    
    user = authorize(token, db)
    if user:
        return create_post(db=db, post=post, author_user_id=user.user_id)
    else:
        raise HTTPException(status_code=403, detail="Forbidden")



@app.get("/posts/{post_id}/likes", response_model=list[PostLike])
def get_post_likes(post_id: int):
    with Session(engine) as session:
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return post.likes


@app.get("/posts/{post_id}/comments", response_model=list[PostComment])
def get_post_comments(post_id: int):
    with Session(engine) as session:
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return post.comments


# Endpoint to get a post by ID
@app.get("/posts/{post_id}", response_model=PostPublic)
async def read_post(post_id: str, db: Session = Depends(get_db)):
    post = get_post(db=db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post



# Endpoint to get all posts
@app.get("/posts", response_model=List[PostPublic])
async def read_all_posts(db: Session = Depends(get_db)):
    return get_all_posts(db=db)



# Endpoint to update a post
@app.put("/posts/{post_id}", response_model=PostPublic)
async def update_existing_post(post_id: str, post: Post, db: Session = Depends(get_db)):
    updated_post = update_post(db=db, post_id=post_id, updated_data=post)
    if updated_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return updated_post


# Endpoint to delete a post
@app.delete("/posts/{post_id}", response_model=dict)
async def delete_existing_post(post_id: str, db: Session = Depends(get_db)):
    success = delete_post(db=db, post_id=post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"detail": "Post deleted successfully"}



# Endpoint to get a user (public)
@app.get("/users/{username}", response_model=UserPublic)
async def get_user_profile(
    username: str,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    posts_count = db.query(Post).filter(Post.author_user_id == user.user_id).count()
    followers_count = db.query(FollowRequest).filter(
        FollowRequest.requested_user_id == user.user_id,
        FollowRequest.status == "accepted"
    ).count()
    following_count = db.query(FollowRequest).filter(
        FollowRequest.requester_user_id == user.user_id,
        FollowRequest.status == "accepted"
    ).count()
    
    is_following = db.query(FollowRequest).filter(
        FollowRequest.requester_user_id == current_user.user_id,
        FollowRequest.requested_user_id == user.user_id,
        FollowRequest.status == "accepted"
    ).first() is not None
    
    return {
        **user.dict(),
        "posts_count": posts_count,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following
    }


@app.post("/users/{username}/follow", status_code=status.HTTP_201_CREATED)
async def follow_user(
    username: str,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    user = authorize(token, db)

    if not user :
        raise HTTPException(status_code=403, detail="Forbidden")
        return;

    target_user = db.query(User).filter(User.username == username).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if target_user.user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    existing_request = db.query(FollowRequest).filter(
        FollowRequest.requester_user_id == current_user.user_id,
        FollowRequest.requested_user_id == target_user.user_id
    ).first()
    
    if existing_request:
        if existing_request.status == "accepted":
            raise HTTPException(status_code=400, detail="Already following this user")
        elif existing_request.status == "pending":
            raise HTTPException(status_code=400, detail="Follow request already pending")
    
    follow_request = FollowRequest(
        requester_user_id=current_user.user_id,
        requested_user_id=target_user.user_id,
        status="pending"
    )
    
    db.add(follow_request)
    db.commit()
    
    return {"message": "Follow request sent"}



# Endpoint to Get user's posts
@app.get("/users/{username}/posts", response_model=List[PostPublic])
async def get_user_posts(
    username: str,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    posts = db.query(Post).filter(Post.author_user_id == user.user_id).all()
    
    # Add is_liked status for each post
    for post in posts:
        post.is_liked = db.query(PostLike).filter(
            PostLike.post_id == post.post_id,
            PostLike.liker_user_id == current_user.user_id
        ).first() is not None
    
    return posts


# Edpoint( protected) for liking post
@app.post("/posts/{post_id}/like")
async def toggle_post_like(
    post_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    user = authorize(token)
    if not user:
        raise HTTPException(status_code=403, detail="Forbidden")

    post = db.query(Post).filter(Post.post_id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    existing_like = db.query(PostLike).filter(
        PostLike.post_id == post_id,
        PostLike.liker_user_id == current_user.user_id
    ).first()
    
    if existing_like:
        db.delete(existing_like)
        message = "Post unliked successfully"
    else:
        like = PostLike(
            post_id=post_id,
            liker_user_id=current_user.user_id
        )
        db.add(like)
        message = "Post liked successfully"
    
    db.commit()
    return {"message": message}


# 7. Like/Unlike comment
@app.post("/comments/{comment_id}/like")
async def toggle_comment_like(
    comment_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    
    user = authorize(token, db)

    if not user :
        raise HTTPException(status_code=403, detail="Forbidden")
        return;

    comment = db.query(PostComment).filter(PostComment.comment_id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    existing_like = db.query(PostCommentLike).filter(
        PostCommentLike.comment_id == comment_id,
        PostCommentLike.liker_user_id == current_user.user_id
    ).first()
    
    if existing_like:
        db.delete(existing_like)
        message = "Comment unliked successfully"
    else:
        like = PostCommentLike(
            comment_id=comment_id,
            liker_user_id=current_user.user_id
        )
        db.add(like)
        message = "Comment liked successfully"
    
    db.commit()
    return {"message": message}

# 8. Get user feed (paginated)
@app.get("/feed", response_model=List[PostPublic])
async def get_feed(
    page: int = Query(1, gt=0),
    token: str = Depends(oauth2_scheme),
    limit: int = Query(10, gt=0, le=50),
    category: Optional[PostCategory] = None,
    db: Session = Depends(get_db)
):

    user = authorize(token, db)

    if not user :
        raise HTTPException(status_code=403, detail="Forbidden")
        return;

    # Get users that current user follows
    following_ids = db.query(FollowRequest.requested_user_id).filter(
        FollowRequest.requester_user_id == current_user.user_id,
        FollowRequest.status == "accepted"
    ).all()
    following_ids = [id for (id,) in following_ids]
    
    # Base query
    query = db.query(Post).filter(Post.author_user_id.in_(following_ids))
    
    # Apply category filter if provided
    if category:
        query = query.filter(Post.post_category == category)
    
    # Apply pagination and ordering
    posts = query.order_by(
        desc(Post.datetime_posted)
    ).offset(
        (page - 1) * limit
    ).limit(limit).all()
    
    # Add is_liked status for each post
    for post in posts:
        post.is_liked = db.query(PostLike).filter(
            PostLike.post_id == post.post_id,
            PostLike.liker_user_id == current_user.user_id
        ).first() is not None
    
    return posts

