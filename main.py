from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ./lib/database_connection import SessionLocal, engine
from ./lib/schemas import UserCreate, UserPublic, PostCreate, PostPublic
from ./src/repository/auth import create_user, authenticate_user, create_access_token
from ./src/repository/post_operations import create_post, get_post, get_all_posts, update_post, delete_post

from sqlmodel import SQLModel

# Create the FastAPI app
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

# Endpoint for user registration
@app.post("/register", response_model=UserPublic)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db=db, user=user)


# Endpoint for user login and token generation
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db=db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token(data={"username": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# Endpoint to create a new post
@app.post("/posts", response_model=PostPublic)
async def create_new_post(post: PostCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    
    user = authorize(token)
    if user:
        return create_post(db=db, post=post, author_user_id=user.user_id)
    else:
        raise HTTPException(status_code=403, detail="Forbidden")

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
async def update_existing_post(post_id: str, post: PostCreate, db: Session = Depends(get_db)):
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

