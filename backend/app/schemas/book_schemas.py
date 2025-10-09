from pydantic import BaseModel
from typing import List, Optional

# These schemas prevent accidentally exposing private data
# and ensure a consistent API response structure.

class CategoryPublic(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class BookCopyPublic(BaseModel):
    id: int
    status: str

    class Config:
        from_attributes = True

class BookPublic(BaseModel):
    id: int
    title: str
    author: str
    publication_year: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    categories: List[CategoryPublic] = []
    copies: List[BookCopyPublic] = []

    class Config:
        from_attributes = True