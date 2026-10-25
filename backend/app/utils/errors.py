"""Custom application exceptions."""


class AppError(Exception):
    """Base application error."""

    status_code = 500

    def __init__(self, message: str = "Internal server error"):
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    status_code = 404

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)


class ValidationError(AppError):
    status_code = 422

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message)


class AuthError(AppError):
    status_code = 401

    def __init__(self, message: str = "Not authenticated"):
        super().__init__(message)


class ConflictError(AppError):
    status_code = 409

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message)


class AIGenerationError(AppError):
    status_code = 502

    def __init__(self, message: str = "AI generation failed"):
        super().__init__(message)
