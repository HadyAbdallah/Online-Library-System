from pydantic import BaseModel, Field
from typing import Optional, List

class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    publication_year: Optional[int] = None
    description: Optional[str] = None
    category_ids: List[int] = []

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    publication_year: Optional[int] = None
    description: Optional[str] = None
    category_ids: Optional[List[int]] = None
