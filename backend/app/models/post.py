from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    author = Column(String(100))
    likes = Column(BigInteger, default=0)
    collects = Column(BigInteger, default=0)
    comments = Column(BigInteger, default=0)
    shares = Column(BigInteger, default=0)
    url = Column(String(500))
    published_at = Column(DateTime(timezone=True))
    crawled_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    keyword = relationship("Keyword", backref="posts")