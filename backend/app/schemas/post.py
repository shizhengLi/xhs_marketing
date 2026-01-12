from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PostBase(BaseModel):
    title: str
    content: str
    author: str
    likes: int
    collects: int
    comments: int
    shares: int
    url: str


class PostCreate(PostBase):
    keyword_id: int


class PostResponse(PostBase):
    id: int
    keyword_id: int
    published_at: Optional[datetime] = None
    crawled_at: datetime

    class Config:
        from_attributes = True


class CrawlRequest(BaseModel):
    keyword_id: int
    count: int = 20


class CrawlResponse(BaseModel):
    success: bool
    message: str
    total_crawled: int
    new_saved: int
    updated: int