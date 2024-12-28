
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel

from .models import (  # Assuming models.py resides in the same directory
    FollowRequest, FollowRequestStatus, Friendship, MediaURL, Post, PostCategory, PostComment, PostLike, User
)


class UserSchema(BaseModel):
    user_id: Optional[int]
    fullname: str
    username: str
    bio: Optional[str]
    date_of_birth: Optional[date]


class MediaURLSchema(BaseModel):
    media_url_id: Optional[int]
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
    post_id: Optional[int]
    media_urls: Optional[List[MediaURLSchema]]
    caption: Optional[str]
    post_category: PostCategory
    datetime_posted: datetime
    author: UserSchema
    highlighted_by_author: bool
    comments: Optional[List[PostCommentSchema]]
    likes: Optional[List[PostLikeSchema]]


class PostPublic(BaseModel):
    post_id: int # No optional here since it will always be there
    caption: Optional[str]
    post_category: PostCategory
    datetime_posted: datetime
    author: UserSchema # Assuming you have a UserSchema
    highlighted_by_author: bool
    media_urls: Optional[List[MediaURLSchema]]


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


