from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Dict
from models.message import Message, MessageCreate
from models.case import Case
from services.auth_service import get_current_user
from typing import List

router = APIRouter()
active_connections: Dict[str, WebSocket] = {}  # Store active connections

@router.websocket("/ws/{case_id}/{username}")
async def websocket_endpoint(websocket: WebSocket, case_id: str, username: str, current_user=Depends(get_current_user)):
    await websocket.accept()

    # Check if user is authorized for this case
    case = await Case.find_one(Case.id == case_id)
    if not case or (current_user.username != case.client and current_user.username != case.lawyer):
        await websocket.close()
        return

    active_connections[username] = websocket  # Store active connection

    try:
        while True:
            data = await websocket.receive_json()  # Receive message
            message = Message(
                case_id=case_id,
                sender=current_user.username,
                receiver=data["receiver"],
                message=data["message"]
            )
            await message.insert()  # Save to MongoDB

            # Send message if receiver is online
            if data["receiver"] in active_connections:
                await active_connections[data["receiver"]].send_json(message.to_dict())

    except WebSocketDisconnect:
        del active_connections[username]  # Remove connection on disconnect



@router.get("/messages/{case_id}", response_model=List[Message])
async def get_case_messages(case_id: str, current_user=Depends(get_current_user)):
    # Check if the user is authorized for this case
    case = await Case.find_one(Case.id == case_id)
    if not case or (current_user.username != case.client and current_user.username != case.lawyer):
        raise HTTPException(status_code=403, detail="Access denied")

    # Retrieve all messages for the case, sorted by timestamp
    messages = await Message.find(Message.case_id == case_id).sort("timestamp").to_list()
    
    return messages
