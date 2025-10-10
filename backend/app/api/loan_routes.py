from flask import Blueprint, request, jsonify, g
from pydantic import ValidationError

from app.core.security import jwt_required
from app.services import loan_service
from app.schemas.loan_schemas import LoanCreate, LoanPublic
from app.core.exceptions import ConcurrencyException, BookNotAvailableException

loan_bp = Blueprint('loans', __name__, url_prefix='/api/loans')

@loan_bp.route('/', methods=['POST'])
@jwt_required
def borrow_book():
    # The `g.user` object is attached by the @jwt_required decorator
    current_user = g.user

    try:
        loan_data = LoanCreate(**request.json)
        new_loan = loan_service.create_loan(user=current_user, book_copy_id=loan_data.book_copy_id)
        return jsonify(LoanPublic.model_validate(new_loan).model_dump()), 201

    except ValidationError as e:
        return jsonify(e.errors()), 400
    except BookNotAvailableException as e:
        return jsonify({"error": str(e)}), 404
    except ConcurrencyException as e:
        # 409 Conflict is the appropriate status code for a race condition
        return jsonify({"error": str(e)}), 409