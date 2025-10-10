from pydantic import BaseModel
import datetime

class LoanCreate(BaseModel):
    book_copy_id: int

class LoanPublic(BaseModel):
    id: int
    loan_date: datetime.datetime
    due_date: datetime.datetime
    book_copy_id: int

    class Config:
        from_attributes = True