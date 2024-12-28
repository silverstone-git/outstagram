
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr

from .models import (
    FollowRequest, FollowRequestStatus, Friendship, MediaURL, Post, PostCategory, PostComment, PostLike, User
)


class UserSchema(BaseModel):
    user_id: Optional[int]
    fullname: str
    email: Optional[EmailStr]
    username: str
    bio: Optional[str]
    date_of_birth: Optional[date]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"email": "test@example.com"},
                {"email": "invalid-email"},
                {"email": None},
            ]
        }
    }


class MediaURLSchema(BaseModel):
    post_id: str
    url: str


class PostLikeSchema(BaseModel):
    post_id: int
    liker: UserSchema
    datetime_liked: datetime


class PostCommentSchema(BaseModel):
    comment_id: Optional[int]
    content: str
    author: UserSchema
    datetime_commented: datetime
    likes: Optional[List[PostLikeSchema]]


class PostSchema(BaseModel):
    post_id: Optional[str]
    media_urls: Optional[List[MediaURLSchema]]
    caption: Optional[str]
    post_category: PostCategory
    datetime_posted: datetime
    author: UserSchema
    highlighted_by_author: bool
    comments: Optional[List[PostCommentSchema]]
    likes: Optional[List[PostLikeSchema]]


class CommentCreate(BaseModel):
    content: str


class PostCreate(BaseModel):
    media_urls: List[str]
    highlighted_by_author: bool
    caption: str
    post_category: PostCategory


class PostPublic(BaseModel):
    post_id: Optional[str] # No optional here since it will always be there
    caption: Optional[str]
    post_category: PostCategory
    datetime_posted: datetime
    author: str
    highlighted_by_author: bool
    media_urls: Optional[List[str]]


class UserPublic(BaseModel):
    user_id: int
    username: str
    fullname: str
    bio: Optional[str]


class FollowRequestSchema(BaseModel):
    request_id: Optional[int]
    requester: UserSchema
    requested: UserSchema
    datetime_requested: datetime
    status: FollowRequestStatus


class FriendshipSchema(BaseModel):
    friendship_id: Optional[int]
    user1: UserSchema
    user2: UserSchema
    datetime_friended: datetime


# Schemas with optional fields for partial updates
class UserUpdateSchema(BaseModel):
    fullname: Optional[str]
    bio: Optional[str]
    date_of_birth: Optional[date]


class PostUpdateSchema(BaseModel):
    caption: Optional[str]
    highlighted_by_author: Optional[bool]


class PostCommentUpdateSchema(BaseModel):
    content: Optional[str]


