from pydantic import BaseModel
from typing import Optional

class CategoryPublic(BaseModel):
    id: int
    name: str
    description: Optional[str] = None 

    class Config:
        from_attributes = True

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None 

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None