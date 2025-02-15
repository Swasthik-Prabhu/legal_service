from models.notification import Notification
from datetime import datetime

async def create_notification(recipient: str, message: str, case_id: str |None, notification_type: str = "general"):
    """
    Create and store a new notification for a user.
    
    :param recipient: Username of the recipient
    :param message: Notification message
    :param case_id: Associated case ID (if applicable)
    :param notification_type: Type of notification (e.g., "new_case", "case_accepted", "case_update")
    """
    notification = Notification(
        recipient=recipient,
        message=message,
        case_id=case_id,
        notification_type=notification_type,
        timestamp=datetime.utcnow(),
        read=False  # Default: unread notification
    )
    await notification.insert()

async def get_notifications(user: str):
    """
    Retrieve all unread notifications for a user.
    :param user: Username of the recipient
    :return: List of notifications
    """
    notifications = await Notification.find(Notification.recipient == user, Notification.read == False).to_list()
    return [n.to_dict() for n in notifications]

async def mark_notification_as_read(notification_id: str):
    """
    Mark a notification as read.
    :param notification_id: ID of the notification
    """
    notification = await Notification.get(notification_id)
    if notification:
        notification.read = True
        await notification.save()
