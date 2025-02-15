from fastapi import APIRouter, Depends, HTTPException
from models.case import Case, CaseCreate, CaseUpdate
from models.user import User
from database import init_db
from services.auth_service import get_current_user
from typing import List

router = APIRouter()

#  Create a new case (Only Clients)
@router.post("/create_case", response_model=dict)
async def create_case(case_data: CaseCreate, current_user: User = Depends(get_current_user)):
    
    await init_db()

    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="Only clients can create cases")

    case = Case(**case_data.dict(), client_username=current_user.username)
    await case.insert()
    return {"message": "Case created successfully", "case": case.to_dict()}

#  List all cases (Only Lawyers)

@router.get("/list_cases", response_model=List[dict])
async def list_cases(current_user: User = Depends(get_current_user)):
    await init_db()

    if current_user.role == "client":
        cases = await Case.find(Case.client_username == current_user.username).to_list()
    elif current_user.role == "lawyer":
        cases = await Case.find(Case.status == "pending").to_list()
    else:
        raise HTTPException(status_code=403, detail="Access denied")

    return [case.to_dict() for case in cases]


#  Get case details (Only Clients & Assigned Lawyers)
@router.get("/{case_id}", response_model=dict)
async def get_case(case_id: str, current_user: User = Depends(get_current_user)):
    await init_db()
    case = await Case.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    if current_user.username not in [case.client_username, case.lawyer_username]:
        raise HTTPException(status_code=403, detail="Access denied")

    return case.to_dict()

#  Accept a case (Only Lawyers)
@router.put("/{case_id}/accept", response_model=dict)
async def accept_case(case_id: str, current_user: User = Depends(get_current_user)):
    await init_db()

    if current_user.role != "lawyer":
        raise HTTPException(status_code=403, detail="Only lawyers can accept cases")

    case = await Case.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    if case.lawyer_username:
        raise HTTPException(status_code=400, detail="Case already assigned to a lawyer")

    case.lawyer_username = current_user.username
    case.status = "accepted"
    await case.save()
    return {"message": "Case accepted successfully", "case": case.to_dict()}

# Update case status (Only Assigned Lawyer)
@router.put("/{case_id}/status", response_model=dict)
async def update_case_status(case_id: str, update_data: CaseUpdate, current_user: User = Depends(get_current_user)):
    await init_db()
    case = await Case.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    if case.lawyer_username != current_user.username:
        raise HTTPException(status_code=403, detail="Only the assigned lawyer can update status")

    if update_data.status:
        case.status = update_data.status
        await case.save()

    return {"message": "Case status updated", "case": case.to_dict()}
