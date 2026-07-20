from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.member import Member


def get_active_notifications(
    db: Session, user_id: int
) -> list[Notification]:
    """Get active unread warnings for the logged-in member."""
    return db.query(Notification).filter(
        Notification.member_id == user_id,
        Notification.is_read.is_(False)
    ).order_by(Notification.created_at.desc()).all()


def read_notification(
    db: Session, notif_id: int, current_user: Member
) -> dict:
    """Mark a notification as read/acknowledged."""
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification {notif_id} not found."
        )

    # Security check: members can only dismiss their own notifications
    if current_user.role != "librarian" and notif.member_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot dismiss other users' alerts."
        )

    notif.is_read = True
    db.commit()
    return {"message": "Notification cleared successfully."}
