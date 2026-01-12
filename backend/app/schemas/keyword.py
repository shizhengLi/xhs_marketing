from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class KeywordBase(BaseModel):
    keyword: str = Field(..., min_length=1, max_length=100, description="关键词")
    group_name: str = Field(default="default", max_length=50, description="分组名称")
    is_active: bool = Field(default=True, description="是否启用")


class KeywordCreate(KeywordBase):
    pass


class KeywordUpdate(BaseModel):
    keyword: Optional[str] = Field(None, min_length=1, max_length=100)
    group_name: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class KeywordResponse(KeywordBase):
    id: int
    user_id: int
    is_ai_expanded: bool
    created_at: datetime

    class Config:
        from_attributes = True


class KeywordAIExpand(BaseModel):
    base_keyword: str = Field(..., min_length=1, max_length=100, description="基础关键词")
    count: int = Field(default=5, ge=1, le=20, description="生成的关键词数量")


class KeywordAIResponse(BaseModel):
    original: str
    suggested_keywords: list[str]