from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role
from app import schemas, models
from app.services import notifications as notifications_service

router = APIRouter(tags=["Notifications"])


@router.post("/loans/overdue/notify", status_code=202)
def check_and_notify_overdue_loans(
    current_user: models.Member = Depends(require_role(["librarian"]))
):
    """Trigger background overdue warnings via Celery (Librarian only)."""
    from app.celery_app import check_and_create_overdue_notifications

    task = check_and_create_overdue_notifications.delay()
    return {
        "status": "Celery warning scanner dispatched",
        "task_id": task.id,
        "message": "Scans are processing asynchronously via Redis/Celery."
    }


@router.get("/notifications", response_model=list[schemas.NotificationSchema])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: models.Member = Depends(
        require_role(["member", "librarian"])
    )
):
    """Get active unread warnings for the logged-in member."""
    return notifications_service.get_active_notifications(db, current_user.id)


@router.post("/notifications/{notif_id}/read")
def mark_notification_read(
    notif_id: int,
    db: Session = Depends(get_db),
    current_user: models.Member = Depends(
        require_role(["member", "librarian"])
    )
):
    """Mark a notification as read/acknowledged."""
    return notifications_service.read_notification(db, notif_id, current_user)
