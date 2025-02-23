from sqlalchemy.orm import Session
from ...lib.schemas import UserPublic, FollowRequestUseful
from ...lib.models import User, FollowRequest, FollowRequestStatus, Friendship
from fastapi import HTTPException
from sqlalchemy import select, and_, or_
from sqlalchemy.exc import SQLAlchemyError

def send_follow_request(target_username: str, current_user: UserPublic, db: Session):

    target_user = db.query(User).filter(User.username == target_username).first()
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

    print("follow request formulated: ", follow_request)
    
    # will be shown in GET /follow-requests of the target user
    
    db.add(follow_request)
    db.commit()
    
    return {"message": "Follow request sent"}


def get_follow_requests(current_user: UserPublic, db: Session):
    # query the FollowRequest model and get the pending requests addressed to the current user
    statement = (
        select(FollowRequest, User.username)
        .join(User, FollowRequest.requester_user_id == User.user_id)
        .where(FollowRequest.requested_user_id == current_user.user_id)
        .where(FollowRequest.status == FollowRequestStatus.pending) # Assuming FollowRequestStatus is an Enum
    )

    #try:
    pending_requests = db.execute(statement).all()
    #except:
    #    raise HTTPException(status_code=500, detail="Couldn't find pending follow request")
    requests_with_usernames = list([
        FollowRequestUseful(
            **request.model_dump(),
            requester_username = requester_username
        )
        for request, requester_username in pending_requests
    ])
    #print("\n\n\ngot pending: ")
    #print(requests_with_usernames)
    #print("type: ", type(requests_with_usernames))
    #print("type of 0th: ", type(requests_with_usernames[0]), "\n\n")
    return requests_with_usernames


def request_approve_repo(request_id: int, current_user: UserPublic, db: Session):

    # First, get and validate the follow request for the current user, if its still pending
    follow_request = db.query(FollowRequest).filter(
        FollowRequest.request_id == request_id,
        FollowRequest.requested_user_id == current_user.user_id,
        FollowRequest.status == FollowRequestStatus.pending
    ).first()
    
    if not follow_request:
        raise HTTPException(
            status_code=404,
            detail="Follow request not found or not pending"
        )
    
    # Check if friendship already exists to avoid duplicates
    existing_friendship = db.query(Friendship).filter(
        or_(
            and_(
                Friendship.user1_id == follow_request.requester_user_id,
                Friendship.user2_id == current_user.user_id
            ),
            and_(
                Friendship.user1_id == current_user.user_id,
                Friendship.user2_id == follow_request.requester_user_id
            )
        )
    ).first()
    
    if existing_friendship:
        raise HTTPException(
            status_code=400,
            detail="Friendship already exists"
        )
    

    try:
        # Update the follow request status to accepted
        follow_request.status = FollowRequestStatus.accepted
        
        # Create new friendship record
        new_friendship = Friendship(
            user1_id=follow_request.requester_user_id,
            user2_id=current_user.user_id,
            being_followed=2
        )
        
        # Add and commit both changes
        db.add(new_friendship)
        db.commit()
        db.refresh(new_friendship)

        #print("\n\n new friendship record is: ", new_friendship)
        
        return new_friendship
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error while approving request"
        )
