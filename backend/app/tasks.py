import time
from app.celery_app import celery_app

@celery_app.task
def send_loan_confirmation_email(loan_id: int):
    
    # A mock task that simulates sending an email.
    # In a real app, this would contain email sending logic.
    
    print(f"Starting task to send confirmation for loan ID: {loan_id}")
    time.sleep(5) # Simulate a slow network operation
    print(f"Email sent successfully for loan ID: {loan_id}")
    return f"Email sent for loan {loan_id}"