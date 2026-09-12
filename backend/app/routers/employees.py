from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.employee import Employee
from app.models.assignment import Assignment
from app.models.task import Task
from app.schemas.employee import EmployeeCreate, EmployeeRead, EmployeeUpdate, WorkloadSummary
from app.schemas.assignment import AssignmentRead
from app.services.jira_service import JiraClient

router = APIRouter()

@router.get("/", response_model=list[EmployeeRead])
async def list_employees(
    department: str = None, 
    availability: str = None, 
    skip: int = 0, 
    limit: int = 50, 
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Employee)
    if department: stmt = stmt.where(Employee.department == department)
    if availability: stmt = stmt.where(Employee.availability_status == availability)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/", response_model=EmployeeRead)
async def create_employee(emp_in: EmployeeCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(Employee).where(Employee.email == emp_in.email)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
        
    emp = Employee(**emp_in.model_dump())
    db.add(emp)
    await db.commit()
    await db.refresh(emp)
    return emp

@router.put("/{employee_id}", response_model=EmployeeRead)
async def update_employee(employee_id: int, emp_in: EmployeeUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(Employee).where(Employee.id == employee_id)
    result = await db.execute(stmt)
    emp = result.scalars().first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    for k, v in emp_in.model_dump(exclude_unset=True).items():
        setattr(emp, k, v)
        
    db.add(emp)
    await db.commit()
    await db.refresh(emp)
    return emp

@router.get("/{employee_id}/workload", response_model=WorkloadSummary)
async def get_workload(employee_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Employee).where(Employee.id == employee_id)
    result = await db.execute(stmt)
    emp = result.scalars().first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    # Count active assignments
    stmt_assign = select(func.count(Assignment.id)).where(
        Assignment.employee_id == employee_id,
        Assignment.status == 'active'
    )
    res_assign = await db.execute(stmt_assign)
    active_count = res_assign.scalar() or 0
    
    return WorkloadSummary(
        employee_id=emp.id,
        name=emp.name,
        current_workload_score=emp.current_workload_score,
        active_task_count=active_count,
        availability_status=emp.availability_status
    )

@router.get("/{employee_id}/history", response_model=list[AssignmentRead])
async def get_history(employee_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Assignment).where(Assignment.employee_id == employee_id)
    result = await db.execute(stmt)
    return result.scalars().all()


# ===================== JIRA SYNC ENDPOINTS =====================

@router.post("/jira/sync")
async def sync_employees_from_jira(db: AsyncSession = Depends(get_db)):
    """Pull all team members from Jira and create/link them as TITANS employees."""
    jira = JiraClient()
    if not jira.is_configured():
        raise HTTPException(
            status_code=400,
            detail="Jira not configured.",
        )

    try:
        jira_users = await jira.fetch_all_users()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch Jira users: {str(e)}")

    all_employees = (await db.execute(select(Employee))).scalars().all()
    created = 0
    linked = 0

    for jira_user in jira_users:
        account_id = jira_user["account_id"]
        display_name = jira_user["display_name"]
        email = jira_user["email"]

        # Skip if already linked by account_id
        already_linked = any(e.jira_account_id == account_id for e in all_employees)
        if already_linked:
            continue

        # Try to match existing employee by email or name
        matched = None
        if email:
            matched = next((e for e in all_employees if e.email and e.email.lower() == email.lower()), None)
        if not matched and display_name:
            first_name = display_name.strip().split()[0].lower()
            matched = next(
                (e for e in all_employees if e.name and e.name.strip().split()[0].lower() == first_name),
                None,
            )

        if matched:
            # Link existing employee to Jira
            matched.jira_account_id = account_id
            db.add(matched)
            linked += 1
        else:
            # Create new employee from Jira user
            new_emp = Employee(
                name=display_name,
                email=email or f"{display_name.lower().replace(' ', '.')}@jira.user",
                skills=[],
                department="From Jira",
                availability_status="available",
                jira_account_id=account_id,
            )
            db.add(new_emp)
            created += 1

    await db.commit()

    return {
        "status": "success",
        "total_jira_users": len(jira_users),
        "created": created,
        "linked": linked,
    }
