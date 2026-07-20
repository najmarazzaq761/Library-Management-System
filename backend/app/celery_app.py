from celery import Celery
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.config import settings
from app.models import Loan, Notification

celery = Celery(
    "tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)


@celery.task
def create_overdue_notifications():
    """Scan active/non-returned book loans and record overdue warnings."""
    db: Session = SessionLocal()
    try:
        active_loans = db.query(Loan).filter(
            Loan.is_returned.is_(False)
        ).all()

        for loan in active_loans:
            msg = (
                f"Warning: Your loan for '{loan.book.title}' borrowed on "
                f"{loan.borrowed_at.strftime('%Y-%m-%d %H:%M:%S')} needs to "
                f"be returned as soon as possible."
            )

            # Check if notification already exists to avoid duplicate warnings
            exists = db.query(Notification).filter(
                Notification.member_id == loan.member_id,
                Notification.message.like(f"%'{loan.book.title}'%"),
                Notification.is_read.is_(False)
            ).first()

            if not exists:
                notif = Notification(
                    member_id=loan.member_id,
                    message=msg
                )
                db.add(notif)

        db.commit()
    except Exception as e:
        print(f"Error in Celery overdue task execution: {e}")
        db.rollback()
    finally:
        db.close()
