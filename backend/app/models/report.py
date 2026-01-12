from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    summary = Column(String(500))
    report_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User", backref="reports")
    keyword = relationship("Keyword", backref="reports")