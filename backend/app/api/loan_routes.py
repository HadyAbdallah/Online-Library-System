"""
Defines the API endpoints for authenticated users to manage their book loans.
"""
from flask import Blueprint, request, jsonify, g
from app.core.security import jwt_required
from app.services import loan_service
from app.schemas.loan_schemas import LoanCreate, LoanPublic, LoanDetailsPublic

loan_bp = Blueprint('loans', __name__, url_prefix='/api/loans')

@loan_bp.route('/', methods=['POST'])
@jwt_required
def borrow_book():
    """Handles a user's request to borrow an available book."""
    # The `g.user` object is attached by the @jwt_required decorator.
    current_user = g.user
    loan_data = LoanCreate(**request.json)
    new_loan = loan_service.create_loan(user=current_user, loan_data=loan_data)
    return jsonify(LoanPublic.model_validate(new_loan).model_dump()), 201

@loan_bp.route('/my-loans', methods=['GET'])
@jwt_required
def get_my_loans():
    """Retrieves the borrowing history for the current user."""
    current_user = g.user
    loans = loan_service.get_user_loans(user_id=current_user.id)
    loans_data = [LoanDetailsPublic.model_validate(loan).model_dump() for loan in loans]
    return jsonify(loans_data)