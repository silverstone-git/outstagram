from sqlalchemy.orm import Session
from ...lib.schemas import UserPublic
from ...lib.models import User

def send_follow_request(target_user_id: int, current_user: UserPublic, db: Session):

    target_user = db.query(User).filter(User.username == target_user_id).first()
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
    
    # will be shown in GET /follow-requests of the target user
    
    db.add(follow_request)
    db.commit()
    
    return {"message": "Follow request sent"}


def get_follow_requests(current_user: UserPublic, db: Session):
    # query the FollowRequest model and get the pending requests addressed to the current user
    return


def request_approve_repo(request_id: int, current_user: UserPublic, db: Session):
    # approve the request, change the status and make a new record in friendship table
    return
