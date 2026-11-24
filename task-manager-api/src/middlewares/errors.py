class AppError(Exception):
    status = 400

    def __init__(self, message, status=None):
        super().__init__(message)
        self.message = message
        if status is not None:
            self.status = status


class NotFoundError(AppError):
    status = 404


class ConflictError(AppError):
    status = 409


class UnauthorizedError(AppError):
    status = 401


class ForbiddenError(AppError):
    status = 403
