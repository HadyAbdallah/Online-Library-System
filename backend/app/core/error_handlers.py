# app/core/error_handlers.py
from flask import jsonify, current_app
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import NotFound, MethodNotAllowed

from .exceptions import (
    ConcurrencyException, BookNotAvailableException, AuthException, 
    MissingTokenException, InvalidTokenException, ExpiredTokenException, 
    AdminAccessRequiredException
)

def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        # Pydantic validation errors
        response = {
            "error": "Validation Error",
            "messages": error.errors()
        }
        return jsonify(response), 422 # 422 Unprocessable Entity

    @app.errorhandler(ConcurrencyException)
    def handle_concurrency_error(error):
        response = {"error": str(error)}
        return jsonify(response), 409 # 409 Conflict

    @app.errorhandler(BookNotAvailableException)
    def handle_book_not_available(error):
        response = {"error": str(error)}
        return jsonify(response), 404 # 404 Not Found

    @app.errorhandler(MissingTokenException)
    @app.errorhandler(InvalidTokenException)
    @app.errorhandler(ExpiredTokenException)
    def handle_token_errors(error):
        # Handles all 401 Unauthorized errors
        return jsonify({"error": str(error)}), 401

    @app.errorhandler(AdminAccessRequiredException)
    def handle_admin_required_error(error):
        # Handles 403 Forbidden errors
        return jsonify({"error": str(error)}), 403

    @app.errorhandler(ValueError)
    def handle_value_error(error):
        # Catches our custom ValueError for duplicate ISBNs
        response = {"error": str(error)}
        return jsonify(response), 409 # 409 Conflict

    @app.errorhandler(NotFound)
    @app.errorhandler(404)
    def handle_not_found_error(error):
        response = {"error": "The requested resource was not found."}
        return jsonify(response), 404

    @app.errorhandler(MethodNotAllowed)
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        response = {"error": "The method is not allowed for the requested URL."}
        return jsonify(response), 405

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        # This is the catch-all for any other unexpected error.
        # It's important to log the real error for debugging.
        current_app.logger.error(f"An unexpected error occurred: {error}", exc_info=True)
        
        # But return a generic message to the user for security.
        response = {"error": "An internal server error occurred."}
        return jsonify(response), 500