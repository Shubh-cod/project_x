"""Custom HTTP exceptions and exception handlers."""
from typing import Any, Dict

from fastapi import Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse


class NovaCRMException(HTTPException):
    """Base exception for NovaCRM API."""

    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = "An error occurred",
        success: bool = False,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.success = success


class NotFoundError(NovaCRMException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedError(NovaCRMException):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenError(NovaCRMException):
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ConflictError(NovaCRMException):
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


def exception_response(request: Request, exc: Exception) -> JSONResponse:
    """Format all exceptions as consistent JSON with data/message/success."""
    if isinstance(exc, NovaCRMException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "data": None,
                "message": exc.detail,
                "success": False,
            },
        )
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "data": None,
                "message": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
                "success": False,
            },
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "data": None,
            "message": "Internal server error",
            "success": False,
        },
    )
