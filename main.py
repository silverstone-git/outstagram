from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .lib.database_connection import SessionLocal, engine
from .lib.schemas import UserSchema, PostSchema, PostCommentSchema, UserPublic, PostPublic, PostCreate, CommentCreate, PostLikeUseful, FollowRequestUseful
from .lib.models import PostLike, User, Post, PostComment, PostCategory, Friendship
from .src.repository.auth import create_user, authenticate_user, create_access_token, authorize
from .src.repository.posts import create_post, get_post, get_all_posts, update_post, delete_post, like_post_repo, get_likes
from .src.repository.comments import add_comment_repo, get_comments
from .src.repository.users import get_dashboard, get_user_posts_repo
from .src.repository.frienship import send_follow_request, request_approve_repo, get_follow_requests
from typing import List, Optional, Annotated

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


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)) -> UserPublic | None:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = authorize(token, db, credentials_exception)

    if user is None:
        raise credentials_exception
    #print("\n \t ...returning ... \n")
    return user



# Endpoint for user registration
@app.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(user: UserSchema, db: Session = Depends(get_db)):
    return create_user(db=db, user=user)



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
async def create_new_post(post: PostCreate, current_user: UserPublic = Depends(get_current_user), db: Session = Depends(get_db)):

    return create_post(db=db, post=post, author_user_id=int(current_user.user_id), author_username = current_user.username)


# Endpoint to like a post
@app.post("/posts/{post_id}/like", response_model=PostLike, status_code=status.HTTP_201_CREATED)
def like_post(post_id: str, current_user: UserPublic = Depends(get_current_user), db: Session = Depends(get_db)):

    #print("\n\n\n in like post, current user is: ", current_user)
    return like_post_repo(post_id, current_user, db)


# Endpoint to comment on a post
@app.post("/posts/{post_id}/comment", response_model=PostComment, status_code=status.HTTP_201_CREATED)
def create_comment(post_id: str, comment_data: CommentCreate, current_user: UserPublic = Depends(get_current_user), db: Session = Depends(get_db)):

    return add_comment_repo(comment_data.content, post_id, current_user, db)


# Endpoint to see likes, page by page
@app.get("/posts/{post_id}/likes/{page}", response_model=list[PostLikeUseful])
def get_post_likes(post_id: str, page: int, current_user: UserPublic = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_likes(post_id, db, page)


# Endpoint to see comments, page by page
@app.get("/posts/{post_id}/comments/{page}", response_model=list[PostComment])
def get_post_comments(post_id: str, page: int, current_user: UserPublic = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_comments(post_id, db, page)


# Endpoint to get a post by ID
@app.get("/posts/{post_id}", response_model=PostPublic)
async def read_post(post_id: str, current_user: UserPublic = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_post(post_id=post_id, current_user=current_user, db=db)


# Endpoint to see all the logged in user's posts, along with user data
@app.get("/dashboard/{page}")
async def dashboard(page: int, current_user: UserPublic = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_dashboard(user = current_user, db=db, page = page)


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


# Endpoint the see all follow requests
@app.get("/follow-requests", response_model = list[FollowRequestUseful])
async def follow_user(
    current_user: UserPublic = Depends(get_current_user), 
    db: Session = Depends(get_db)
):

    return get_follow_requests(current_user, db)


# Endpoint to follow a user
@app.post("/users/{username}/follow", status_code=status.HTTP_201_CREATED)
async def follow_user(
    username: str,
    current_user: UserPublic = Depends(get_current_user), 
    db: Session = Depends(get_db)
):

    return send_follow_request(username, current_user, db)


# Endpoint to approve a request_id
@app.post("/request-approve/{request_id}", response_model = Friendship, status_code=status.HTTP_201_CREATED)
async def request_approve(
    request_id: str,
    current_user: UserPublic = Depends(get_current_user), 
    db: Session = Depends(get_db)
):

    return request_approve_repo(request_id, current_user, db)


# Endpoint to Get user's posts
@app.get("/users/{username}/posts/{page}", response_model=List[PostPublic])
async def get_user_posts(
    username: str,
    page: int,
    current_user: UserPublic = Depends(get_current_user), 
    db: Session = Depends(get_db),
):

    return get_user_posts_repo(username = username, current_user = current_user, db = db, page = page)





# Endpoint to get all posts of followed users, paginated reverse chronological, friends first
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

