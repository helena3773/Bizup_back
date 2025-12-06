from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.contract import ContractCreate, ContractUpdate, ContractResponse
from app.models.contract import Contract
from app.models.employee import Employee

router = APIRouter(prefix="/contracts", tags=["근로계약서"])


@router.get("/", response_model=List[ContractResponse])
def get_contracts(db: Session = Depends(get_db)):
    """모든 근로계약서 조회"""
    return db.query(Contract).all()


@router.get("/employee/{employee_id}", response_model=List[ContractResponse])
def get_contracts_by_employee(employee_id: int, db: Session = Depends(get_db)):
    """특정 직원의 근로계약서 조회"""
    contracts = db.query(Contract).filter(Contract.employee_id == employee_id).all()
    return contracts


@router.get("/{contract_id}", response_model=ContractResponse)
def get_contract(contract_id: int, db: Session = Depends(get_db)):
    """근로계약서 상세 조회"""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="근로계약서를 찾을 수 없습니다")
    return contract


@router.post("/", response_model=ContractResponse, status_code=201)
def create_contract(contract: ContractCreate, db: Session = Depends(get_db)):
    """근로계약서 생성"""
    import logging
    logger = logging.getLogger(__name__)
    
    # 디버깅: 받은 데이터 확인
    logger.info(f"받은 계약서 데이터 - employee_id: {contract.employee_id}")
    logger.info(f"받은 서명 데이터 길이: {len(contract.employee_signature) if contract.employee_signature else 0}")
    logger.info(f"받은 서명 데이터 시작: {contract.employee_signature[:50] if contract.employee_signature else 'None'}...")
    
    # 직원 존재 확인
    employee = db.query(Employee).filter(Employee.id == contract.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="직원을 찾을 수 없습니다")
    
    # 서명 데이터 검증
    if not contract.employee_signature or len(contract.employee_signature) < 100:
        logger.error(f"서명 데이터가 유효하지 않습니다. 길이: {len(contract.employee_signature) if contract.employee_signature else 0}")
        raise HTTPException(status_code=400, detail="근로자 서명이 유효하지 않습니다")
    
    db_contract = Contract(
        employee_id=contract.employee_id,
        employer_name=contract.employer_name,
        working_conditions=contract.working_conditions,
        wage=contract.wage,
        contract_date=contract.contract_date,
        employee_name=contract.employee_name,
        employee_address=contract.employee_address,
        employee_phone=contract.employee_phone,
        employee_signature=contract.employee_signature,
    )
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    
    logger.info(f"계약서 생성 완료 - ID: {db_contract.id}, 서명 길이: {len(db_contract.employee_signature)}")
    
    return db_contract


@router.put("/{contract_id}", response_model=ContractResponse)
def update_contract(
    contract_id: int,
    contract: ContractUpdate,
    db: Session = Depends(get_db)
):
    """근로계약서 수정"""
    db_contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not db_contract:
        raise HTTPException(status_code=404, detail="근로계약서를 찾을 수 없습니다")
    
    update_data = contract.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_contract, field, value)
    
    db.commit()
    db.refresh(db_contract)
    return db_contract


@router.delete("/{contract_id}", status_code=204)
def delete_contract(contract_id: int, db: Session = Depends(get_db)):
    """근로계약서 삭제"""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="근로계약서를 찾을 수 없습니다")
    
    db.delete(contract)
    db.commit()
    return None

