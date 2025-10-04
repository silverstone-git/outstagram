from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .lib.database_connection import SessionLocal, engine
from .lib.schemas import UserSchema, PostSchema, PostCommentSchema, UserPublic, PostPublic, PostCreate, CommentCreate, PostLikeUseful, FollowRequestUseful, UserProfileSchema, ExamCreate, ExamPublic, ExamPublicList
from .lib.models import PostLike, User, Post, PostComment, PostCategory, Friendship, Exam
from .src.repository.auth import create_user, authenticate_user, create_access_token, authorize
from .src.repository.posts import create_post, get_post, update_post, delete_post, like_post_repo, get_likes, get_feed_repo
from .src.repository.comments import add_comment_repo, get_comments
from .src.repository.users import get_dashboard, get_user_posts_repo, get_user_profile_repo
from .src.repository.frienship import send_follow_request, request_approve_repo, get_follow_requests
from .src.repository.exams import get_all_exams_paginated
from typing import List, Optional, Annotated
from uuid import uuid4
from os import getenv

from sqlmodel import SQLModel

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[getenv("OUTSTAGRAM_ALLOWED_ORIGIN", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    return {"access_token": access_token, "token_type": "bearer", "user": user}


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
async def update_existing_post(post_id: str, post: Post, current_user: UserPublic = Depends(get_current_user), db: Session = Depends(get_db)):
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
@app.get("/users/{username}", response_model=UserProfileSchema)
async def get_user_profile(
    username: str,
    current_user: UserPublic = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_user_profile_repo(target_username = username, current_user = current_user, db = db)


# Endpoint the see all follow requests
@app.get("/follow-requests", response_model = list[FollowRequestUseful])
async def get_follow_requests_endpoint(
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
    request_id: int,
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
    page: int | None = Query(None, description="Page number for pagination"),
    category: str | None = Query(None, description="Filter by category"),
    current_user: UserPublic = Depends(get_current_user), 
    db: Session = Depends(get_db)
):

    return get_feed_repo(page=page, category=category, current_user=current_user, db=db)


@app.post("/pariksha", response_model=ExamPublic, status_code=status.HTTP_201_CREATED)
async def create_exam(exam_data: ExamCreate, db: Session = Depends(get_db)):
    new_exam = Exam(exam_id=str(uuid4()), exam_title=exam_data.exam_title, exam_json_str=exam_data.exam_json_str)
    db.add(new_exam)
    db.commit()
    db.refresh(new_exam)
    return new_exam


@app.get("/pariksha", response_model=List[ExamPublicList])
async def get_all_exams(page: int = 1, db: Session = Depends(get_db)):
    exams_from_db = get_all_exams_paginated(db=db, page=page)
    return [
        ExamPublicList(
            exam_id=exam.exam_id,
            exam_title=exam.exam_title,
            datetime_uploaded=exam.datetime_uploaded
        ) for exam in exams_from_db
    ]


@app.get("/pariksha/{exam_id}", response_model=ExamPublic)
async def get_exam_by_id(exam_id: str, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.exam_id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")
    return exam

