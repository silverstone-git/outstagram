
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr

from .models import (
    FollowRequest, FollowRequestStatus, Friendship, MediaURL, Post, PostCategory, PostComment, PostLike, User
)


class UserSchema(BaseModel):
    # used for creation, etc.
    fullname: str
    username: str
    bio: Optional[str]
    email: Optional[EmailStr]
    password: str
    date_of_birth: date

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"email": "test@example.com"},
                {"email": "invalid-email"},
                {"email": None},
            ]
        }
    }


class UserProfileSchema(BaseModel):
    user_id: int
    fullname: str
    username: str
    bio: Optional[str]
    posts_count: int
    followers_count: int
    following_count: int

    # 0.5 if the request is pending, 1 is accepted, 0 otherwise
    they_follow_you: float
    you_follow_them: float



class MediaURLSchema(BaseModel):
    post_id: str | None
    url: str
    media_type: str


class PostLikeSchema(BaseModel):
    post_id: str
    liker: UserSchema
    datetime_liked: datetime


class PostLikeUseful(BaseModel):
    post_id: str
    liker_user_id: int
    liker_username: str
    datetime_liked: datetime

class PostCommentSchema(BaseModel):
    comment_id: Optional[int]
    content: str
    author: UserSchema
    datetime_commented: datetime
    likes: Optional[List[PostLikeSchema]]


class PostSchema(BaseModel):
    post_id: Optional[str]
    media_urls: Optional[List[MediaURL]]
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
    media_urls: List[MediaURLSchema]
    highlighted_by_author: bool
    caption: str
    post_category: PostCategory


class PostPublic(BaseModel):
    post_id: Optional[str] # No optional here since it will always be there
    caption: Optional[str]
    post_category: PostCategory
    # in ISO format
    datetime_posted: str
    author_user_id: int
    highlighted_by_author: bool
    is_liked: bool | None
    media_urls: Optional[List[MediaURL]]
    author: str


class UserPublic(BaseModel):
    user_id: int
    username: str
    fullname: str
    bio: Optional[str]


class FollowRequestSchema(BaseModel):
    request_id: Optional[int]
    requester_user_id: int
    requested_user_id: int
    datetime_requested: datetime
    status: FollowRequestStatus


class FollowRequestUseful(FollowRequestSchema):
    requester_username: str


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


