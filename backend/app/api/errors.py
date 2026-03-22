from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.schemas import ErrorResponse


def _error_body(code: str, message: str, details: dict[str, object] | None = None) -> dict[str, object]:
    return ErrorResponse(
        error={"code": code, "message": message, "details": details or {}},
    ).model_dump(mode="json")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_body(
                "validation_error",
                "request validation failed",
                {"errors": exc.errors()},
            ),
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(_: Request, exc: HTTPException) -> JSONResponse:
        code = {
            401: "unauthorized",
            403: "forbidden",
            404: "not_found",
            409: "conflict",
        }.get(exc.status_code, "http_error")
        details = exc.detail if isinstance(exc.detail, dict) else {"detail": exc.detail}
        message = exc.detail if isinstance(exc.detail, str) else code.replace("_", " ")
        return JSONResponse(status_code=exc.status_code, content=_error_body(code, message, details))

    @app.exception_handler(LookupError)
    async def handle_lookup_error(_: Request, exc: LookupError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=_error_body("not_found", str(exc)),
        )

    @app.exception_handler(PermissionError)
    async def handle_permission_error(_: Request, exc: PermissionError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=_error_body("forbidden", str(exc)),
        )

    @app.exception_handler(ValueError)
    async def handle_value_error(_: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=_error_body("bad_request", str(exc)),
        )

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(_: Request, exc: IntegrityError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=_error_body("conflict", "resource conflict", {"detail": str(exc.orig)}),
        )