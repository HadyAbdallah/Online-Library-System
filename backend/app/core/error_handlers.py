"""
Registers global error handlers for the Flask application to ensure
consistent JSON error responses across the API.
"""
from flask import jsonify, current_app
from pydantic import ValidationError
from werkzeug.exceptions import NotFound, MethodNotAllowed
from .exceptions import (
    ConcurrencyException, BookNotAvailableException,
    MissingTokenException, InvalidTokenException, ExpiredTokenException,
    AdminAccessRequiredException
)

def register_error_handlers(app):
    """Attaches all custom error handlers to the Flask app instance."""
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        # Handles Pydantic model validation errors (422 Unprocessable Entity).
        response = {
            "error": "Validation Error",
            "messages": error.errors()
        }
        return jsonify(response), 422

    @app.errorhandler(ConcurrencyException)
    def handle_concurrency_error(error):
        # Handles database race conditions (409 Conflict).
        return jsonify({"error": str(error)}), 409

    @app.errorhandler(BookNotAvailableException)
    def handle_book_not_available(error):
        return jsonify({"error": str(error)}), 404

    @app.errorhandler(MissingTokenException)
    @app.errorhandler(InvalidTokenException)
    @app.errorhandler(ExpiredTokenException)
    def handle_token_errors(error):
        # Handles all authentication token errors (401 Unauthorized).
        return jsonify({"error": str(error)}), 401

    @app.errorhandler(AdminAccessRequiredException)
    def handle_admin_required_error(error):
        # Handles authorization errors for admin routes (403 Forbidden).
        return jsonify({"error": str(error)}), 403

    @app.errorhandler(ValueError)
    def handle_value_error(error):
        # Catches custom ValueErrors, e.g., for duplicate items (409 Conflict).
        return jsonify({"error": str(error)}), 409

    @app.errorhandler(NotFound)
    @app.errorhandler(404)
    def handle_not_found_error(error):
        return jsonify({"error": "The requested resource was not found."}), 404

    @app.errorhandler(MethodNotAllowed)
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({"error": "The method is not allowed for the requested URL."}), 405

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        # This is a catch-all for any other unexpected error (500 Internal Server Error).
        # Log the real error for debugging purposes.
        current_app.logger.error(f"An unexpected error occurred: {error}", exc_info=True)
        # Return a generic message to the user for security.
        return jsonify({"error": "An internal server error occurred."}), 500