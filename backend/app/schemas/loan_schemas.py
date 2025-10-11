from pydantic import BaseModel, Field
from typing import Optional
import datetime

class LoanCreate(BaseModel):
    book_id: int 
    loan_days: int = Field(14, gt=0, le=14)

class LoanPublic(BaseModel):
    id: int
    loan_date: datetime.datetime
    due_date: datetime.datetime
    book_copy_id: int

    class Config:
        from_attributes = True


# A simplified book schema for displaying in the loan list
class BookInLoan(BaseModel):
    id: int
    title: str
    author: str

    class Config:
        from_attributes = True

# A simplified book copy schema
class BookCopyInLoan(BaseModel):
    id: int
    book: BookInLoan

    class Config:
        from_attributes = True

# The main schema for the "my-loans" endpoint
class LoanDetailsPublic(BaseModel):
    id: int
    loan_date: datetime.datetime
    due_date: datetime.datetime
    return_date: Optional[datetime.datetime] = None
    book_copy: BookCopyInLoan

    class Config:
        from_attributes = True