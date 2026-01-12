from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    keyword = Column(String(100), nullable=False)
    group_name = Column(String(50), default="default")
    is_active = Column(Boolean, default=True)
    is_ai_expanded = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User", backref="keywords")