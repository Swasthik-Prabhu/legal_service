from beanie import Document
from datetime import datetime
from pydantic import BaseModel

class Message(Document):
    case_id: str  # The case associated with the message
    sender: str   # Username of the sender (client or lawyer)
    receiver: str # Username of the receiver (client or lawyer)
    message: str  # Message content
    timestamp: datetime = datetime.utcnow()  # Auto timestamp

    class Settings:
        collection = "messages"  # MongoDB collection name

    def to_dict(self):
        return {
            "id": str(self.id),
            "case_id": self.case_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }

class MessageCreate(BaseModel):
    message: str  # Only message content is required in request body
