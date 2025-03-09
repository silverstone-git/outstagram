from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel, create_engine, select


class User(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    fullname: str = Field(nullable=False)
    username: str = Field(nullable=False, unique=True, index = True)
    password: str = Field(nullable=False)
    email: str = Field(nullable=False, unique=True, index = True)
    bio: Optional[str] = None
    date_of_birth: Optional[date] = None
    posts: List["Post"] = Relationship(
        back_populates="author",
        cascade_delete= True
    )
    comments: List["PostComment"] = Relationship(
        back_populates="author",
        cascade_delete= True
    )
    likes: List["PostLike"] = Relationship(
        back_populates="liker",
        cascade_delete= True
    )
    comment_likes: List["PostCommentLike"] = Relationship(
        back_populates="liker",
        cascade_delete= True
    )


    follow_requests_sent: List["FollowRequest"] = Relationship(
        back_populates="requester",
        sa_relationship_kwargs={'foreign_keys': 'FollowRequest.requester_user_id'},
        cascade_delete= True
    )
    follow_requests_received: List["FollowRequest"] = Relationship(
        back_populates="requested",
        sa_relationship_kwargs={'foreign_keys': 'FollowRequest.requested_user_id'},
        cascade_delete= True
    )
    friendships1: List["Friendship"] = Relationship(
        back_populates="user1",
        sa_relationship_kwargs={'foreign_keys': 'Friendship.user1_id'},
        cascade_delete= True
    )
    friendships2: List["Friendship"] = Relationship(
        back_populates="user2",
        sa_relationship_kwargs={'foreign_keys': 'Friendship.user2_id'},
        cascade_delete= True
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
    author_user_id: Optional[int] = Field(default=None, foreign_key="user.user_id", ondelete= "CASCADE")
    author: User = Relationship(
        back_populates="posts",
    )
    highlighted_by_author: bool = Field(default=False)

    comments: List["PostComment"] = Relationship(
        back_populates="post",
        cascade_delete= True
    )
    likes: List["PostLike"] = Relationship(
        back_populates="post",
        cascade_delete= True
    )
    media_urls: List["MediaURL"] = Relationship(
        back_populates="post",
        cascade_delete= True
    )

class MediaURL(SQLModel, table=True):

    post_id: Optional[str] = Field(default=None, foreign_key="post.post_id", primary_key = True, ondelete= "CASCADE")
    url: str = Field(nullable=False, primary_key = True)

    post: Post = Relationship(
        back_populates="media_urls",
    )

class PostComment(SQLModel, table=True):
    comment_id: Optional[int] = Field(default=None, primary_key=True)
    post_id: Optional[str] = Field(default=None, foreign_key="post.post_id", ondelete= "CASCADE")
    post: Post = Relationship(
        back_populates="comments",
    )
    content: str = Field(nullable=False)
    author_user_id: Optional[int] = Field(default=None, foreign_key="user.user_id", ondelete= "CASCADE")
    author: User = Relationship(
        back_populates="comments",
    )
    datetime_commented: datetime = Field(default_factory=datetime.utcnow)
    likes: List["PostCommentLike"] = Relationship(back_populates="comment")

class PostLike(SQLModel, table=True):
    post_id: str = Field(foreign_key="post.post_id", primary_key=True, index = True, ondelete= "CASCADE")
    post: Post = Relationship(
        back_populates="likes",
    )
    liker_user_id: int = Field(foreign_key="user.user_id", primary_key=True, ondelete= "CASCADE")
    liker: User = Relationship(
        back_populates="likes",
    )
    datetime_liked: datetime = Field(default_factory=datetime.utcnow)

class PostCommentLike(SQLModel, table=True):
    comment_id: int = Field(foreign_key="postcomment.comment_id", primary_key=True, ondelete= "CASCADE")
    comment: PostComment = Relationship(
        back_populates="likes",
    )
    liker_user_id: int = Field(foreign_key="user.user_id", primary_key=True, ondelete= "CASCADE")
    liker: User = Relationship(
        back_populates="comment_likes",
    )
    datetime_liked: datetime = Field(default_factory=datetime.utcnow)

class FollowRequestStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class FollowRequest(SQLModel, table=True):
    request_id: Optional[int] = Field(default=None, primary_key=True)
    requester_user_id: int = Field(foreign_key="user.user_id", ondelete= "CASCADE")
    requester: User = Relationship(
        back_populates="follow_requests_sent",
        sa_relationship_kwargs={'foreign_keys': '[FollowRequest.requester_user_id]'},
    )
    requested_user_id: int = Field(foreign_key="user.user_id", ondelete= "CASCADE")
    requested: User = Relationship(
        back_populates="follow_requests_received",
        sa_relationship_kwargs={'foreign_keys': '[FollowRequest.requested_user_id]'},
    )
    datetime_requested: datetime = Field(default_factory=datetime.utcnow)
    status: FollowRequestStatus = Field(default="pending")

class Friendship(SQLModel, table=True):
    # should also contain information about 1to2, 2to1, or both-ways
    user1_id: int = Field(foreign_key="user.user_id", primary_key = True, ondelete= "CASCADE")
    user1: User = Relationship(
        back_populates="friendships1",
        sa_relationship_kwargs={'foreign_keys': '[Friendship.user1_id]'},
    )
    user2_id: int = Field(foreign_key="user.user_id", primary_key = True, ondelete= "CASCADE")
    user2: User = Relationship(
        back_populates="friendships2",
        sa_relationship_kwargs={'foreign_keys': '[Friendship.user2_id]'},
    )
    # zero for both-ways, 1 or 2 otherwise
    being_followed: int = Field(default= None)
    datetime_friended: datetime = Field(default_factory=datetime.utcnow)

