from datetime import date, datetime

from enum import Enum
from typing import Annotated, List, Optional
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, Relationship, SQLModel, create_engine, select


class User(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    fullname: str = Field(nullable=False)
    username: str = Field(nullable=False, unique=True, index = True)
    password: str = Field(nullable=False)
    email: str = Field(nullable=False, unique=True, index = True)
    bio: Optional[str] = None
    date_of_birth: Optional[date] = None
    posts: List["Post"] = Relationship(back_populates="author")
    comments: List["PostComment"] = Relationship(back_populates="author")
    likes: List["PostLike"] = Relationship(back_populates="liker")
    comment_likes: List["PostCommentLike"] = Relationship(back_populates="liker")


    follow_requests_sent: List["FollowRequest"] = Relationship(
        back_populates="requester",
        sa_relationship_kwargs={'foreign_keys': 'FollowRequest.requester_user_id'}
    )
    follow_requests_received: List["FollowRequest"] = Relationship(
        back_populates="requested",
        sa_relationship_kwargs={'foreign_keys': 'FollowRequest.requested_user_id'}
    )
    friendships1: List["Friendship"] = Relationship(
        back_populates="user1",
        sa_relationship_kwargs={'foreign_keys': 'Friendship.user1_id'}
    )
    friendships2: List["Friendship"] = Relationship(
        back_populates="user2",
        sa_relationship_kwargs={'foreign_keys': 'Friendship.user2_id'}
    )


class PostCategory(str, Enum):
    tech = "tech"
    entertainment = "entertainment"
    business = "business"
    vlog = "vlog"
    lifestyle = "lifestyle"

class Post(SQLModel, table=True):
    post_id: str = Field(default=None, primary_key=True)
    caption: Optional[str] = None
    post_category: PostCategory = Field(nullable=False)
    datetime_posted: datetime = Field(default_factory=datetime.utcnow)
    author_user_id: Optional[int] = Field(default=None, foreign_key="user.user_id")
    author: User = Relationship(back_populates="posts")
    highlighted_by_author: bool = Field(default=False)

    comments: List["PostComment"] = Relationship(back_populates="post")
    likes: List["PostLike"] = Relationship(back_populates="post")
    media_urls: List["MediaURL"] = Relationship(back_populates="post")

class MediaURL(SQLModel, table=True):

    post_id: Optional[str] = Field(default=None, foreign_key="post.post_id", primary_key = True)
    url: str = Field(nullable=False, primary_key = True)

    post: Post = Relationship(back_populates="media_urls")

class PostComment(SQLModel, table=True):
    comment_id: Optional[int] = Field(default=None, primary_key=True)
    post_id: Optional[str] = Field(default=None, foreign_key="post.post_id")
    post: Post = Relationship(back_populates="comments")
    content: str = Field(nullable=False)
    author_user_id: Optional[int] = Field(default=None, foreign_key="user.user_id")
    author: User = Relationship(back_populates="comments")
    datetime_commented: datetime = Field(default_factory=datetime.utcnow)
    likes: List["PostCommentLike"] = Relationship(back_populates="comment")

class PostLike(SQLModel, table=True):
    post_id: str = Field(foreign_key="post.post_id", primary_key=True, index = True)
    post: Post = Relationship(back_populates="likes")
    liker_user_id: int = Field(foreign_key="user.user_id", primary_key=True)
    liker: User = Relationship(back_populates="likes")
    datetime_liked: datetime = Field(default_factory=datetime.utcnow)

class PostCommentLike(SQLModel, table=True):
    comment_id: int = Field(foreign_key="postcomment.comment_id", primary_key=True)
    comment: PostComment = Relationship(back_populates="likes")
    liker_user_id: int = Field(foreign_key="user.user_id", primary_key=True)
    liker: User = Relationship(back_populates="comment_likes")
    datetime_liked: datetime = Field(default_factory=datetime.utcnow)

class FollowRequestStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class FollowRequest(SQLModel, table=True):
    request_id: Optional[int] = Field(default=None, primary_key=True)
    requester_user_id: int = Field(foreign_key="user.user_id")
    requester: User = Relationship(
        back_populates="follow_requests_sent",
        sa_relationship_kwargs={'foreign_keys': '[FollowRequest.requester_user_id]'}
    )
    requested_user_id: int = Field(foreign_key="user.user_id")
    requested: User = Relationship(
        back_populates="follow_requests_received",
        sa_relationship_kwargs={'foreign_keys': '[FollowRequest.requested_user_id]'}
    )
    datetime_requested: datetime = Field(default_factory=datetime.utcnow)
    status: FollowRequestStatus = Field(default="pending")

class Friendship(SQLModel, table=True):
    # should also contain information about 1to2, 2to1, or both-ways
    friendship_id: Optional[int] = Field(default=None, primary_key=True)
    user1_id: int = Field(foreign_key="user.user_id")
    user1: User = Relationship(
        back_populates="friendships1",
        sa_relationship_kwargs={'foreign_keys': '[Friendship.user1_id]'}
    )
    user2_id: int = Field(foreign_key="user.user_id")
    user2: User = Relationship(
        back_populates="friendships2",
        sa_relationship_kwargs={'foreign_keys': '[Friendship.user2_id]'}
    )
    datetime_friended: datetime = Field(default_factory=datetime.utcnow)

