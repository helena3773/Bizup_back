from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    
    # 사업주 정보
    employer_name = Column(String, nullable=False)
    working_conditions = Column(String, nullable=True)
    wage = Column(String, nullable=True)
    contract_date = Column(Date, nullable=False)
    
    # 근로자 정보
    employee_name = Column(String, nullable=False)
    employee_address = Column(String, nullable=False)
    employee_phone = Column(String, nullable=False)
    employee_signature = Column(Text, nullable=False)  # base64 이미지 데이터
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 관계 설정
    employee = relationship("Employee", backref="contracts")

