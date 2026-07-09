import time

def send_overdue_email(member_email: str, member_name: str, book_title: str, borrowed_at: str, days_overdue: int = 5):
    """Simulates sending an overdue warning email with network delay."""
    time.sleep(2)  # Simulate network latency of SMTP delivery
    print(f"📧 NOTIFICATION: Book '{book_title}' is overdue!")
    print(f"   Member: {member_name} ({member_email})")
    print(f"   Borrowed on: {borrowed_at}")
    print(f"   Days overdue: {days_overdue}")
    print(f"   [SIMULATION] Email sent to {member_email}\n", flush=True)
